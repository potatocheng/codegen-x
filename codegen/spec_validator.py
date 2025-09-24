import ast
import json
import re
from dataclasses import dataclass
from typing import List, Set, Tuple

from codegen.spec import Spec, Predicate, MetamorphicRelation, Example

# -----------------------------
# Exceptions
# -----------------------------
class SpecValidationError(Exception):
    pass

@dataclass
class ValidationIssue:
    code: str
    location: str
    message: str
    severity: str = "ERROR"  # or WARNING

    def format(self) -> str:
        return f"{self.severity}:{self.code}::{self.location}::{self.message}"

# -----------------------------
# Validator
# -----------------------------
class SpecValidator:
    SAFE_CALL_WHITELIST = {"len", "abs", "min", "max", "sum", "all", "any"}
    FORBIDDEN_IDENTIFIERS = {"__import__", "eval", "exec", "open"}
    FORBIDDEN_API_INTERNAL = {"__import__", "eval", "exec"}
    COMPLEXITY_RULES_ALLOWED = {"no_sort", "no_quadratic_nested_loops", "no_hash_map", "no_recursion"}
    META_RELATIONS_ALLOWED = {"equal", "subset", "permutation", "length_non_decreasing", "custom"}

    @classmethod
    def validate(cls, spec: Spec) -> Tuple[List[ValidationIssue], List[ValidationIssue]]:
        errors: List[ValidationIssue] = []
        warnings: List[ValidationIssue] = []

        if spec.spec_version != 2:
            errors.append(cls._err("STRUCTURE_ERROR", "spec_version", "spec_version must be 2"))

        if not spec.main_function or not spec.main_function.name:
            errors.append(cls._err("STRUCTURE_ERROR", "main_function.name", "Main function name missing"))

        # Basic signature checks
        if spec.main_function and not spec.main_function.signature.return_type:
            errors.append(cls._err("STRUCTURE_ERROR", "main_function.signature.return_type", "Return type missing"))

        # ID uniqueness
        cls._check_id_uniqueness(spec.pre + spec.post + spec.invariants, errors, context="predicates")
        cls._check_example_ids(spec, errors)
        cls._check_meta_ids(spec, errors)

        param_names = {p.name for p in spec.types.parameters}

        # Predicates
        for group_name, preds in [("pre", spec.pre), ("post", spec.post), ("invariants", spec.invariants)]:
            for p in preds:
                cls._validate_predicate_expr(p, param_names, errors, warnings, group_name)

        # Exceptions predicates (types.exceptions)
        for idx, exc in enumerate(spec.types.exceptions):
            if exc.predicate:
                cls._validate_expr(exc.predicate, param_names, f"types.exceptions[{idx}].predicate", errors, warnings)
            if not exc.type:
                errors.append(cls._err("STRUCTURE_ERROR", f"types.exceptions[{idx}].type", "Exception type empty"))

        # Examples
        cls._validate_examples(spec, param_names, errors, warnings)

        # Metamorphic relations
        for i, m in enumerate(spec.metamorphic_relations):
            cls._validate_metamorphic(spec, m, i, param_names, errors, warnings)

        # Forbidden APIs
        for i, api in enumerate(spec.forbidden_apis):
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$", api):
                errors.append(cls._err("FORBIDDEN_API_FORMAT", f"forbidden_apis[{i}]", f"Invalid api token '{api}'"))
            if api in cls.FORBIDDEN_API_INTERNAL:
                errors.append(cls._err("FORBIDDEN_API_FORMAT", f"forbidden_apis[{i}]", f"Internal unsafe api '{api}' not allowed"))

        # Complexity
        if spec.complexity_guarantee:
            if not re.match(r"^O\([^()]+\)$", spec.complexity_guarantee.big_o.strip()):
                errors.append(cls._err("COMPLEXITY_INVALID", "complexity_guarantee.big_o", "big_o must look like O(n)"))
            for r in spec.complexity_guarantee.witness_rules:
                if r not in cls.COMPLEXITY_RULES_ALLOWED:
                    warnings.append(cls._warn("COMPLEXITY_INVALID", "complexity_guarantee.witness_rules", f"Unknown rule '{r}'"))

        # Coverage minimal
        if len(spec.pre) == 0:
            errors.append(cls._err("COVERAGE_INSUFFICIENT", "pre", "At least one pre predicate required"))
        if len(spec.post) == 0:
            errors.append(cls._err("COVERAGE_INSUFFICIENT", "post", "At least one post predicate required"))
        if len(spec.examples.positive) == 0:
            warnings.append(cls._warn("COVERAGE_INSUFFICIENT", "examples.positive", "No positive examples provided"))
        if len(spec.examples.negative) == 0:
            warnings.append(cls._warn("COVERAGE_INSUFFICIENT", "examples.negative", "No negative examples provided"))

        if errors:
            # raise with aggregated message
            raise SpecValidationError("\n".join([e.format() for e in errors]))
        return errors, warnings

    # ------------------------- Helpers -------------------------
    @staticmethod
    def _err(code: str, loc: str, msg: str) -> ValidationIssue:
        return ValidationIssue(code=code, location=loc, message=msg, severity="ERROR")

    @staticmethod
    def _warn(code: str, loc: str, msg: str) -> ValidationIssue:
        return ValidationIssue(code=code, location=loc, message=msg, severity="WARNING")

    @classmethod
    def _check_id_uniqueness(cls, preds: List[Predicate], errors: List[ValidationIssue], context: str):
        seen = set()
        for p in preds:
            if not p.id:
                errors.append(cls._err("ID_CONFLICT", context, "Predicate id empty"))
            elif p.id in seen:
                errors.append(cls._err("ID_CONFLICT", f"{context}.{p.id}", "Duplicate predicate id"))
            else:
                seen.add(p.id)

    @classmethod
    def _check_example_ids(cls, spec: Spec, errors: List[ValidationIssue]):
        seen = set()
        for group_name, arr in [("positive", spec.examples.positive), ("negative", spec.examples.negative)]:
            for ex in arr:
                if not ex.id:
                    errors.append(cls._err("ID_CONFLICT", f"examples.{group_name}", "Example id empty"))
                elif ex.id in seen:
                    errors.append(cls._err("ID_CONFLICT", f"examples.{group_name}.{ex.id}", "Duplicate example id"))
                else:
                    seen.add(ex.id)

    @classmethod
    def _check_meta_ids(cls, spec: Spec, errors: List[ValidationIssue]):
        seen = set()
        for m in spec.metamorphic_relations:
            if not m.id:
                errors.append(cls._err("ID_CONFLICT", "metamorphic_relations", "Relation id empty"))
            elif m.id in seen:
                errors.append(cls._err("ID_CONFLICT", f"metamorphic_relations.{m.id}", "Duplicate relation id"))
            else:
                seen.add(m.id)

    @classmethod
    def _validate_predicate_expr(cls, predicate: Predicate, params: Set[str], errors: List[ValidationIssue], warnings: List[ValidationIssue], group: str):
        if not predicate.expr:
            errors.append(cls._err("PRED_EXPR_INVALID", f"{group}.{predicate.id}", "Empty expression"))
            return
        cls._validate_expr(predicate.expr, params, f"{group}.{predicate.id}.expr", errors, warnings)

    @classmethod
    def _validate_expr(cls, expr: str, params: Set[str], location: str, errors: List[ValidationIssue], warnings: List[ValidationIssue]):
        # security quick scan
        if any(tok in expr for tok in [";", "__import__", "import ", "exec(", "eval("]):
            errors.append(cls._err("PRED_UNSAFE_NODE", location, "Contains forbidden token"))
            return
        try:
            node = ast.parse(expr, mode='eval')
        except Exception as e:
            errors.append(cls._err("PRED_EXPR_INVALID", location, f"Parse error: {e}"))
            return
        # walk
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                fname = cls._extract_call_name(n)
                if fname not in cls.SAFE_CALL_WHITELIST:
                    errors.append(cls._err("PRED_UNSAFE_NODE", location, f"Call not allowed: {fname}"))
            elif isinstance(n, (ast.Import, ast.ImportFrom, ast.Lambda, ast.With, ast.Try, ast.FunctionDef, ast.ClassDef)):
                errors.append(cls._err("PRED_UNSAFE_NODE", location, f"Forbidden syntax: {type(n).__name__}"))
            elif isinstance(n, ast.Name):
                if n.id not in params and n.id not in {"result", "original_result", "new_result"} and not isinstance(n.ctx, ast.Store):
                    warnings.append(cls._warn("PRED_NAME_UNKNOWN", location, f"Name '{n.id}' not in params"))
        # trivial literal
        if isinstance(node.body, ast.Constant):
            warnings.append(cls._warn("PRED_TRIVIAL", location, "Predicate is a constant"))

    @staticmethod
    def _extract_call_name(call: ast.Call) -> str:
        if isinstance(call.func, ast.Name):
            return call.func.id
        if isinstance(call.func, ast.Attribute):
            return call.func.attr
        return "<unknown>"

    @classmethod
    def _validate_examples(cls, spec: Spec, params: Set[str], errors: List[ValidationIssue], warnings: List[ValidationIssue]):
        for group, arr in [("positive", spec.examples.positive), ("negative", spec.examples.negative)]:
            for ex in arr:
                loc = f"examples.{group}.{ex.id or '<?>'}"
                # inputs keys subset of params
                missing = params - set(ex.inputs.keys())
                if group == "positive" and missing:
                    warnings.append(cls._warn("EXAMPLE_INPUT_MISSING", loc, f"Missing params: {','.join(sorted(missing))}"))
                # negative must have raises
                if group == "negative":
                    if not ex.raises:
                        errors.append(cls._err("EXAMPLE_INVALID", loc, "Negative example must have 'raises'"))
                    if ex.output is not None:
                        errors.append(cls._err("EXAMPLE_INVALID", loc, "Negative example should not define output"))
                else:
                    if ex.raises:
                        errors.append(cls._err("EXAMPLE_INVALID", loc, "Positive example must not set 'raises'"))
                # JSON serializable check
                try:
                    json.dumps(ex.inputs)
                except Exception:
                    errors.append(cls._err("EXAMPLE_INVALID", loc, "inputs not JSON serializable"))

    @classmethod
    def _validate_metamorphic(cls, spec: Spec, m: MetamorphicRelation, idx: int, params: Set[str], errors: List[ValidationIssue], warnings: List[ValidationIssue]):
        loc = f"metamorphic_relations[{idx}].{m.id or '?'}"
        if m.relation not in cls.META_RELATIONS_ALLOWED:
            errors.append(cls._err("META_RELATION_INVALID", loc, f"Unknown relation '{m.relation}'"))
        if not m.transform_inputs:
            errors.append(cls._err("META_RELATION_INVALID", loc, "transform_inputs empty"))
        if m.relation == "custom" and not m.oracle_expr:
            errors.append(cls._err("META_RELATION_INVALID", loc, "custom relation requires oracle_expr"))
        if m.oracle_expr:
            cls._validate_expr(m.oracle_expr, params | {"original_result", "new_result"}, f"{loc}.oracle_expr", errors, warnings)

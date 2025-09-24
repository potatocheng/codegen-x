from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json

# -----------------------------
# Core Spec Data Structures
# -----------------------------

@dataclass
class TypeDescriptor:
    name: str
    type: str
    description: str = ""
    nullable: bool = False
    union: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TypeDescriptor":
        return cls(
            name=data.get("name", ""),
            type=data.get("type", ""),
            description=data.get("description", ""),
            nullable=data.get("nullable", False),
            union=data.get("union", []) or []
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "nullable": self.nullable,
            "union": self.union,
        }

@dataclass
class ExceptionSpec:
    type: str
    predicate: str  # condition expression for raising
    message: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExceptionSpec":
        return cls(
            type=data.get("type", ""),
            predicate=data.get("predicate", data.get("condition", "")),
            message=data.get("message", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "predicate": self.predicate,
            "message": self.message,
        }

@dataclass
class Predicate:
    id: str
    expr: str
    message: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Predicate":
        return cls(
            id=data.get("id", ""),
            expr=data.get("expr", ""),
            message=data.get("message", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "expr": self.expr, "message": self.message}

@dataclass
class Example:
    id: str
    inputs: Dict[str, Any]
    output: Any = None
    raises: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Example":
        return cls(
            id=data.get("id", ""),
            inputs=data.get("inputs", {}),
            output=data.get("output"),
            raises=data.get("raises"),
            tags=data.get("tags", []) or [],
            notes=data.get("notes", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "inputs": self.inputs,
            "output": self.output,
            "raises": self.raises,
            "tags": self.tags,
            "notes": self.notes,
        }

@dataclass
class MetamorphicRelation:
    id: str
    transform_inputs: str  # e.g. "lambda args: {...}"
    relation: str          # equal|subset|permutation|length_non_decreasing|custom
    oracle_expr: str       # expression comparing original & transformed results
    notes: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetamorphicRelation":
        return cls(
            id=data.get("id", ""),
            transform_inputs=data.get("transform_inputs", ""),
            relation=data.get("relation", ""),
            oracle_expr=data.get("oracle_expr", ""),
            notes=data.get("notes", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "transform_inputs": self.transform_inputs,
            "relation": self.relation,
            "oracle_expr": self.oracle_expr,
            "notes": self.notes,
        }

@dataclass
class ComplexityGuarantee:
    big_o: str
    witness_rules: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplexityGuarantee":
        return cls(
            big_o=data.get("big_o", data.get("complexity", "")),
            witness_rules=data.get("witness_rules", []) or []
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"big_o": self.big_o, "witness_rules": self.witness_rules}

@dataclass
class OracleSpec:
    type: str  # reference_impl | assertion_bundle | inline
    ref: Optional[str] = None
    code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OracleSpec":
        return cls(
            type=data.get("type", ""),
            ref=data.get("ref"),
            code=data.get("code")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "ref": self.ref, "code": self.code}

@dataclass
class TypesModel:
    parameters: List[TypeDescriptor] = field(default_factory=list)
    returns: Optional[TypeDescriptor] = None
    exceptions: List[ExceptionSpec] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TypesModel":
        return cls(
            parameters=[TypeDescriptor.from_dict(p) for p in data.get("parameters", [])],
            returns=TypeDescriptor.from_dict(data.get("returns", {})) if data.get("returns") else None,
            exceptions=[ExceptionSpec.from_dict(e) for e in data.get("exceptions", [])]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns.to_dict() if self.returns else None,
            "exceptions": [e.to_dict() for e in self.exceptions],
        }

@dataclass
class ExamplesBundle:
    positive: List[Example] = field(default_factory=list)
    negative: List[Example] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExamplesBundle":
        return cls(
            positive=[Example.from_dict(e) for e in data.get("positive", [])],
            negative=[Example.from_dict(e) for e in data.get("negative", [])]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "positive": [e.to_dict() for e in self.positive],
            "negative": [e.to_dict() for e in self.negative],
        }

# Minimal duplicates for backward compatibility mapping
@dataclass
class LegacyParameter:
    name: str
    type: str
    description: str = ""
    constraints: str = ""

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "constraints": self.constraints,
        }

@dataclass
class LegacySignature:
    parameters: List[LegacyParameter]
    return_type: str
    return_description: str

    def to_dict(self):
        return {
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type,
            "return_description": self.return_description,
        }

@dataclass
class LegacyException:
    type: str
    condition: str

    def to_dict(self):
        return {"type": self.type, "condition": self.condition}

@dataclass
class LegacyHelperFunction:
    name: str
    purpose: str
    signature: LegacySignature
    exceptions: List[LegacyException]

    def to_dict(self):
        return {
            "name": self.name,
            "purpose": self.purpose,
            "signature": self.signature.to_dict(),
            "exceptions": [e.to_dict() for e in self.exceptions],
        }

@dataclass
class LegacyMainFunction:
    name: str
    purpose: str
    signature: LegacySignature
    exceptions: List[LegacyException]
    complexity: str = ""

    def to_dict(self):
        return {
            "name": self.name,
            "purpose": self.purpose,
            "signature": self.signature.to_dict(),
            "exceptions": [e.to_dict() for e in self.exceptions],
            "complexity": self.complexity,
        }

# -----------------------------
# Spec Root
# -----------------------------
@dataclass
class Spec:
    main_function: Optional[LegacyMainFunction]
    helper_functions: List[LegacyHelperFunction]
    types: TypesModel
    pre: List[Predicate]
    post: List[Predicate]
    invariants: List[Predicate]
    examples: ExamplesBundle
    metamorphic_relations: List[MetamorphicRelation]
    forbidden_apis: List[str]
    complexity_guarantee: Optional[ComplexityGuarantee]
    oracle: Optional[OracleSpec]
    design_notes: str = ""
    spec_version: int = 2

    @classmethod
    def from_json(cls, raw: str) -> "Spec":
        data = json.loads(raw)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Spec":
        # Backward compatible if only contract fields exist
        types_section = TypesModel.from_dict(data.get("types", {}))
        # Derive legacy main function if provided in new structure or fallback
        legacy_main = None
        if data.get("main_function"):
            mf = data["main_function"]
            sig = mf.get("signature", {})
            legacy_main = LegacyMainFunction(
                name=mf.get("name", ""),
                purpose=mf.get("purpose", ""),
                signature=LegacySignature(
                    parameters=[LegacyParameter(**p) for p in sig.get("parameters", [])],
                    return_type=sig.get("return_type", sig.get("returns", "Any")),
                    return_description=sig.get("return_description", "")
                ),
                exceptions=[LegacyException(type=e.get("type", ""), condition=e.get("condition", e.get("predicate", ""))) for e in mf.get("exceptions", [])],
                complexity=mf.get("complexity", "")
            )
        helper_functions = []
        for h in data.get("helper_functions", []):
            sig = h.get("signature", {})
            helper_functions.append(
                LegacyHelperFunction(
                    name=h.get("name", ""),
                    purpose=h.get("purpose", ""),
                    signature=LegacySignature(
                        parameters=[LegacyParameter(**p) for p in sig.get("parameters", [])],
                        return_type=sig.get("return_type", sig.get("returns", "Any")),
                        return_description=sig.get("return_description", "")
                    ),
                    exceptions=[LegacyException(type=e.get("type", ""), condition=e.get("condition", e.get("predicate", ""))) for e in h.get("exceptions", [])]
                )
            )
        return cls(
            main_function=legacy_main,
            helper_functions=helper_functions,
            types=types_section,
            pre=[Predicate.from_dict(p) for p in data.get("pre", [])],
            post=[Predicate.from_dict(p) for p in data.get("post", [])],
            invariants=[Predicate.from_dict(p) for p in data.get("invariants", [])],
            examples=ExamplesBundle.from_dict(data.get("examples", {})),
            metamorphic_relations=[MetamorphicRelation.from_dict(m) for m in data.get("metamorphic_relations", [])],
            forbidden_apis=data.get("forbidden_apis", []) or [],
            complexity_guarantee=ComplexityGuarantee.from_dict(data.get("complexity_guarantee", {})) if data.get("complexity_guarantee") else None,
            oracle=OracleSpec.from_dict(data.get("oracle", {})) if data.get("oracle") else None,
            design_notes=data.get("design_notes", data.get("notes", "")),
            spec_version=data.get("spec_version", 2)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec_version": self.spec_version,
            "main_function": self.main_function.to_dict() if self.main_function else None,
            "helper_functions": [h.to_dict() for h in self.helper_functions],
            "types": self.types.to_dict(),
            "pre": [p.to_dict() for p in self.pre],
            "post": [p.to_dict() for p in self.post],
            "invariants": [p.to_dict() for p in self.invariants],
            "examples": self.examples.to_dict(),
            "metamorphic_relations": [m.to_dict() for m in self.metamorphic_relations],
            "forbidden_apis": self.forbidden_apis,
            "complexity_guarantee": self.complexity_guarantee.to_dict() if self.complexity_guarantee else None,
            "oracle": self.oracle.to_dict() if self.oracle else None,
            "design_notes": self.design_notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    # Adapter helpers to mimic legacy contract API
    @property
    def name(self) -> str:
        return self.main_function.name if self.main_function else ""

    @property
    def purpose(self) -> str:
        return self.main_function.purpose if self.main_function else ""

    @property
    def legacy_parameters(self) -> List[LegacyParameter]:
        return self.main_function.signature.parameters if self.main_function else []

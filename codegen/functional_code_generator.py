from config.config import get_prompts
from llm.factory import create_llm
from llm.message import Message

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from codegen.spec import Spec
from codegen.spec_validator import SpecValidator, SpecValidationError
from codegen.schema_loader import load_schema, validate_json_against_schema
from codegen.step_graph import StepGraph, StepGraphValidator, StepGraphValidationError

@dataclass
class Parameter:
    """参数定义"""
    name: str
    type: str
    description: str
    constraints: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "constraints": self.constraints
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Parameter':
        return cls(
            name=data['name'],
            type=data['type'],
            description=data['description'],
            constraints=data.get('constraints', '')
        )

@dataclass
class ContractException:
    """异常定义"""
    type: str
    condition: str
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "condition": self.condition
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ContractException':
        return cls(
            type=data['type'],
            condition=data['condition']
        )

@dataclass
class Signature:
    """函数签名定义"""
    parameters: List[Parameter]
    return_type: str
    return_description: str
    
    def to_dict(self) -> Dict:
        return {
            "parameters": [param.to_dict() for param in self.parameters],
            "return_type": self.return_type,
            "return_description": self.return_description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Signature':
        parameters = [Parameter.from_dict(param) for param in data.get('parameters', [])]
        return cls(
            parameters=parameters,
            return_type=data['return_type'],
            return_description=data['return_description']
        )

@dataclass
class ContractHelper:
    name: str
    purpose: str
    signature: Signature
    exceptions: List[ContractException]

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "signature": self.signature.to_dict(),
            "exceptions": [exc.to_dict() for exc in self.exceptions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ContractHelper':
        signature = Signature.from_dict(data['signature'])
        exceptions = [ContractException.from_dict(exc) for exc in data.get('exceptions', [])]
        return cls(
            name=data['name'],
            purpose=data['purpose'],
            signature=signature,
            exceptions=exceptions
        )

@dataclass
class MainFunction:
    """主函数定义"""
    name: str
    purpose: str
    signature: Signature
    exceptions: List[ContractException]
    complexity: str
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "signature": self.signature.to_dict(),
            "exceptions": [exc.to_dict() for exc in self.exceptions],
            "complexity": self.complexity
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MainFunction':
        signature = Signature.from_dict(data['signature'])
        exceptions = [ContractException.from_dict(exc) for exc in data.get('exceptions', [])]
        return cls(
            name=data['name'],
            purpose=data['purpose'],
            signature=signature,
            exceptions=exceptions,
            complexity=data.get('complexity', '')
        )

@dataclass
class Contract:
    main_function: MainFunction
    helper_functions: List[ContractHelper]
    design_notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "main_function": self.main_function.to_dict(),
            "helper_functions": [helper.to_dict() for helper in self.helper_functions],
            "design_notes": self.design_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Contract':
        main_function = MainFunction.from_dict(data['main_function'])
        helper_functions = [ContractHelper.from_dict(helper) for helper in data.get('helper_functions', [])]
        return cls(
            main_function=main_function,
            helper_functions=helper_functions,
            design_notes=data.get('design_notes', '')
        )
    
    # 为了保持向后兼容性，添加一些便利属性
    @property
    def name(self) -> str:
        """返回主函数名称，保持向后兼容"""
        return self.main_function.name
    
    @property
    def purpose(self) -> str:
        """返回主函数目的，保持向后兼容"""
        return self.main_function.purpose
    
    @property
    def inputs(self) -> Dict[str, str]:
        """返回输入参数字典，保持向后兼容"""
        return {param.name: param.type for param in self.main_function.signature.parameters}
    
    @property
    def outputs(self) -> str:
        """返回输出类型，保持向后兼容"""
        return self.main_function.signature.return_type
    
    @property
    def helpers(self) -> List[ContractHelper]:
        """返回辅助函数列表，保持向后兼容"""
        return self.helper_functions
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Contract':
        data = json.loads(json_str)
        return cls.from_dict(data)


class FunctionalCodeGenerator:
    DEFAULT_OUTPUT_FILE = "contract.json"
    
    def __init__(self, request: str = "", output_file: Optional[str] = None, provider: str = "deepseek", model_name: str = "deepseek-chat"):
        self.request: str = request
        self.contract_raw: str = ""
        self.contract: Optional[Contract] = None
        self.spec: Optional[Spec] = None
        self.step_graph: Optional[StepGraph] = None
        self.step_graph_raw: str = ""
        self.logic: str = ""
        self.implementation: str = ""
        self.output_file: str = output_file or self.DEFAULT_OUTPUT_FILE
        self.llm = create_llm(provider=provider, model_name=model_name)
        self.logger = logging.getLogger(__name__)               

    def generate_spec(self):
        if not self.request.strip():
            raise ValueError("Request cannot be empty")
        prompts = get_prompts("functional_code_generator")
        base_user_prompt = prompts['spec_user'].replace('{request}', self.request)
        system_prompt = prompts['spec_system']
        schema = load_schema('spec_v2.schema.json')
        max_attempts = 4
        attempt = 0
        raw = ""
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=base_user_prompt)
        ]
        while attempt < max_attempts:
            attempt += 1
            response = self.llm.call(messages=messages)
            raw = response.content
            self.contract_raw = raw
            json_obj = None
            try:
                json_start = raw.find('{')
                json_end = raw.rfind('}') + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError("No JSON braces found")
                candidate = raw[json_start:json_end]
                json_obj = json.loads(candidate)
            except Exception as e:
                self.logger.warning(f"Spec parse attempt {attempt} failed: {e}")
                messages = [
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=(
                        f"你的上一次输出无法解析为JSON (错误: {e}). 请重新输出完整且合法的 JSON, 不要添加任何解释或前后缀.\n" +
                        base_user_prompt))
                ]
                continue
            # schema validation
            schema_errors = validate_json_against_schema(json_obj, schema)
            if schema_errors:
                self.logger.warning(f"Spec schema errors attempt {attempt}: {schema_errors}")
                # build repair prompt with error list
                error_list = "\n".join([f"- {err}" for err in schema_errors])
                repair_instruction = (
                    "上一次JSON不符合Schema。请只输出修正后的完整JSON。不要输出除JSON外的任何文本。\n"
                    f"错误列表:\n{error_list}\n保持已有正确字段不变，修复错误后再输出。"
                )
                messages = [
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=repair_instruction),
                ]
                continue
            # Passed schema
            try:
                self.spec = self._parse_spec_response(json.dumps(json_obj, ensure_ascii=False))
                # semantic validation
                _errors, warnings = SpecValidator.validate(self.spec)
                for w in warnings:
                    self.logger.warning(f"Spec warning: {w.format()}")
                # build legacy contract for downstream logic
                if self.spec and self.spec.main_function:
                    legacy_json = {
                        "main_function": self.spec.main_function.to_dict(),
                        "helper_functions": [h.to_dict() for h in self.spec.helper_functions],
                        "design_notes": self.spec.design_notes,
                    }
                    self.contract = Contract.from_dict(legacy_json)
                self._save_contract_to_file()
                self.logger.info(f"Spec generated (attempt {attempt}) for function: {self.spec.name if self.spec else 'UNKNOWN'}")
                return
            except SpecValidationError as se:
                self.logger.warning(f"Semantic validation failed attempt {attempt}: {se}")
                repair_instruction = (
                    "语义校验失败，请修复以下问题并重新输出完整JSON（不可添加解释）。\n" + str(se)
                )
                messages = [
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=repair_instruction),
                ]
                continue
            except Exception as e:  # generic parse to Spec failure
                self.logger.warning(f"Spec object construction failed attempt {attempt}: {e}")
                messages = [
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=(
                        f"无法构造规范对象 (错误: {e}). 请重新输出完整合法 JSON。\n" + base_user_prompt))
                ]
                continue
        # if loop ends without return
        self._save_failed_spec(raw, "Exceeded max attempts for spec generation")
        raise RuntimeError("Failed to generate valid spec within retry limit")

    def generate_step_graph(self):
        if not self.spec:
            raise ValueError("Spec must be generated before step graph")
        prompts = get_prompts("functional_code_generator")
        system_prompt = prompts['step_graph_system']
        base_user_prompt = prompts['step_graph_user'].replace('{spec_json}', self.contract_raw)
        max_attempts = 3
        attempt = 0
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=base_user_prompt)
        ]
        last_raw = ""
        while attempt < max_attempts:
            attempt += 1
            response = self.llm.call(messages=messages)
            raw = response.content
            last_raw = raw
            self.step_graph_raw = raw
            try:
                json_start = raw.find('{')
                json_end = raw.rfind('}') + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError("No JSON object found in step graph response")
                json_str = raw[json_start:json_end]
                data = json.loads(json_str)
            except Exception as e:
                self.logger.warning(f"StepGraph parse attempt {attempt} failed: {e}")
                repair_prompt = (
                    f"上一次输出无法解析为合法JSON (错误: {e}). 只输出修正后的完整 StepGraph JSON, 不要附加解释或Markdown。\n" +
                    base_user_prompt
                )
                messages = [
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=repair_prompt)
                ]
                continue
            try:
                candidate = StepGraph.from_dict(data)
                pre_ids = {p.id for p in self.spec.pre}
                post_ids = {p.id for p in self.spec.post}
                inv_ids = {p.id for p in self.spec.invariants}
                StepGraphValidator.validate(candidate, pre_ids, post_ids, inv_ids)
                # order fallback if empty
                if not candidate.order:
                    candidate.order = [s.id for s in candidate.steps]
                # simple sanity: ensure every step id appears exactly once in logic generation order
                if len(set(candidate.order)) != len(candidate.steps):
                    raise StepGraphValidationError("order must list each step id exactly once")
                self.step_graph = candidate
                self.logger.info(f"StepGraph generated successfully (attempt {attempt}) with %d steps", len(candidate.steps))
                return
            except StepGraphValidationError as ve:
                self.logger.warning(f"StepGraph validation attempt {attempt} failed: {ve}")
                repair_prompt = (
                    "上一次 StepGraph JSON 结构/引用校验失败。请仅输出修正后的完整 JSON。不要添加解释。错误如下:\n" +
                    str(ve) + "\n重新生成时保持已正确字段不变，修复错误。"
                )
                messages = [
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=repair_prompt)
                ]
                continue
            except Exception as e:
                self.logger.warning(f"StepGraph construction unexpected error attempt {attempt}: {e}")
                repair_prompt = (
                    f"内部构造失败 (错误: {e}). 请重新输出完整合法 StepGraph JSON。\n" + base_user_prompt
                )
                messages = [
                    Message(role="system", content=system_prompt),
                    Message(role="user", content=repair_prompt)
                ]
                continue
        # exceeded attempts
        self.logger.error("Failed to generate valid StepGraph within retry limit")
        raise RuntimeError("Failed to generate StepGraph within retry limit")

    def generate_logic_from_step_graph(self):
        if not (self.spec and self.step_graph):
            raise ValueError("Spec and StepGraph must be generated before logic generation")
        mf = self.spec.main_function
        if not mf:
            raise ValueError("Main function missing in spec")
        params_sig = ", ".join([f"{p.name}: {p.type}" for p in mf.signature.parameters])
        returns = mf.signature.return_type
        parameter_docs = []
        for p in mf.signature.parameters:
            line = f"{p.name} ({p.type})"
            parameter_docs.append(line)
        parameter_doc_block = "\n        ".join(parameter_docs)
        exception_docs = []
        if self.spec.types.exceptions:
            for exc in self.spec.types.exceptions:
                exception_docs.append(f"{exc.type}: {exc.predicate}")
        exception_block = "\n        ".join(exception_docs)
        # Embed compact step graph JSON (single line) for traceability
        sg_json_compact = json.dumps(self.step_graph.to_dict(), separators=(',', ':'))
        lines = [
            f"# STEP_GRAPH: {sg_json_compact}",
            f"def {mf.name}({params_sig}) -> {returns}:",
            '    """',
            f"    {mf.purpose}",
            "",  # blank line inside docstring
            "    Args:",
            "        " + parameter_doc_block if parameter_doc_block else "        (none)",
            "", "    Returns:", f"        {returns}",
            "", "    Raises:", "        " + exception_block if exception_block else "        (none)",
            '    """',
        ]
        # Map steps in order
        order = self.step_graph.order or [s.id for s in self.step_graph.steps]
        step_lookup = {s.id: s for s in self.step_graph.steps}
        for sid in order:
            step = step_lookup[sid]
            refs_pre = ','.join(step.pre_refs) or '-'
            refs_post = ','.join(step.post_refs) or '-'
            refs_inv = ','.join(step.invariant_refs) or '-'
            refs_evd = ','.join(step.evidence_hooks) or '-'
            lines.append(f"    # [{step.id}] intent: {step.intent}")
            lines.append(f"    # refs pre:[{refs_pre}] post:[{refs_post}] inv:[{refs_inv}] evidence:[{refs_evd}]")
            lines.append(f"    # TODO({step.id}): implement step")
            lines.append("    pass  # placeholder")
            lines.append("")
        self.logic = "\n".join(lines)
        self.logger.info("Logic (anchored) generated from StepGraph with %d steps", len(order))

    def generate_contract(self):  # pragma: no cover
        self.generate_spec()

    def _save_contract_to_file(self):
        if self.contract_raw:
            try:
                Path(self.output_file).write_text(self.contract_raw, encoding='utf-8')
                self.logger.debug(f"Contract saved to {self.output_file}")
            except Exception as e:
                self.logger.warning(f"Failed to save contract to file: {e}")
    
    def _save_failed_spec(self, raw: str, errors: str):
        try:
            ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            path = Path(self.output_file).parent / f"failed_spec_{ts}.json"
            data = {"raw": raw, "errors": errors}
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            self.logger.error(f"Failed spec saved to {path}")
        except Exception as e:
            self.logger.error(f"Could not save failed spec: {e}")
    
    def _parse_spec_response(self, response: str) -> Spec:
        if not response or not response.strip():
            raise ValueError("Empty response received from LLM")
        
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON object found in the response")
        json_str = response[json_start:json_end]
        
        try:
            return Spec.from_json(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in spec response: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required field in spec: {e}")

    def generate_logic(self):
        if not (self.contract or self.spec):
            raise ValueError("Spec/Contract must be generated before generating logic")
        try:
            prompts = get_prompts("functional_code_generator")
            target_contract = self.contract
            parameters = ", ".join([f"{param.name}: {param.type}" for param in target_contract.main_function.signature.parameters])  # type: ignore
            parameter_docs = []
            for param in target_contract.main_function.signature.parameters:  # type: ignore
                param_doc = f"{param.name} ({param.type}): {param.description}"
                if getattr(param, 'constraints', ''):
                    param_doc += f". Constraints: {param.constraints}"
                parameter_docs.append(param_doc)
            parameter_documentation = "\n        ".join(parameter_docs)
            exception_docs = []
            for exc in target_contract.main_function.exceptions:  # type: ignore
                exception_docs.append(f"{exc.type}: {exc.condition}")
            exception_documentation = "\n        ".join(exception_docs)
            helper_function_logic = ""
            if target_contract.helper_functions:  # type: ignore
                helper_parts = []
                for helper in target_contract.helper_functions:  # type: ignore
                    helper_params = ", ".join([f"{param.name}: {param.type}" for param in helper.signature.parameters])
                    helper_part = f"""
def {helper.name}({helper_params}) -> {helper.signature.return_type}:
    \"\"\"
    {helper.purpose}
    \"\"\"
    # TODO: Implement {helper.name}
    pass"""
                    helper_parts.append(helper_part)
                helper_function_logic = "\n".join(helper_parts)
            user_logic_prompt = prompts['logic_user'].format(
                contract=self.contract_raw,
                function_name=target_contract.name,  # type: ignore
                parameters=parameters,
                return_type=target_contract.outputs,  # type: ignore
                function_purpose=target_contract.purpose,  # type: ignore
                chosen_algorithm_approach="TBD (to be determined by LLM)",
                parameter_documentation=parameter_documentation,
                return_documentation=target_contract.main_function.signature.return_description,  # type: ignore
                exception_documentation=exception_documentation,
                helper_function_logic=helper_function_logic
            )
            messages = [
                Message(role="system", content=prompts['logic_system']),
                Message(role="user", content=user_logic_prompt),
            ]
            response = self.llm.call(messages=messages)
            self.logic = response.content
            self.logger.info("Logic generated successfully")
        except Exception as e:
            self.logger.error(f"Error generating logic: {e}")
            raise

    def generate_implementation(self):
        if not self.logic:
            raise ValueError("Logic must be generated before generating implementation")
        
        try:
            prompts = get_prompts("implementation")
            user_implementation_prompt = prompts['user'].format(
                logic=self.logic,
            )
            
            messages = [
                Message(role="system", content=prompts['system']),
                Message(role="user", content=user_implementation_prompt)
            ]
            
            response = self.llm.call(messages=messages)
            self.implementation = response.content
            self.logger.info("Implementation generated successfully")
        except Exception as e:
            self.logger.error(f"Error generating implementation: {e}")
            raise
    
    def generate_all(self) -> str:
        """Generate spec, step graph, logic, and implementation in sequence"""
        self.generate_spec()
        self.generate_step_graph()
        self.generate_logic_from_step_graph()
        self.generate_implementation()
        return self.implementation
    
    def reset(self):
        """Reset all generated content"""
        self.contract_raw = ""
        self.contract = None
        self.spec = None
        self.step_graph = None
        self.step_graph_raw = ""
        self.logic = ""
        self.implementation = ""


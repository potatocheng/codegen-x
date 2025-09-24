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
        self.logic: str = ""
        self.implementation: str = ""
        self.output_file: str = output_file or self.DEFAULT_OUTPUT_FILE
        self.llm = create_llm(provider=provider, model_name=model_name)
        self.logger = logging.getLogger(__name__)               

    def generate_spec(self):
        if not self.request.strip():
            raise ValueError("Request cannot be empty")
        prompts = get_prompts("functional_code_generator")
        user_prompt = prompts['spec_user'].replace('{request}', self.request)
        messages = [
            Message(role="system", content=prompts['spec_system']),
            Message(role="user", content=user_prompt)
        ]
        try:
            response = self.llm.call(messages=messages)
            raw = response.content
            self.contract_raw = raw
            self._save_contract_to_file()
            self.spec = self._parse_spec_response(raw)
            # validate spec before producing legacy contract
            try:
                _errors, warnings = SpecValidator.validate(self.spec)  # errors would raise before return
                for w in warnings:
                    self.logger.warning(f"Spec warning: {w.format()}")
            except SpecValidationError as e:
                self._save_failed_spec(raw, str(e))
                raise
            if self.spec and self.spec.main_function:
                legacy_json = {
                    "main_function": self.spec.main_function.to_dict(),
                    "helper_functions": [h.to_dict() for h in self.spec.helper_functions],
                    "design_notes": self.spec.design_notes,
                }
                self.contract = Contract.from_dict(legacy_json)
            self.logger.info(f"Spec generated successfully for function: {self.spec.name if self.spec else 'UNKNOWN'}")
        except Exception as e:
            self._save_contract_to_file()
            self.logger.error(f"Error generating spec: {e}")
            if self.contract_raw:
                self.logger.debug(f"Raw spec response: {self.contract_raw}")
            raise

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
        """Generate spec, logic, and implementation in sequence"""
        self.generate_spec()
        self.generate_logic()
        self.generate_implementation()
        return self.implementation
    
    def reset(self):
        """Reset all generated content"""
        self.contract_raw = ""
        self.contract = None
        self.spec = None
        self.logic = ""
        self.implementation = ""


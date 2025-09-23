import unittest
from unittest.mock import Mock, patch
from typing import List, Dict, Any, Optional
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm_interface import LLMInterface, LLMResponse
from llm.message import Message
from codegen.functional_code_generator import FunctionalCodeGenerator, Contract, ContractHelper


class MockLLMInterface(LLMInterface):
    """
    Mock LLM接口，简单地将传入的messages内容作为response返回
    """
    
    def __init__(self, model_name: str = "mock_model", config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, config)
    
    def _create_client(self) -> Any:
        """Mock客户端创建，返回None"""
        return None
    
    def call(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """
        Mock call方法，将所有messages的content连接起来作为response返回
        """
        # 将所有messages的content连接起来
        combined_content = "\n".join([msg.content for msg in messages])
        
        return LLMResponse(
            content=combined_content,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            model=self.model_name,
            finish_reason="stop",
            response_time=0.1
        )
    
    async def acall(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """
        Mock异步call方法，与同步方法行为一致
        """
        return self.call(messages, **kwargs)


class TestFunctionalCodeGenerator(unittest.TestCase):
    """
    测试FunctionalCodeGenerator类
    """
    
    def setUp(self):
        """设置测试环境"""
        self.mock_llm = MockLLMInterface()
        self.generator = FunctionalCodeGenerator(request="测试请求")
    
    # def test_mock_llm_interface(self):
    #     """测试mock LLM接口是否正常工作"""
    #     messages = [
    #         Message(role="system", content="You are a helpful assistant."),
    #         Message(role="user", content="Hello, how are you?")
    #     ]
        
    #     response = self.mock_llm.call(messages)
        
    #     # 验证响应内容是传入messages的拼接
    #     expected_content = "You are a helpful assistant.\nHello, how are you?"
    #     self.assertEqual(response.content, expected_content)
    #     self.assertEqual(response.model, "mock_model")
    #     self.assertEqual(response.finish_reason, "stop")
    
    # def test_mock_llm_with_single_message(self):
    #     """测试单个message的情况"""
    #     messages = [Message(role="user", content="Test message")]
        
    #     response = self.mock_llm.call(messages)
        
    #     self.assertEqual(response.content, "Test message")
    
    # def test_mock_llm_with_empty_messages(self):
    #     """测试空messages的情况"""
    #     messages = []
        
    #     response = self.mock_llm.call(messages)
        
    #     self.assertEqual(response.content, "")
    
    # @patch('llm.factory.create_llm')
    # def test_functional_code_generator_with_mock_llm(self, mock_create_llm):
    #     """测试使用mock LLM的FunctionalCodeGenerator"""
    #     # 配置mock factory返回我们的mock LLM
    #     mock_create_llm.return_value = self.mock_llm
        
    #     # 这里可以添加对FunctionalCodeGenerator的实际测试
    #     # 例如：generator = FunctionalCodeGenerator()
    #     # result = generator.some_method()
        
    #     # 验证mock LLM被正确调用
    #     # mock_create_llm.assert_called_once()
    #     pass
    
    # def test_custom_response_mock_llm(self):
    #     """测试自定义响应的mock LLM"""
        
    #     class CustomMockLLM(MockLLMInterface):
    #         """自定义响应的mock LLM"""
            
    #         def __init__(self, custom_response: str):
    #             super().__init__()
    #             self.custom_response = custom_response
            
    #         def call(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
    #             """返回自定义响应而不是messages内容"""
    #             return LLMResponse(
    #                 content=self.custom_response,
    #                 usage={"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
    #                 model=self.model_name,
    #                 finish_reason="stop",
    #                 response_time=0.05
    #             )
        
    #     # 创建自定义响应的mock
    #     custom_llm = CustomMockLLM("This is a custom response")
        
    #     messages = [Message(role="user", content="Any question")]
    #     response = custom_llm.call(messages)
        
    #     self.assertEqual(response.content, "This is a custom response")
    #     self.assertIsNotNone(response.usage)
    #     if response.usage:
    #         self.assertEqual(response.usage["total_tokens"], 15)

    # @patch('codegen.functional_code_generator.FunctionalCodeGenerator.generate_contract')
    # def test_generate_contract_mock(self, mock_generate_contract):
    #     """测试mock generate_contract方法"""
    #     # 设置mock的返回值或行为
    #     mock_generate_contract.return_value = None
        
    #     # 创建FunctionalCodeGenerator实例
    #     generator = FunctionalCodeGenerator(request="创建一个计算器函数")
        
    #     # 调用generate_contract方法
    #     result = generator.generate_contract()
        
    #     # 验证mock方法被调用
    #     mock_generate_contract.assert_called_once()
        
    #     # 验证结果
    #     self.assertIsNone(result)
    
    # @patch('codegen.functional_code_generator.create_llm')
    # @patch('codegen.functional_code_generator.get_prompts')
    # def test_generate_contract_with_mock_prompts(self, mock_get_prompts, mock_create_llm):
    #     """测试使用mock prompts的generate_contract方法"""
    #     # Mock prompts配置
    #     mock_prompts = {
    #         'contract_system': 'You are a helpful assistant.',
    #         'contract_user': 'Create a contract for: {request}'
    #     }
    #     mock_get_prompts.return_value = mock_prompts
        
    #     # Mock LLM响应
    #     mock_contract_response = '''
    #     {
    #         "name": "calculator",
    #         "purpose": "执行基本的数学运算",
    #         "inputs": {"a": "float", "b": "float", "operation": "str"},
    #         "outputs": "float",
    #         "helpers": []
    #     }
    #     '''
        
    #     mock_llm_instance = MockLLMInterface()
    #     mock_llm_instance.call = Mock(return_value=LLMResponse(
    #         content=mock_contract_response,
    #         usage={"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
    #         model="mock_model",
    #         finish_reason="stop"
    #     ))
        
    #     mock_create_llm.return_value = mock_llm_instance
        
    #     # 创建generator并调用generate_contract
    #     generator = FunctionalCodeGenerator(request="创建一个计算器函数")
    #     generator.generate_contract()
        
    #     # 验证prompts被正确调用
    #     mock_get_prompts.assert_called_once_with("functional_code_generator")
        
    #     # 验证LLM被正确调用
    #     mock_llm_instance.call.assert_called_once()
        
    #     # 验证contract_raw被设置
    #     self.assertEqual(generator.contract_raw.strip(), mock_contract_response.strip())
        
    #     # 验证contract对象被正确解析
    #     self.assertIsNotNone(generator.contract)
    #     if generator.contract:
    #         self.assertEqual(generator.contract.name, "calculator")
    #         self.assertEqual(generator.contract.purpose, "执行基本的数学运算")
    
    # def test_contract_creation_and_parsing(self):
    #     """测试Contract对象的创建和解析"""
    #     # 创建一个Contract对象
    #     contract = Contract(
    #         name="test_function",
    #         purpose="测试函数",
    #         inputs={"x": "int", "y": "str"},
    #         outputs="bool",
    #         helpers=[
    #             ContractHelper(
    #                 name="helper_func",
    #                 purpose="辅助函数",
    #                 inputs={"data": "str"},
    #                 outputs="str"
    #             )
    #         ]
    #     )
        
    #     # 测试转换为JSON
    #     json_str = contract.to_json()
    #     self.assertIn("test_function", json_str)
    #     self.assertIn("测试函数", json_str)
        
    #     # 测试从JSON恢复
    #     restored_contract = Contract.from_json(json_str)
    #     self.assertEqual(restored_contract.name, "test_function")
    #     self.assertEqual(restored_contract.purpose, "测试函数")
    #     self.assertEqual(len(restored_contract.helpers), 1)
    #     self.assertEqual(restored_contract.helpers[0].name, "helper_func")

    def test_parse_contract_response(self):
        self.generator.contract_raw = """
Here's the comprehensive function contract for the requested algorithm problem:

```json
{
    "main_function": {
        "name": "remove_duplicates",
        "purpose": "Removes duplicate elements from a non-strictly increasing array in-place, maintaining relative order of elements, and returns the count of unique elements.",
        "signature": {
            "parameters": [
                {
                    "name": "nums",
                    "type": "List[int]",
                    "description": "A non-strictly increasing array of integers with possible duplicates",
                    "constraints": "Must be non-strictly increasing (nums[i] <= nums[i+1] for all valid i). Must be mutable."
                }
            ],
            "return_type": "int",
            "return_description": "The count of unique elements in the modified array. The first k elements of nums will contain the unique elements in their original order."
        },
        "exceptions": [
            {
                "type": "ValueError",
                "condition": "If input array is not non-strictly increasing"
            },
            {
                "type": "TypeError",
                "condition": "If input is not a list or contains non-integer elements"
            }
        ],
        "complexity": "O(n) time complexity where n is the length of the input array. O(1) space complexity as operation is performed in-place."
    },
    "helper_functions": [
        {
            "name": "_validate_input",
            "purpose": "Validates that the input array meets the non-strictly increasing requirement and contains only integers.",
            "signature": {
                "parameters": [
                    {
                        "name": "nums",
                        "type": "List[int]",
                        "description": "Array to validate",
                        "constraints": "Must be a list"
                    }
                ],
                "return_type": "bool",
                "return_description": "True if input is valid, raises exceptions otherwise"
            },
            "exceptions": [
                {
                    "type": "ValueError",
                    "condition": "If array is not non-strictly increasing"
                },
                {
                    "type": "TypeError",
                    "condition": "If input is not a list or contains non-integer elements"
                }
            ]
        }
    ],
    "design_notes": [
        "The function modifies the input array in-place to optimize space usage.",
        "The solution uses a two-pointer technique where one pointer tracks the position to insert the next unique element and another scans through the array.",
        "We assume that empty arrays are valid input and will return 0.",
        "The relative order of elements is preserved by design as we process the array sequentially.",
        "The validation helper ensures the contract is respected before processing begins."
    ]
}
```

Key aspects of this contract:
1. Clearly defines the in-place modification requirement and return value
2. Specifies input validation requirements
3. Documents expected exceptions
4. Provides complexity analysis
5. Includes a helper function for input validation
6. Notes design decisions about the two-pointer approach and edge cases

The contract ensures the function can be implemented unambiguously while providing all necessary information for testing and usage.s
"""

        contract = self.generator._parse_contract_response(self.generator.contract_raw)
        self.assertEqual(contract.name, "remove_duplicates")


if __name__ == '__main__':
    unittest.main()
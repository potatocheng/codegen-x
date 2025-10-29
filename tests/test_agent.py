"""
测试新的Agent架构
"""
import unittest
from unittest.mock import Mock, MagicMock
from pydantic import BaseModel, Field
from typing import List

from llm.structured_llm import StructuredLLM
from agent.code_agent import CodeGenAgent
from tools.spec_tool import FunctionSpec, Parameter, Example, ExceptionCase
from tools.implement_tool import Implementation
from tools.validate_tool import ValidationResult, TestResult


class MockStructuredLLM:
    """Mock的StructuredLLM，用于测试"""

    def __init__(self):
        self.call_count = 0
        self.responses = {}

    def generate_structured(self, prompt: str, output_schema: type, **kwargs):
        """模拟结构化输出"""
        self.call_count += 1

        # 根据output_schema返回不同的mock数据
        if output_schema == FunctionSpec:
            return FunctionSpec(
                name="remove_duplicates",
                purpose="从有序数组中删除重复元素",
                parameters=[
                    Parameter(
                        name="nums",
                        type="List[int]",
                        description="有序整数数组",
                        constraints="必须是有序的"
                    )
                ],
                return_type="int",
                return_description="去重后的数组长度",
                examples=[
                    Example(
                        inputs={"nums": [1, 1, 2]},
                        expected_output=2,
                        description="简单情况"
                    ),
                    Example(
                        inputs={"nums": []},
                        expected_output=0,
                        description="空数组"
                    )
                ],
                edge_cases=["空数组", "所有元素相同", "无重复元素"],
                exceptions=[
                    ExceptionCase(
                        type="TypeError",
                        condition="输入不是列表"
                    )
                ],
                complexity="O(n) 时间, O(1) 空间",
                notes="原地修改数组"
            )

        elif output_schema == Implementation:
            # 返回一个正确的实现
            code = '''def remove_duplicates(nums: List[int]) -> int:
    """从有序数组中删除重复元素"""
    if not nums:
        return 0

    write_index = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[i-1]:
            nums[write_index] = nums[i]
            write_index += 1

    return write_index
'''
            return Implementation(
                code=code,
                explanation="使用双指针法，一个指针遍历，一个指针记录写入位置",
                test_cases=[
                    "assert remove_duplicates([1,1,2]) == 2",
                    "assert remove_duplicates([]) == 0"
                ]
            )

        # 默认返回空对象
        return output_schema()


class TestCodeGenAgent(unittest.TestCase):
    """测试CodeGenAgent"""

    def setUp(self):
        """设置测试环境"""
        self.mock_llm = MockStructuredLLM()
        self.agent = CodeGenAgent(self.mock_llm, max_refine_attempts=2)

    def test_agent_initialization(self):
        """测试Agent初始化"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(len(self.agent.tools), 4)
        self.assertIn("generate_spec", self.agent.tools)
        self.assertIn("implement_function", self.agent.tools)
        self.assertIn("validate_code", self.agent.tools)
        self.assertIn("refine_code", self.agent.tools)

    def test_spec_tool(self):
        """测试SpecTool"""
        spec_tool = self.agent.tools["generate_spec"]
        result = spec_tool.execute(spec_tool.input_schema(
            requirement="写一个删除有序数组重复元素的函数"
        ))

        self.assertTrue(result.success)
        self.assertIsInstance(result.data, FunctionSpec)
        self.assertEqual(result.data.name, "remove_duplicates")

    def test_implement_tool(self):
        """测试ImplementTool"""
        # 先生成spec
        spec_tool = self.agent.tools["generate_spec"]
        spec_result = spec_tool.execute(spec_tool.input_schema(
            requirement="写一个删除有序数组重复元素的函数"
        ))
        spec = spec_result.data

        # 然后实现
        impl_tool = self.agent.tools["implement_function"]
        impl_result = impl_tool.execute(impl_tool.input_schema(
            spec=spec,
            style="concise"
        ))

        self.assertTrue(impl_result.success)
        self.assertIsInstance(impl_result.data, Implementation)
        self.assertIn("def remove_duplicates", impl_result.data.code)

    def test_validate_tool(self):
        """测试ValidateTool"""
        # 准备spec
        spec = FunctionSpec(
            name="add",
            purpose="加法",
            parameters=[
                Parameter(name="a", type="int", description="第一个数"),
                Parameter(name="b", type="int", description="第二个数")
            ],
            return_type="int",
            return_description="和",
            examples=[
                Example(inputs={"a": 1, "b": 2}, expected_output=3),
                Example(inputs={"a": 0, "b": 0}, expected_output=0)
            ],
            edge_cases=[],
            exceptions=[]
        )

        # 正确的代码
        code = "def add(a: int, b: int) -> int:\n    return a + b"

        validate_tool = self.agent.tools["validate_code"]
        result = validate_tool.execute(validate_tool.input_schema(
            code=code,
            spec=spec
        ))

        self.assertTrue(result.success)
        validation = result.data
        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.passed_count, 2)

    def test_validate_tool_with_wrong_code(self):
        """测试ValidateTool对错误代码的验证"""
        spec = FunctionSpec(
            name="add",
            purpose="加法",
            parameters=[
                Parameter(name="a", type="int", description="第一个数"),
                Parameter(name="b", type="int", description="第二个数")
            ],
            return_type="int",
            return_description="和",
            examples=[
                Example(inputs={"a": 1, "b": 2}, expected_output=3)
            ],
            edge_cases=[],
            exceptions=[]
        )

        # 错误的代码（返回差而不是和）
        code = "def add(a: int, b: int) -> int:\n    return a - b"

        validate_tool = self.agent.tools["validate_code"]
        result = validate_tool.execute(validate_tool.input_schema(
            code=code,
            spec=spec
        ))

        self.assertTrue(result.success)
        validation = result.data
        self.assertFalse(validation.is_valid)
        self.assertEqual(validation.passed_count, 0)


class TestToolSchemas(unittest.TestCase):
    """测试工具的Schema定义"""

    def test_function_spec_schema(self):
        """测试FunctionSpec可以正确序列化"""
        spec = FunctionSpec(
            name="test",
            purpose="测试",
            parameters=[],
            return_type="None",
            return_description="无",
            examples=[],
            edge_cases=[],
            exceptions=[]
        )

        # 测试可以转换为dict和JSON
        spec_dict = spec.model_dump()
        self.assertEqual(spec_dict["name"], "test")

    def test_implementation_schema(self):
        """测试Implementation可以正确序列化"""
        impl = Implementation(
            code="def test(): pass",
            explanation="测试函数",
            test_cases=[]
        )

        impl_dict = impl.model_dump()
        self.assertIn("code", impl_dict)


if __name__ == "__main__":
    unittest.main()

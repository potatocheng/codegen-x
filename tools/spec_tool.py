from pydantic import BaseModel, Field
from typing import List, Dict, Any
from tools.base import Tool, ToolInput, ToolOutput


class SpecInput(ToolInput):
    """生成规范的输入"""
    requirement: str = Field(description="用户需求描述", min_length=1)


class Parameter(BaseModel):
    """函数参数定义"""
    name: str = Field(description="参数名称")
    type: str = Field(description="参数类型")
    description: str = Field(description="参数描述")
    constraints: str = Field(default="", description="参数约束")


class Example(BaseModel):
    """函数示例"""
    inputs: Dict[str, Any] = Field(description="输入参数")
    expected_output: Any = Field(description="期望输出")
    description: str = Field(default="", description="示例描述")


class ExceptionCase(BaseModel):
    """异常情况"""
    type: str = Field(description="异常类型")
    condition: str = Field(description="触发条件")
    message: str = Field(default="", description="异常消息")


class FunctionSpec(BaseModel):
    """结构化的函数规范"""
    name: str = Field(description="函数名称")
    purpose: str = Field(description="函数目的和功能描述")
    parameters: List[Parameter] = Field(description="函数参数列表")
    return_type: str = Field(description="返回值类型")
    return_description: str = Field(description="返回值描述")
    examples: List[Example] = Field(description="示例用例，包含正常和边界情况", min_items=1)
    edge_cases: List[str] = Field(description="需要考虑的边界情况")
    exceptions: List[ExceptionCase] = Field(description="可能抛出的异常")
    complexity: str = Field(default="", description="时间和空间复杂度")
    notes: str = Field(default="", description="额外的设计说明")

    class Config:
        """Pydantic配置"""
        extra = "forbid"


class SpecTool(Tool):
    """规范生成工具

    根据用户需求生成详细的函数规范，包含函数签名、示例、边界情况和异常处理。
    """

    name = "generate_spec"
    description = "根据用户需求生成详细的函数规范，包含函数签名、示例、边界情况和异常处理"
    input_schema = SpecInput

    def __init__(self, llm):
        super().__init__()
        self.llm = llm

    def _execute_impl(self, input_data: SpecInput) -> ToolOutput:
        """生成函数规范"""
        prompt = f"""请为以下需求生成一个详细的函数规范：

需求：{input_data.requirement}

要求：
1. 函数名称应该清晰表达其功能
2. 参数设计要合理，类型标注要准确
3. 至少提供3个示例用例（包含正常情况和边界情况）
4. 列出所有需要考虑的边界情况
5. 说明可能抛出的异常
6. 分析时间和空间复杂度

注意：确保示例的输入输出数据类型正确匹配。
"""

        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                output_schema=FunctionSpec,
                system="你是一个专业的软件架构师，擅长设计清晰、健壮的函数接口。"
            )

            return ToolOutput.success_result(
                data=response,
                message=f"已生成函数规范：{response.name}",
                requirement=input_data.requirement,
                parameter_count=len(response.parameters),
                example_count=len(response.examples)
            )

        except Exception as e:
            return ToolOutput.error_result(
                f"生成规范失败：{str(e)}",
                requirement=input_data.requirement,
                error_type=type(e).__name__
            )

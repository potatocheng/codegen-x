from pydantic import BaseModel, Field
from typing import List
from tools.base import Tool, ToolInput, ToolOutput
from tools.spec_tool import FunctionSpec


class ImplementInput(ToolInput):
    """实现代码的输入"""
    spec: FunctionSpec = Field(description="函数规范")
    style: str = Field(
        default="concise",
        description="代码风格：concise(简洁), documented(文档详细), defensive(防御性编程)"
    )


class Implementation(BaseModel):
    """代码实现结果"""
    code: str = Field(description="完整的函数实现代码")
    explanation: str = Field(description="实现思路和关键逻辑说明")
    test_cases: List[str] = Field(description="基于示例生成的测试用例代码")


class ImplementOutput(ToolOutput):
    """实现代码的输出"""
    data: Implementation


class ImplementTool(Tool):
    """代码实现工具"""
    name = "implement_function"
    description = "根据函数规范实现代码，生成完整的函数实现和测试用例"
    input_schema = ImplementInput

    def __init__(self, llm):
        self.llm = llm

    def execute(self, input: ImplementInput) -> ImplementOutput:
        """实现函数"""
        spec = input.spec

        # 构建详细的实现提示
        examples_str = "\n".join([
            f"示例{i+1}: 输入{ex.inputs} -> 输出{ex.expected_output} ({ex.description})"
            for i, ex in enumerate(spec.examples)
        ])

        edge_cases_str = "\n".join([f"- {case}" for case in spec.edge_cases])

        exceptions_str = "\n".join([
            f"- {exc.type}: {exc.condition}"
            for exc in spec.exceptions
        ])

        prompt = f"""请实现以下函数：

函数名：{spec.name}
目的：{spec.purpose}

参数：
{self._format_parameters(spec.parameters)}

返回值：{spec.return_type} - {spec.return_description}

示例用例：
{examples_str}

边界情况：
{edge_cases_str}

异常处理：
{exceptions_str}

复杂度要求：{spec.complexity if spec.complexity else "尽可能优化"}

代码风格：{input.style}

要求：
1. 实现完整的函数代码
2. 处理所有边界情况
3. 包含适当的异常处理
4. 添加必要的注释
5. 生成对应的测试用例代码（使用assert语句）

【重要的行有效性要求】：
- 每一行代码都必须有明确的用途，对逻辑流有直接贡献
- 禁止包含以下内容：
  * 冗余的赋值（如重复赋值同一变量）
  * 从未被使用的变量定义
  * 无关的调试代码
  * 重复的代码块
  * 过度的中间变量（除非有必要提高可读性）
- 优先选择简洁高效的实现方式
- 只添加提高代码理解的注释（不要过度注释）
"""

        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                output_schema=Implementation,
                system="你是一个专业的Python开发者，擅长编写清晰、高效、健壮的代码。"
            )

            return ImplementOutput(
                success=True,
                data=response,
                message=f"已实现函数：{spec.name}"
            )
        except Exception as e:
            return ImplementOutput(
                success=False,
                data=None,
                message=f"实现函数失败：{str(e)}"
            )

    def _format_parameters(self, parameters: List) -> str:
        """格式化参数列表"""
        if not parameters:
            return "无参数"

        lines = []
        for param in parameters:
            line = f"- {param.name}: {param.type} - {param.description}"
            if param.constraints:
                line += f" (约束: {param.constraints})"
            lines.append(line)
        return "\n".join(lines)

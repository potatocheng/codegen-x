from pydantic import BaseModel, Field
from tools.base import Tool, ToolInput, ToolOutput
from tools.spec_tool import FunctionSpec
from tools.validate_tool import ValidationResult
from tools.implement_tool import Implementation


class RefineInput(ToolInput):
    """优化代码的输入"""
    code: str = Field(description="当前的代码实现")
    spec: FunctionSpec = Field(description="函数规范")
    validation_result: ValidationResult = Field(description="验证结果")


class RefineOutput(ToolOutput):
    """优化代码的输出"""
    data: Implementation


class RefineTool(Tool):
    """代码优化工具"""
    name = "refine_code"
    description = "根据验证结果修复代码问题，改进实现"
    input_schema = RefineInput

    def __init__(self, llm):
        self.llm = llm

    def execute(self, input: RefineInput) -> RefineOutput:
        """优化代码"""
        spec = input.spec
        code = input.code
        validation = input.validation_result

        # 构建失败测试的详细信息
        failed_tests_info = []
        for test in validation.test_results:
            if not test.passed:
                info = f"""
测试: {test.test_name}
输入: {test.input_values}
期望输出: {test.expected_output}
实际输出: {test.actual_output if test.actual_output is not None else "N/A"}
错误: {test.error}
"""
                failed_tests_info.append(info)

        failed_tests_str = "\n".join(failed_tests_info)
        suggestions_str = "\n".join([f"- {s}" for s in validation.suggestions])

        prompt = f"""请修复以下代码的问题：

原始规范：
函数名：{spec.name}
目的：{spec.purpose}

当前实现：
```python
{code}
```

测试结果：通过 {validation.passed_count}/{validation.total_tests} 个测试

失败的测试：
{failed_tests_str}

改进建议：
{suggestions_str}

要求：
1. 仔细分析失败原因
2. 修复所有测试失败的问题
3. 确保处理所有边界情况
4. 保持代码清晰和高效
5. 不要改变函数签名（除非规范要求）
"""

        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                output_schema=Implementation,
                system="你是一个专业的代码审查者和问题解决专家，擅长调试和优化代码。"
            )

            return RefineOutput(
                success=True,
                data=response,
                message=f"已优化代码，修复了 {validation.total_tests - validation.passed_count} 个测试"
            )
        except Exception as e:
            return RefineOutput(
                success=False,
                data=None,
                message=f"优化代码失败：{str(e)}"
            )

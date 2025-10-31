from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from tools.base import Tool, ToolInput, ToolOutput
from tools.spec_tool import FunctionSpec
from core import CodeExecutor, ExecutionStatus
from cognitive.line_effectiveness_validator import LineEffectivenessValidator


class ValidateInput(ToolInput):
    """验证代码的输入"""
    code: str = Field(description="要验证的代码", min_length=1)
    spec: FunctionSpec = Field(description="函数规范")


class TestResult(BaseModel):
    """单个测试结果"""
    test_name: str = Field(description="测试名称")
    passed: bool = Field(description="是否通过")
    input_values: Dict[str, Any] = Field(description="输入值")
    expected_output: Any = Field(description="期望输出")
    actual_output: Optional[Any] = Field(default=None, description="实际输出")
    error: Optional[str] = Field(default=None, description="错误信息")

    class Config:
        """Pydantic配置"""
        extra = "forbid"


class ValidationResult(BaseModel):
    """验证结果"""
    is_valid: bool = Field(description="是否通过所有测试")
    total_tests: int = Field(description="总测试数")
    passed_count: int = Field(description="通过的测试数")
    test_results: List[TestResult] = Field(description="详细测试结果")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")

    # 新增：行有效性检查结果
    line_effectiveness_score: Optional[float] = Field(default=None, description="代码行有效性评分 (0-1)")
    line_effectiveness_analysis: Optional[Dict[str, Any]] = Field(default=None, description="行有效性分析详情")
    has_redundant_code: bool = Field(default=False, description="是否存在冗余代码")

    class Config:
        """Pydantic配置"""
        extra = "forbid"


class ValidateTool(Tool):
    """代码验证工具

    执行代码并根据规范验证其正确性，返回详细的测试结果。
    """

    name = "validate_code"
    description = "执行代码并根据规范验证其正确性，返回详细的测试结果"
    input_schema = ValidateInput

    def __init__(self):
        super().__init__()
        self.executor = CodeExecutor(timeout=30.0, enable_security=True)
        self.line_validator = LineEffectivenessValidator()

    def _execute_impl(self, input_data: ValidateInput) -> ToolOutput:
        """验证代码"""
        spec = input_data.spec
        code = input_data.code

        if not spec.examples:
            return ToolOutput.warning_result(
                data=ValidationResult(
                    is_valid=True,
                    total_tests=0,
                    passed_count=0,
                    test_results=[],
                    suggestions=["规范中没有测试用例，无法验证代码正确性"]
                ),
                message="没有测试用例可供验证",
                code_length=len(code),
                function_name=spec.name
            )

        test_results = []

        # 基于规范中的examples生成测试
        for idx, example in enumerate(spec.examples):
            result = self._run_single_test(
                code=code,
                func_name=spec.name,
                test_name=f"Example_{idx+1}",
                inputs=example.inputs,
                expected_output=example.expected_output
            )
            test_results.append(result)

        # 统计结果
        passed_count = sum(1 for r in test_results if r.passed)
        total_tests = len(test_results)
        is_valid = passed_count == total_tests

        # 生成改进建议
        suggestions = self._generate_suggestions(test_results, spec)

        # 【新增】执行行有效性检查
        line_effectiveness_report = self.line_validator.analyze_code(code, spec.purpose)
        line_effectiveness_suggestions = self.line_validator.suggest_optimizations(line_effectiveness_report)

        validation_result = ValidationResult(
            is_valid=is_valid,
            total_tests=total_tests,
            passed_count=passed_count,
            test_results=test_results,
            suggestions=suggestions,
            # 【新增】行有效性检查结果
            line_effectiveness_score=line_effectiveness_report.effectiveness_score,
            line_effectiveness_analysis={
                "total_lines": line_effectiveness_report.total_lines,
                "essential_lines": line_effectiveness_report.essential_lines,
                "important_lines": line_effectiveness_report.important_lines,
                "optional_lines": line_effectiveness_report.optional_lines,
                "redundant_lines": line_effectiveness_report.redundant_lines,
                "unused_lines": line_effectiveness_report.unused_lines,
            },
            has_redundant_code=(line_effectiveness_report.redundant_lines > 0 or
                               line_effectiveness_report.unused_lines > 0)
        )

        # 添加行有效性建议到建议列表
        if line_effectiveness_suggestions:
            suggestions.append("\n📊 行有效性优化建议:")
            suggestions.extend(line_effectiveness_suggestions)

        if is_valid:
            return ToolOutput.success_result(
                data=validation_result,
                message=f"所有测试通过: {passed_count}/{total_tests}，行有效性评分: {line_effectiveness_report.effectiveness_score:.2f}/1.0",
                function_name=spec.name,
                test_count=total_tests,
                effectiveness_score=line_effectiveness_report.effectiveness_score
            )
        else:
            return ToolOutput.warning_result(
                data=validation_result,
                message=f"部分测试失败: {passed_count}/{total_tests}",
                function_name=spec.name,
                failed_tests=total_tests - passed_count
            )

    def _run_single_test(
        self,
        code: str,
        func_name: str,
        test_name: str,
        inputs: Dict[str, Any],
        expected_output: Any
    ) -> TestResult:
        """运行单个测试"""
        # 构建测试代码
        try:
            args_str = ", ".join([f"{k}={repr(v)}" for k, v in inputs.items()])
            test_code = f"""
{code}

# 运行测试
try:
    result = {func_name}({args_str})
    print("RESULT:", repr(result))
except Exception as e:
    print("ERROR:", str(e))
    print("ERROR_TYPE:", type(e).__name__)
"""

            exec_result = self.executor.run(test_code)

            if exec_result.status == ExecutionStatus.SUCCESS:
                # 解析输出
                output = exec_result.stdout.strip()

                if output.startswith("RESULT:"):
                    actual_output_str = output.replace("RESULT:", "").strip()
                    try:
                        actual_output = eval(actual_output_str)
                        passed = actual_output == expected_output

                        return TestResult(
                            test_name=test_name,
                            passed=passed,
                            input_values=inputs,
                            expected_output=expected_output,
                            actual_output=actual_output,
                            error=None if passed else f"期望 {expected_output}, 实际 {actual_output}"
                        )
                    except Exception as e:
                        return TestResult(
                            test_name=test_name,
                            passed=False,
                            input_values=inputs,
                            expected_output=expected_output,
                            error=f"无法解析输出: {actual_output_str}"
                        )
                elif "ERROR:" in output:
                    error_lines = output.split('\n')
                    error_msg = ""
                    for line in error_lines:
                        if line.startswith("ERROR:"):
                            error_msg = line.replace("ERROR:", "").strip()
                            break

                    return TestResult(
                        test_name=test_name,
                        passed=False,
                        input_values=inputs,
                        expected_output=expected_output,
                        error=f"运行时异常: {error_msg}"
                    )
                else:
                    return TestResult(
                        test_name=test_name,
                        passed=False,
                        input_values=inputs,
                        expected_output=expected_output,
                        error="无法解析函数输出"
                    )
            else:
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    input_values=inputs,
                    expected_output=expected_output,
                    error=exec_result.error or "代码执行失败"
                )

        except Exception as e:
            return TestResult(
                test_name=test_name,
                passed=False,
                input_values=inputs,
                expected_output=expected_output,
                error=f"测试执行异常: {str(e)}"
            )

    def _generate_suggestions(
        self,
        test_results: List[TestResult],
        spec: FunctionSpec
    ) -> List[str]:
        """根据测试结果生成改进建议"""
        suggestions = []
        failed_tests = [r for r in test_results if not r.passed]

        if not failed_tests:
            return ["[SUCCESS] All tests passed, code meets requirements!"]

        # 分析失败原因
        error_types = {}
        for result in failed_tests:
            if result.error:
                if "期望" in result.error and "实际" in result.error:
                    error_types["output_mismatch"] = error_types.get("output_mismatch", 0) + 1
                elif "异常" in result.error or "Exception" in result.error:
                    error_types["runtime_error"] = error_types.get("runtime_error", 0) + 1
                else:
                    error_types["other"] = error_types.get("other", 0) + 1

        # 生成具体建议
        if error_types.get("output_mismatch", 0) > 0:
            suggestions.append("[CHECK] Review function logic to ensure return values match expectations")

        if error_types.get("runtime_error", 0) > 0:
            suggestions.append("[HANDLE] Handle runtime exceptions and check edge cases")

        # 检查是否处理了所有边界情况
        if spec.edge_cases:
            suggestions.append(f"[EDGE] Ensure handling of these edge cases: {', '.join(spec.edge_cases[:2])}")

        return suggestions

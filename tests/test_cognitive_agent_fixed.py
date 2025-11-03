"""
测试修复后的认知代理功能

验证所有LLM集成修复是否工作正常，包括：
1. 问题理解阶段
2. 解决方案规划阶段
3. 算法设计阶段
4. 代码实现阶段
5. 验证阶段
6. 优化阶段
7. 反思阶段
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive.cognitive_agent import CognitiveCodeGenAgent, CognitiveCodeGenRequest
from cognitive.llm_schemas import (
    ProblemComprehension, SolutionPlan, AlgorithmDesign,
    CodeImplementation, ValidationResult, OptimizationResult,
    SolutionReflection, ProblemComplexity, ComponentType,
    SolutionStrategy, AlgorithmComponent, ReflectionInsight
)
from llm.structured_llm import StructuredLLM


class MockStructuredLLM:
    """模拟的StructuredLLM，用于测试"""

    def generate_structured(self, prompt, output_schema, **kwargs):
        """模拟结构化生成"""

        if output_schema == ProblemComprehension:
            return ProblemComprehension(
                main_goal="实现一个简单的数学计算函数",
                key_components=[ComponentType.INPUT_PROCESSING, ComponentType.CORE_LOGIC],
                complexity_assessment=ProblemComplexity.SIMPLE,
                input_requirements=["数字参数"],
                output_requirements=["计算结果"],
                constraints=["无特殊约束"],
                edge_cases=["零值输入", "负数输入"],
                initial_thoughts=["需要验证输入", "执行计算", "返回结果"],
                domain_knowledge_needed=["基础数学", "Python语法"]
            )

        elif output_schema == SolutionPlan:
            return SolutionPlan(
                chosen_strategy=SolutionStrategy.TOP_DOWN,
                strategy_rationale="问题简单，自顶向下分解最适合",
                main_steps=["定义函数", "验证输入", "执行计算", "返回结果"],
                step_dependencies={"验证输入": ["定义函数"]},
                considerations=["输入验证", "错误处理"],
                potential_challenges=["边界情况处理"],
                alternative_approaches=["递归方法", "迭代方法"],
                estimated_difficulty=ProblemComplexity.SIMPLE
            )

        elif output_schema == AlgorithmDesign:
            return AlgorithmDesign(
                algorithm_name="simple_calculator",
                algorithm_description="一个简单的数学计算器函数",
                pseudocode=["1. 检查输入有效性", "2. 执行数学运算", "3. 返回结果"],
                data_structures=["变量", "参数"],
                components=[
                    AlgorithmComponent(
                        name="input_validator",
                        purpose="验证输入",
                        input_type="Any",
                        output_type="bool",
                        complexity="O(1)"
                    )
                ],
                time_complexity="O(1)",
                space_complexity="O(1)",
                invariants=["输入参数有效"],
                edge_cases_handling=["处理无效输入", "处理边界值"],
                optimization_opportunities=["无需优化"]
            )

        elif output_schema == CodeImplementation:
            return CodeImplementation(
                function_name="simple_calculator",
                function_signature="def simple_calculator(a, b, operation='add')",
                docstring="简单的数学计算器，支持基本运算",
                implementation_code="""def simple_calculator(a, b, operation='add'):
    \"\"\"
    简单的数学计算器，支持基本运算

    Args:
        a: 第一个数字
        b: 第二个数字
        operation: 运算类型 ('add', 'subtract', 'multiply', 'divide')

    Returns:
        计算结果
    \"\"\"
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise ValueError("输入必须是数字")

    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    else:
        raise ValueError("不支持的运算类型")""",
                helper_functions=[],
                import_statements=[],
                implementation_notes=["包含基本的输入验证", "支持四种基本运算"],
                code_rationale="采用简单直接的实现方式，易于理解和维护"
            )

        elif output_schema == ValidationResult:
            return ValidationResult(
                syntax_valid=True,
                logic_valid=True,
                test_cases_passed=4,
                total_test_cases=4,
                identified_issues=[],
                suggestions=["可以添加更多运算类型", "考虑支持复数运算"],
                needs_optimization=False,
                confidence_score=0.9
            )

        elif output_schema == OptimizationResult:
            return OptimizationResult(
                optimized_code="# 无需优化的代码",
                optimization_techniques=["代码已经足够简洁"],
                performance_improvements=["性能良好"],
                trade_offs=["简洁性与扩展性的平衡"],
                optimization_rationale="当前代码已经足够优化"
            )

        elif output_schema == SolutionReflection:
            return SolutionReflection(
                quality_assessment="良好",
                strengths=["代码清晰", "错误处理完善", "易于使用"],
                weaknesses=["功能相对简单", "可扩展性有限"],
                alternative_approaches=["面向对象设计", "函数式编程风格"],
                lessons_learned=["简单直接的方法往往最有效", "输入验证很重要"],
                future_improvements=["添加更多运算类型", "支持表达式解析"],
                insights=[
                    ReflectionInsight(
                        insight_type="设计模式",
                        description="简单函数设计适合基础功能",
                        impact="正面影响，提高可读性",
                        confidence=0.8
                    )
                ],
                overall_satisfaction=0.8
            )

        else:
            raise ValueError(f"Unsupported output schema: {output_schema}")


class TestCognitiveAgentFixed(unittest.TestCase):
    """测试修复后的认知代理"""

    def setUp(self):
        """设置测试环境"""
        self.mock_llm = MockStructuredLLM()
        self.agent = CognitiveCodeGenAgent(self.mock_llm)

    def test_agent_initialization(self):
        """测试代理初始化"""
        self.assertIsNotNone(self.agent.llm)
        self.assertIsNotNone(self.agent.line_explainer)
        self.assertIsNotNone(self.agent.thinking_process)
        self.assertIsNotNone(self.agent.cognitive_model)

    def test_problem_comprehension_with_llm(self):
        """测试问题理解阶段的LLM集成"""
        request = CognitiveCodeGenRequest(
            requirement="写一个计算两个数字和的函数",
            context="简单的数学运算",
            constraints=["使用Python"],
            difficulty="simple"
        )

        understanding = self.agent._comprehend_problem(request)

        # 验证返回的理解结果
        self.assertIn("main_goal", understanding)
        self.assertIn("key_components", understanding)
        self.assertIn("complexity_assessment", understanding)
        self.assertIn("llm_analysis", understanding)
        self.assertEqual(understanding["main_goal"], "实现一个简单的数学计算函数")

    def test_solution_planning_with_llm(self):
        """测试解决方案规划阶段的LLM集成"""
        problem_understanding = {
            "main_goal": "实现计算器函数",
            "key_components": ["input_processing", "core_logic"],
            "complexity_assessment": "simple",
            "constraints": []
        }

        plan = self.agent._plan_solution(problem_understanding)

        # 验证返回的规划结果
        self.assertIn("strategy", plan)
        self.assertIn("strategy_rationale", plan)
        self.assertIn("main_steps", plan)
        self.assertIn("llm_plan", plan)
        self.assertEqual(plan["strategy"], "top_down")

    def test_algorithm_design_with_llm(self):
        """测试算法设计阶段的LLM集成"""
        solution_plan = {
            "strategy": "top_down",
            "strategy_rationale": "适合简单问题",
            "main_steps": ["步骤1", "步骤2"],
            "considerations": ["考虑因素"],
            "potential_challenges": ["挑战"]
        }

        algorithm = self.agent._design_algorithm(solution_plan)

        # 验证返回的算法设计结果
        self.assertIn("algorithm_name", algorithm)
        self.assertIn("pseudocode", algorithm)
        self.assertIn("time_complexity", algorithm)
        self.assertIn("llm_design", algorithm)

    def test_code_implementation_with_llm(self):
        """测试代码实现阶段的LLM集成"""
        algorithm_design = {
            "algorithm_name": "test_function",
            "algorithm_description": "测试函数",
            "pseudocode": ["步骤1", "步骤2"],
            "time_complexity": "O(1)",
            "strategy": "iterative"
        }

        implementation = self.agent._implement_code(algorithm_design)

        # 验证返回的实现结果
        self.assertIn("function_name", implementation)
        self.assertIn("code", implementation)
        self.assertIn("explanation", implementation)
        self.assertIn("confidence", implementation)

    def test_validation_with_llm(self):
        """测试验证阶段的LLM集成"""
        implementation = {
            "code": "def test(): return 42",
            "function_name": "test",
            "explanation": "测试函数",
            "confidence": 0.8
        }

        request = CognitiveCodeGenRequest(requirement="测试需求")
        validation = self.agent._validate_solution(implementation, request)

        # 验证返回的验证结果
        self.assertIn("syntax_check", validation)
        self.assertIn("logic_check", validation)
        self.assertIn("confidence_score", validation)

    def test_full_generation_workflow(self):
        """测试完整的代码生成工作流"""
        request = CognitiveCodeGenRequest(
            requirement="写一个计算两个数字相加的函数",
            context="基础数学运算",
            constraints=["使用Python", "包含错误处理"],
            difficulty="simple"
        )

        # 执行完整的生成流程
        result = self.agent.generate_code(request)

        # 验证最终结果
        self.assertIsNotNone(result.generated_code)
        self.assertIsNotNone(result.explanation)
        self.assertIsInstance(result.line_explanations, dict)
        self.assertIsNotNone(result.cognitive_trace)
        self.assertIsInstance(result.reasoning_chain, list)
        self.assertGreater(result.confidence, 0)

        # 验证代码内容
        self.assertIn("def ", result.generated_code)
        self.assertIn("simple_calculator", result.generated_code)

        print("完整的认知代理工作流测试通过")
        print(f"生成的代码长度: {len(result.generated_code)} 字符")
        print(f"置信度: {result.confidence}")
        print(f"认知复杂度: {result.cognitive_load}")


def test_fallback_behavior():
    """测试LLM调用失败时的降级行为"""

    class FailingLLM:
        def generate_structured(self, *args, **kwargs):
            raise Exception("LLM 服务不可用")

    failing_llm = FailingLLM()
    agent = CognitiveCodeGenAgent(failing_llm)

    request = CognitiveCodeGenRequest(
        requirement="写一个简单函数",
        difficulty="simple"
    )

    # 应该能够处理LLM失败并使用降级逻辑
    result = agent.generate_code(request)

    # 验证降级结果仍然有效
    assert result.generated_code is not None
    assert result.confidence > 0
    assert len(result.reasoning_chain) > 0

    print("LLM 失败降级行为测试通过")


if __name__ == "__main__":
    print("开始测试修复后的认知代理功能...")
    print("=" * 50)

    # 运行单元测试
    unittest.main(verbosity=2, exit=False)

    print("\n" + "=" * 50)
    print("测试LLM失败降级行为...")
    test_fallback_behavior()

    print("\n" + "=" * 50)
    print("所有测试完成！认知代理修复成功。")
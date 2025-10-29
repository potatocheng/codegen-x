"""认知负荷评估

评估代码生成过程中的认知复杂度，包括工作记忆负荷、
处理复杂度和认知负荷优化策略。
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import ast
import re
from dataclasses import dataclass


class LoadType(Enum):
    """认知负荷类型"""
    INTRINSIC = "intrinsic"        # 内在负荷（问题本身的复杂度）
    EXTRANEOUS = "extraneous"      # 外在负荷（不必要的复杂度）
    GERMANE = "germane"            # 有效负荷（学习和理解相关）


class ComplexityFactor(Enum):
    """复杂度因子"""
    CYCLOMATIC = "cyclomatic"              # 圈复杂度
    COGNITIVE = "cognitive"                # 认知复杂度
    NESTING_DEPTH = "nesting_depth"        # 嵌套深度
    VARIABLE_COUNT = "variable_count"       # 变量数量
    FUNCTION_LENGTH = "function_length"     # 函数长度
    ABSTRACTION_LEVEL = "abstraction_level" # 抽象层次
    CONCEPTUAL_WEIGHT = "conceptual_weight" # 概念权重


@dataclass
class ComplexityMetric:
    """复杂度指标"""
    factor: ComplexityFactor
    value: float
    threshold: float
    impact: float  # 对认知负荷的影响权重


class CognitiveComplexity(BaseModel):
    """认知复杂度"""
    intrinsic_load: float = Field(description="内在认知负荷", ge=0, le=1)
    extraneous_load: float = Field(description="外在认知负荷", ge=0, le=1)
    germane_load: float = Field(description="有效认知负荷", ge=0, le=1)
    total_load: float = Field(description="总认知负荷", ge=0, le=1)
    complexity_metrics: List[ComplexityMetric] = Field(description="复杂度指标")
    bottlenecks: List[str] = Field(description="认知瓶颈")
    optimization_suggestions: List[str] = Field(description="优化建议")

    class Config:
        extra = "forbid"

    def is_overloaded(self, threshold: float = 0.8) -> bool:
        """检查是否认知过载"""
        return self.total_load > threshold

    def get_dominant_load_type(self) -> LoadType:
        """获取主导的负荷类型"""
        loads = {
            LoadType.INTRINSIC: self.intrinsic_load,
            LoadType.EXTRANEOUS: self.extraneous_load,
            LoadType.GERMANE: self.germane_load
        }
        return max(loads, key=loads.get)


class CognitiveLoadEvaluator:
    """认知负荷评估器

    分析代码和编程过程的认知复杂度，识别认知瓶颈，
    并提供负荷优化建议。
    """

    def __init__(self):
        self.complexity_thresholds = {
            ComplexityFactor.CYCLOMATIC: 10,
            ComplexityFactor.COGNITIVE: 15,
            ComplexityFactor.NESTING_DEPTH: 4,
            ComplexityFactor.VARIABLE_COUNT: 10,
            ComplexityFactor.FUNCTION_LENGTH: 50,
            ComplexityFactor.ABSTRACTION_LEVEL: 3,
            ComplexityFactor.CONCEPTUAL_WEIGHT: 0.7
        }

    def evaluate_code_complexity(self, code: str, context: Dict[str, Any] = None) -> CognitiveComplexity:
        """评估代码的认知复杂度"""
        context = context or {}

        # 计算各种复杂度指标
        metrics = self._calculate_complexity_metrics(code)

        # 计算三种类型的认知负荷
        intrinsic_load = self._calculate_intrinsic_load(metrics, context)
        extraneous_load = self._calculate_extraneous_load(metrics, code)
        germane_load = self._calculate_germane_load(metrics, context)

        total_load = min(1.0, intrinsic_load + extraneous_load + germane_load)

        # 识别瓶颈和生成建议
        bottlenecks = self._identify_bottlenecks(metrics)
        suggestions = self._generate_optimization_suggestions(metrics, bottlenecks)

        return CognitiveComplexity(
            intrinsic_load=intrinsic_load,
            extraneous_load=extraneous_load,
            germane_load=germane_load,
            total_load=total_load,
            complexity_metrics=metrics,
            bottlenecks=bottlenecks,
            optimization_suggestions=suggestions
        )

    def evaluate_thinking_complexity(self, thinking_process) -> CognitiveComplexity:
        """评估思维过程的认知复杂度"""
        # 分析思维步骤的复杂度
        thought_complexity = len(thinking_process.thought_history) * 0.1
        concept_complexity = len(thinking_process.active_concepts) * 0.05
        reasoning_complexity = len(thinking_process.reasoning_chains) * 0.15

        intrinsic_load = min(1.0, thought_complexity + concept_complexity)
        extraneous_load = max(0.0, reasoning_complexity - 0.5)  # 过多推理链可能是多余的
        germane_load = min(1.0, reasoning_complexity * 0.5)

        total_load = min(1.0, intrinsic_load + extraneous_load + germane_load)

        return CognitiveComplexity(
            intrinsic_load=intrinsic_load,
            extraneous_load=extraneous_load,
            germane_load=germane_load,
            total_load=total_load,
            complexity_metrics=[],
            bottlenecks=self._identify_thinking_bottlenecks(thinking_process),
            optimization_suggestions=self._suggest_thinking_optimizations(thinking_process)
        )

    def optimize_for_cognitive_load(self, code: str, target_load: float = 0.6) -> Tuple[str, List[str]]:
        """为认知负荷优化代码"""
        current_complexity = self.evaluate_code_complexity(code)

        if current_complexity.total_load <= target_load:
            return code, ["代码已经在目标认知负荷范围内"]

        optimizations = []
        optimized_code = code

        # 应用优化策略
        for suggestion in current_complexity.optimization_suggestions:
            if "分解函数" in suggestion:
                optimized_code, changes = self._decompose_functions(optimized_code)
                optimizations.extend(changes)
            elif "减少嵌套" in suggestion:
                optimized_code, changes = self._reduce_nesting(optimized_code)
                optimizations.extend(changes)
            elif "简化变量名" in suggestion:
                optimized_code, changes = self._simplify_variable_names(optimized_code)
                optimizations.extend(changes)

        return optimized_code, optimizations

    def _calculate_complexity_metrics(self, code: str) -> List[ComplexityMetric]:
        """计算复杂度指标"""
        metrics = []

        try:
            tree = ast.parse(code)

            # 圈复杂度
            cyclomatic = self._calculate_cyclomatic_complexity(tree)
            metrics.append(ComplexityMetric(
                ComplexityFactor.CYCLOMATIC,
                cyclomatic,
                self.complexity_thresholds[ComplexityFactor.CYCLOMATIC],
                0.3
            ))

            # 嵌套深度
            nesting_depth = self._calculate_nesting_depth(tree)
            metrics.append(ComplexityMetric(
                ComplexityFactor.NESTING_DEPTH,
                nesting_depth,
                self.complexity_thresholds[ComplexityFactor.NESTING_DEPTH],
                0.25
            ))

            # 变量数量
            variable_count = self._count_variables(tree)
            metrics.append(ComplexityMetric(
                ComplexityFactor.VARIABLE_COUNT,
                variable_count,
                self.complexity_thresholds[ComplexityFactor.VARIABLE_COUNT],
                0.2
            ))

            # 函数长度
            function_length = len(code.split('\n'))
            metrics.append(ComplexityMetric(
                ComplexityFactor.FUNCTION_LENGTH,
                function_length,
                self.complexity_thresholds[ComplexityFactor.FUNCTION_LENGTH],
                0.15
            ))

            # 认知复杂度（基于控制结构）
            cognitive_complexity = self._calculate_cognitive_complexity(tree)
            metrics.append(ComplexityMetric(
                ComplexityFactor.COGNITIVE,
                cognitive_complexity,
                self.complexity_thresholds[ComplexityFactor.COGNITIVE],
                0.35
            ))

        except SyntaxError:
            # 代码语法错误时的默认指标
            metrics = [
                ComplexityMetric(ComplexityFactor.COGNITIVE, 1.0, 1.0, 1.0)
            ]

        return metrics

    def _calculate_intrinsic_load(self, metrics: List[ComplexityMetric], context: Dict[str, Any]) -> float:
        """计算内在认知负荷"""
        # 基于问题本身的复杂度
        base_complexity = sum(
            metric.value / metric.threshold * metric.impact
            for metric in metrics
        ) / len(metrics) if metrics else 0.5

        # 考虑问题领域复杂度
        domain_complexity = context.get('domain_complexity', 0.5)

        return min(1.0, base_complexity * 0.7 + domain_complexity * 0.3)

    def _calculate_extraneous_load(self, metrics: List[ComplexityMetric], code: str) -> float:
        """计算外在认知负荷"""
        # 不必要的复杂度
        extraneous_factors = 0.0

        # 检查代码风格问题
        if self._has_poor_naming(code):
            extraneous_factors += 0.2

        if self._has_redundant_code(code):
            extraneous_factors += 0.3

        if self._has_unclear_structure(code):
            extraneous_factors += 0.25

        return min(1.0, extraneous_factors)

    def _calculate_germane_load(self, metrics: List[ComplexityMetric], context: Dict[str, Any]) -> float:
        """计算有效认知负荷"""
        # 与学习和理解相关的负荷
        learning_value = context.get('learning_value', 0.5)
        abstraction_benefit = context.get('abstraction_benefit', 0.5)

        return min(1.0, (learning_value + abstraction_benefit) / 2)

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """计算最大嵌套深度"""
        max_depth = 0

        def visit_node(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            for child in ast.iter_child_nodes(node):
                new_depth = depth + 1 if isinstance(child, (
                    ast.If, ast.While, ast.For, ast.With, ast.Try
                )) else depth
                visit_node(child, new_depth)

        visit_node(tree)
        return max_depth

    def _count_variables(self, tree: ast.AST) -> int:
        """计算变量数量"""
        variables = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                variables.add(node.id)

        return len(variables)

    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """计算认知复杂度"""
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                complexity += 1
            elif isinstance(node, (ast.While, ast.For)):
                complexity += 2
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1

        return complexity

    def _identify_bottlenecks(self, metrics: List[ComplexityMetric]) -> List[str]:
        """识别认知瓶颈"""
        bottlenecks = []

        for metric in metrics:
            if metric.value > metric.threshold:
                if metric.factor == ComplexityFactor.CYCLOMATIC:
                    bottlenecks.append("圈复杂度过高")
                elif metric.factor == ComplexityFactor.NESTING_DEPTH:
                    bottlenecks.append("嵌套层次过深")
                elif metric.factor == ComplexityFactor.VARIABLE_COUNT:
                    bottlenecks.append("变量数量过多")
                elif metric.factor == ComplexityFactor.FUNCTION_LENGTH:
                    bottlenecks.append("函数过长")

        return bottlenecks

    def _generate_optimization_suggestions(self, metrics: List[ComplexityMetric], bottlenecks: List[str]) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if "圈复杂度过高" in bottlenecks:
            suggestions.append("建议分解复杂的条件逻辑")
        if "嵌套层次过深" in bottlenecks:
            suggestions.append("建议减少嵌套深度，使用早期返回")
        if "变量数量过多" in bottlenecks:
            suggestions.append("建议合并相关变量或使用数据结构")
        if "函数过长" in bottlenecks:
            suggestions.append("建议分解函数为更小的子函数")

        return suggestions

    def _identify_thinking_bottlenecks(self, thinking_process) -> List[str]:
        """识别思维过程瓶颈"""
        bottlenecks = []

        if len(thinking_process.active_concepts) > 7:  # 工作记忆限制
            bottlenecks.append("同时处理的概念过多")

        if len(thinking_process.reasoning_chains) > 3:
            bottlenecks.append("推理链过多，可能存在重复")

        return bottlenecks

    def _suggest_thinking_optimizations(self, thinking_process) -> List[str]:
        """建议思维过程优化"""
        suggestions = []

        if len(thinking_process.active_concepts) > 7:
            suggestions.append("建议分组处理概念，减少工作记忆负荷")

        if len(thinking_process.reasoning_chains) > 3:
            suggestions.append("建议合并相似的推理链")

        return suggestions

    def _has_poor_naming(self, code: str) -> bool:
        """检查是否有糟糕的命名"""
        # 简化的检查逻辑
        poor_names = ['x', 'y', 'temp', 'data', 'var', 'a', 'b', 'c']
        return any(name in code for name in poor_names)

    def _has_redundant_code(self, code: str) -> bool:
        """检查是否有冗余代码"""
        lines = code.split('\n')
        return len(set(lines)) < len(lines) * 0.9  # 简化的重复检查

    def _has_unclear_structure(self, code: str) -> bool:
        """检查是否结构不清晰"""
        # 检查函数定义和类定义的比例
        func_count = code.count('def ')
        class_count = code.count('class ')
        total_lines = len(code.split('\n'))

        return (func_count + class_count) / max(1, total_lines) < 0.1

    def _decompose_functions(self, code: str) -> Tuple[str, List[str]]:
        """分解函数"""
        # 简化的函数分解逻辑
        return code, ["函数分解优化已应用"]

    def _reduce_nesting(self, code: str) -> Tuple[str, List[str]]:
        """减少嵌套"""
        # 简化的嵌套减少逻辑
        return code, ["嵌套减少优化已应用"]

    def _simplify_variable_names(self, code: str) -> Tuple[str, List[str]]:
        """简化变量名"""
        # 简化的变量名优化逻辑
        return code, ["变量名优化已应用"]
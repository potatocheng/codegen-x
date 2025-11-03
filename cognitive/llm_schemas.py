"""
LLM 结构化输出的 Pydantic 模型定义

这些模型用于确保 LLM 返回符合预期格式的结构化数据，
避免 JSON 解析错误并提供类型安全。
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProblemComplexity(Enum):
    """问题复杂度等级"""
    TRIVIAL = "trivial"      # 平凡问题
    SIMPLE = "simple"        # 简单问题
    MEDIUM = "medium"        # 中等问题
    COMPLEX = "complex"      # 复杂问题
    VERY_COMPLEX = "very_complex"  # 非常复杂


class ComponentType(Enum):
    """组件类型"""
    INPUT_PROCESSING = "input_processing"
    CORE_LOGIC = "core_logic"
    OUTPUT_FORMATTING = "output_formatting"
    ERROR_HANDLING = "error_handling"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"


class ProblemComprehension(BaseModel):
    """问题理解的结构化输出"""
    main_goal: str = Field(description="问题的主要目标")
    key_components: List[ComponentType] = Field(description="关键组件类型")
    complexity_assessment: ProblemComplexity = Field(description="复杂度评估")
    input_requirements: List[str] = Field(description="输入需求")
    output_requirements: List[str] = Field(description="输出需求")
    constraints: List[str] = Field(description="约束条件")
    edge_cases: List[str] = Field(description="边界情况")
    initial_thoughts: List[str] = Field(description="初步想法")
    domain_knowledge_needed: List[str] = Field(description="需要的领域知识")

    class Config:
        extra = "forbid"


class SolutionStrategy(Enum):
    """解决方案策略"""
    TOP_DOWN = "top_down"
    BOTTOM_UP = "bottom_up"
    DIVIDE_CONQUER = "divide_conquer"
    ITERATIVE = "iterative"
    RECURSIVE = "recursive"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    GREEDY = "greedy"
    BACKTRACKING = "backtracking"


class SolutionPlan(BaseModel):
    """解决方案规划的结构化输出"""
    chosen_strategy: SolutionStrategy = Field(description="选择的策略")
    strategy_rationale: str = Field(description="策略选择理由")
    main_steps: List[str] = Field(description="主要步骤")
    step_dependencies: Dict[str, List[str]] = Field(description="步骤依赖关系")
    considerations: List[str] = Field(description="考虑因素")
    potential_challenges: List[str] = Field(description="潜在挑战")
    alternative_approaches: List[str] = Field(description="备选方案")
    estimated_difficulty: ProblemComplexity = Field(description="估计难度")

    class Config:
        extra = "forbid"


class AlgorithmComponent(BaseModel):
    """算法组件"""
    name: str = Field(description="组件名称")
    purpose: str = Field(description="组件用途")
    input_type: str = Field(description="输入类型")
    output_type: str = Field(description="输出类型")
    complexity: str = Field(description="复杂度")


class AlgorithmDesign(BaseModel):
    """算法设计的结构化输出"""
    algorithm_name: str = Field(description="算法名称")
    algorithm_description: str = Field(description="算法描述")
    pseudocode: List[str] = Field(description="伪代码步骤")
    data_structures: List[str] = Field(description="所需数据结构")
    components: List[AlgorithmComponent] = Field(description="算法组件")
    time_complexity: str = Field(description="时间复杂度")
    space_complexity: str = Field(description="空间复杂度")
    invariants: List[str] = Field(description="循环不变量")
    edge_cases_handling: List[str] = Field(description="边界情况处理")
    optimization_opportunities: List[str] = Field(description="优化机会")

    class Config:
        extra = "forbid"


class CodeImplementation(BaseModel):
    """代码实现的结构化输出"""
    function_name: str = Field(description="函数名称")
    function_signature: str = Field(description="函数签名")
    docstring: str = Field(description="文档字符串")
    implementation_code: str = Field(description="实现代码")
    helper_functions: List[str] = Field(description="辅助函数代码")
    import_statements: List[str] = Field(description="导入语句")
    implementation_notes: List[str] = Field(description="实现说明")
    code_rationale: str = Field(description="代码设计理由")

    class Config:
        extra = "forbid"


class ValidationResult(BaseModel):
    """验证结果的结构化输出"""
    syntax_valid: bool = Field(description="语法是否有效")
    logic_valid: bool = Field(description="逻辑是否有效")
    test_cases_passed: int = Field(description="通过的测试用例数")
    total_test_cases: int = Field(description="总测试用例数")
    identified_issues: List[str] = Field(description="发现的问题")
    suggestions: List[str] = Field(description="改进建议")
    needs_optimization: bool = Field(description="是否需要优化")
    confidence_score: float = Field(description="置信度分数", ge=0, le=1)

    class Config:
        extra = "forbid"


class OptimizationResult(BaseModel):
    """优化结果的结构化输出"""
    optimized_code: str = Field(description="优化后的代码")
    optimization_techniques: List[str] = Field(description="使用的优化技术")
    performance_improvements: List[str] = Field(description="性能改进")
    trade_offs: List[str] = Field(description="权衡考虑")
    optimization_rationale: str = Field(description="优化理由")

    class Config:
        extra = "forbid"


class ReflectionInsight(BaseModel):
    """反思洞察"""
    insight_type: str = Field(description="洞察类型")
    description: str = Field(description="洞察描述")
    impact: str = Field(description="影响")
    confidence: float = Field(description="置信度", ge=0, le=1)


class SolutionReflection(BaseModel):
    """解决方案反思的结构化输出"""
    quality_assessment: str = Field(description="质量评估")
    strengths: List[str] = Field(description="优势")
    weaknesses: List[str] = Field(description="劣势")
    alternative_approaches: List[str] = Field(description="备选方案")
    lessons_learned: List[str] = Field(description="经验教训")
    future_improvements: List[str] = Field(description="未来改进")
    insights: List[ReflectionInsight] = Field(description="反思洞察")
    overall_satisfaction: float = Field(description="总体满意度", ge=0, le=1)

    class Config:
        extra = "forbid"
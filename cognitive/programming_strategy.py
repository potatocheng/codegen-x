"""编程策略选择

基于问题特征和认知状态，选择最适合的编程策略和方法。
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class StrategyType(Enum):
    """编程策略类型"""
    TOP_DOWN = "top_down"                    # 自顶向下
    BOTTOM_UP = "bottom_up"                  # 自底向上
    DIVIDE_CONQUER = "divide_conquer"        # 分而治之
    INCREMENTAL = "incremental"              # 增量式
    PROTOTYPE = "prototype"                  # 原型法
    PATTERN_BASED = "pattern_based"          # 基于模式
    TEST_DRIVEN = "test_driven"              # 测试驱动
    REFACTOR = "refactor"                    # 重构式


class ProblemCharacteristics(BaseModel):
    """问题特征"""
    complexity_level: float = Field(description="复杂度等级 (0-1)", ge=0, le=1)
    domain_familiarity: float = Field(description="领域熟悉度 (0-1)", ge=0, le=1)
    requirements_clarity: float = Field(description="需求清晰度 (0-1)", ge=0, le=1)
    time_constraint: float = Field(description="时间约束 (0-1)", ge=0, le=1)
    quality_requirement: float = Field(description="质量要求 (0-1)", ge=0, le=1)
    innovation_need: float = Field(description="创新需求 (0-1)", ge=0, le=1)
    maintenance_importance: float = Field(description="维护重要性 (0-1)", ge=0, le=1)

    class Config:
        extra = "forbid"


@dataclass
class StrategyScore:
    """策略评分"""
    strategy: StrategyType
    score: float
    reasoning: str
    advantages: List[str]
    disadvantages: List[str]


class ProgrammingStrategy(BaseModel):
    """编程策略

    根据问题特征、认知状态和历史经验选择最优的编程策略。
    """

    selected_strategy: Optional[StrategyType] = Field(default=None, description="选择的策略")
    strategy_scores: List[StrategyScore] = Field(default_factory=list, description="策略评分")
    adaptation_rules: Dict[str, Any] = Field(default_factory=dict, description="适应性规则")
    historical_performance: Dict[StrategyType, float] = Field(default_factory=dict, description="历史表现")

    class Config:
        extra = "forbid"

    def select_strategy(self, problem_chars: ProblemCharacteristics,
                       cognitive_state, thinking_process) -> StrategyType:
        """选择最优编程策略"""

        # 评估所有策略
        self.strategy_scores = []
        for strategy in StrategyType:
            score = self._evaluate_strategy(strategy, problem_chars, cognitive_state, thinking_process)
            self.strategy_scores.append(score)

        # 选择最高分策略
        best_strategy = max(self.strategy_scores, key=lambda x: x.score)
        self.selected_strategy = best_strategy.strategy

        return self.selected_strategy

    def adapt_strategy(self, feedback: Dict[str, Any]) -> StrategyType:
        """基于反馈适应策略"""
        current_performance = feedback.get('performance', 0.5)

        # 更新历史表现
        if self.selected_strategy:
            if self.selected_strategy not in self.historical_performance:
                self.historical_performance[self.selected_strategy] = current_performance
            else:
                # 使用指数加权移动平均
                alpha = 0.3
                old_perf = self.historical_performance[self.selected_strategy]
                self.historical_performance[self.selected_strategy] = (
                    alpha * current_performance + (1 - alpha) * old_perf
                )

        # 如果当前策略表现不佳，考虑切换
        if current_performance < 0.6:
            return self._suggest_alternative_strategy(feedback)

        return self.selected_strategy

    def get_strategy_guidance(self, strategy: StrategyType) -> Dict[str, Any]:
        """获取策略指导"""
        guidance = {
            StrategyType.TOP_DOWN: {
                "approach": "从整体架构开始，逐步细化实现",
                "steps": [
                    "分析整体需求",
                    "设计高层架构",
                    "定义主要接口",
                    "实现核心功能",
                    "填充具体细节"
                ],
                "focus": "系统性思考，保持整体视角"
            },
            StrategyType.BOTTOM_UP: {
                "approach": "从基础组件开始，逐步构建复杂功能",
                "steps": [
                    "识别基础元素",
                    "实现核心工具函数",
                    "构建中层组件",
                    "组合成完整系统",
                    "优化整体架构"
                ],
                "focus": "扎实的基础，渐进式构建"
            },
            StrategyType.DIVIDE_CONQUER: {
                "approach": "将复杂问题分解为独立的子问题",
                "steps": [
                    "识别问题边界",
                    "分解为子问题",
                    "独立解决子问题",
                    "整合子问题解决方案",
                    "验证整体解决方案"
                ],
                "focus": "问题分解，并行解决"
            },
            StrategyType.INCREMENTAL: {
                "approach": "逐步增加功能，每次都有可工作的版本",
                "steps": [
                    "实现最小可用版本",
                    "添加核心功能",
                    "逐步扩展特性",
                    "持续优化改进",
                    "保持系统稳定性"
                ],
                "focus": "渐进式开发，快速反馈"
            },
            StrategyType.PROTOTYPE: {
                "approach": "快速构建原型验证想法",
                "steps": [
                    "明确核心假设",
                    "快速实现原型",
                    "验证关键功能",
                    "收集反馈意见",
                    "迭代改进或重写"
                ],
                "focus": "快速验证，降低风险"
            },
            StrategyType.PATTERN_BASED: {
                "approach": "基于已知模式和最佳实践",
                "steps": [
                    "识别问题模式",
                    "选择适用的设计模式",
                    "应用标准解决方案",
                    "适配具体需求",
                    "验证模式效果"
                ],
                "focus": "复用经验，标准化解决方案"
            },
            StrategyType.TEST_DRIVEN: {
                "approach": "先写测试，再实现功能",
                "steps": [
                    "编写失败的测试",
                    "实现最小功能使测试通过",
                    "重构改进代码",
                    "添加更多测试",
                    "持续迭代"
                ],
                "focus": "质量驱动，明确规格"
            },
            StrategyType.REFACTOR: {
                "approach": "在保持功能的前提下改进代码结构",
                "steps": [
                    "分析现有代码",
                    "识别改进机会",
                    "制定重构计划",
                    "逐步重构",
                    "验证功能完整性"
                ],
                "focus": "结构优化，质量提升"
            }
        }

        return guidance.get(strategy, {})

    def _evaluate_strategy(self, strategy: StrategyType, problem_chars: ProblemCharacteristics,
                          cognitive_state, thinking_process) -> StrategyScore:
        """评估策略适用性"""

        score = 0.0
        reasoning = []
        advantages = []
        disadvantages = []

        # 基于问题特征评估
        if strategy == StrategyType.TOP_DOWN:
            if problem_chars.complexity_level > 0.7:
                score += 0.3
                advantages.append("适合复杂问题的系统化处理")
            if problem_chars.requirements_clarity > 0.6:
                score += 0.2
                advantages.append("需求清晰时能有效指导设计")
            if problem_chars.domain_familiarity > 0.7:
                score += 0.2
                advantages.append("在熟悉领域中能快速构建架构")
            else:
                disadvantages.append("在不熟悉领域可能导致错误的顶层设计")

        elif strategy == StrategyType.BOTTOM_UP:
            if problem_chars.domain_familiarity < 0.5:
                score += 0.25
                advantages.append("在不熟悉领域中能建立扎实基础")
            if problem_chars.innovation_need > 0.6:
                score += 0.2
                advantages.append("有利于探索性开发")
            if problem_chars.time_constraint > 0.7:
                disadvantages.append("在时间紧迫时可能效率较低")

        elif strategy == StrategyType.DIVIDE_CONQUER:
            if problem_chars.complexity_level > 0.8:
                score += 0.35
                advantages.append("擅长处理超复杂问题")
            if cognitive_state.working_memory_load > 0.7:
                score += 0.25
                advantages.append("减少认知负荷")
            reasoning.append("复杂问题分解策略")

        elif strategy == StrategyType.INCREMENTAL:
            if problem_chars.time_constraint > 0.6:
                score += 0.3
                advantages.append("能快速交付可用版本")
            if problem_chars.requirements_clarity < 0.5:
                score += 0.25
                advantages.append("适应需求不明确的情况")
            reasoning.append("渐进式开发策略")

        elif strategy == StrategyType.PROTOTYPE:
            if problem_chars.innovation_need > 0.7:
                score += 0.3
                advantages.append("有利于创新探索")
            if problem_chars.requirements_clarity < 0.4:
                score += 0.25
                advantages.append("帮助明确模糊需求")
            if problem_chars.quality_requirement > 0.8:
                disadvantages.append("原型质量可能不符合高标准要求")

        elif strategy == StrategyType.PATTERN_BASED:
            if problem_chars.domain_familiarity > 0.8:
                score += 0.3
                advantages.append("能复用成熟的解决方案")
            if problem_chars.time_constraint > 0.7:
                score += 0.2
                advantages.append("基于模式能快速实现")
            if problem_chars.innovation_need > 0.6:
                disadvantages.append("可能限制创新思维")

        elif strategy == StrategyType.TEST_DRIVEN:
            if problem_chars.quality_requirement > 0.8:
                score += 0.35
                advantages.append("保证高质量和正确性")
            if problem_chars.maintenance_importance > 0.7:
                score += 0.2
                advantages.append("有利于长期维护")
            if problem_chars.time_constraint > 0.8:
                disadvantages.append("初期开发速度较慢")

        elif strategy == StrategyType.REFACTOR:
            if hasattr(thinking_process, 'hypotheses') and len(thinking_process.hypotheses) > 0:
                # 如果已有初步实现，重构策略更适用
                score += 0.3
                advantages.append("改进现有代码结构")

        # 考虑历史表现
        if strategy in self.historical_performance:
            historical_score = self.historical_performance[strategy]
            score = score * 0.7 + historical_score * 0.3
            reasoning.append(f"历史表现: {historical_score:.2f}")

        # 考虑认知状态
        if cognitive_state.confidence < 0.5 and strategy in [StrategyType.INCREMENTAL, StrategyType.PROTOTYPE]:
            score += 0.1
            advantages.append("低置信度时的安全选择")

        if cognitive_state.mental_effort > 0.8 and strategy == StrategyType.PATTERN_BASED:
            score += 0.15
            advantages.append("减少心理努力")

        return StrategyScore(
            strategy=strategy,
            score=min(1.0, score),
            reasoning="; ".join(reasoning),
            advantages=advantages,
            disadvantages=disadvantages
        )

    def _suggest_alternative_strategy(self, feedback: Dict[str, Any]) -> StrategyType:
        """建议替代策略"""
        current_issues = feedback.get('issues', [])

        # 基于具体问题建议策略
        if 'complexity_too_high' in current_issues:
            return StrategyType.DIVIDE_CONQUER
        elif 'unclear_requirements' in current_issues:
            return StrategyType.PROTOTYPE
        elif 'time_pressure' in current_issues:
            return StrategyType.INCREMENTAL
        elif 'quality_issues' in current_issues:
            return StrategyType.TEST_DRIVEN

        # 默认返回当前策略
        return self.selected_strategy
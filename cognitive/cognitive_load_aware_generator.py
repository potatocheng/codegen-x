"""
认知负荷感知的代码生成策略

根据实时认知负荷评估动态调整代码生成策略，优化程序员的认知体验。
"""

from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum

from .cognitive_load import CognitiveLoadEvaluator, CognitiveComplexity, LoadType
from .programming_strategy import ProgrammingStrategy, StrategyType, ProblemCharacteristics
from .cognitive_model import CognitiveModel, ThinkingStage


class LoadAdaptationStrategy(Enum):
    """负荷适应策略"""
    REDUCE_COMPLEXITY = "reduce_complexity"         # 降低复杂度
    INCREASE_SCAFFOLDING = "increase_scaffolding"   # 增加脚手架
    OPTIMIZE_CHUNKING = "optimize_chunking"         # 优化分块
    ENHANCE_CLARITY = "enhance_clarity"             # 增强清晰度
    PROVIDE_GUIDANCE = "provide_guidance"           # 提供指导
    ADAPTIVE_PACING = "adaptive_pacing"             # 自适应节奏


class CognitiveStrategy(BaseModel):
    """认知策略配置"""
    target_load: float = Field(description="目标认知负荷 (0-1)", ge=0, le=1, default=0.7)
    load_tolerance: float = Field(description="负荷容忍度", ge=0, le=0.3, default=0.1)
    adaptation_threshold: float = Field(description="适应阈值", ge=0.5, le=1.0, default=0.8)
    scaffolding_level: float = Field(description="脚手架水平", ge=0, le=1, default=0.5)
    chunking_size: int = Field(description="认知分块大小", ge=3, le=9, default=7)
    guidance_verbosity: float = Field(description="指导详细程度", ge=0, le=1, default=0.6)


class AdaptationAction(BaseModel):
    """适应性行动"""
    strategy: LoadAdaptationStrategy = Field(description="适应策略")
    action: str = Field(description="具体行动")
    reasoning: str = Field(description="采取行动的原因")
    expected_load_reduction: float = Field(description="预期负荷降低", ge=0, le=1)
    implementation_details: Dict[str, Any] = Field(description="实施细节", default_factory=dict)


class CognitiveLoadAwareGenerator:
    """认知负荷感知的代码生成器

    根据实时认知负荷动态调整生成策略，确保生成过程始终在
    程序员的认知舒适区内进行。
    """

    def __init__(self, strategy: Optional[CognitiveStrategy] = None):
        self.strategy = strategy or CognitiveStrategy()
        self.load_evaluator = CognitiveLoadEvaluator()
        self.programming_strategy = ProgrammingStrategy()

        # 负荷历史记录
        self.load_history: List[CognitiveComplexity] = []
        self.adaptation_history: List[AdaptationAction] = []

        # 当前状态
        self.current_load: Optional[CognitiveComplexity] = None
        self.active_adaptations: List[LoadAdaptationStrategy] = []

    def assess_and_adapt(self,
                        code: str,
                        cognitive_context: Dict[str, Any],
                        thinking_process: Any = None) -> Tuple[List[AdaptationAction], Dict[str, Any]]:
        """评估认知负荷并生成适应性策略

        Args:
            code: 当前生成的代码
            cognitive_context: 认知上下文信息
            thinking_process: 思维过程对象

        Returns:
            (适应性行动列表, 更新的生成配置)
        """
        # 评估当前认知负荷
        self.current_load = self.load_evaluator.evaluate_code_complexity(code, cognitive_context)
        self.load_history.append(self.current_load)

        # 评估思维过程负荷（如果可用）
        if thinking_process:
            thinking_load = self.load_evaluator.evaluate_thinking_complexity(thinking_process)
            self.current_load.total_load = min(1.0,
                (self.current_load.total_load + thinking_load.total_load) / 2
            )

        # 生成适应性行动
        adaptations = self._generate_adaptations()

        # 更新生成配置
        updated_config = self._update_generation_config(adaptations)

        # 记录适应历史
        self.adaptation_history.extend(adaptations)

        return adaptations, updated_config

    def _generate_adaptations(self) -> List[AdaptationAction]:
        """生成适应性行动"""
        adaptations = []

        if not self.current_load:
            return adaptations

        # 检查是否需要适应
        if self.current_load.total_load <= self.strategy.target_load + self.strategy.load_tolerance:
            return adaptations  # 负荷在可接受范围内

        # 分析主导负荷类型并生成对应策略
        dominant_load = self.current_load.get_dominant_load_type()

        if dominant_load == LoadType.INTRINSIC:
            adaptations.extend(self._handle_intrinsic_overload())
        elif dominant_load == LoadType.EXTRANEOUS:
            adaptations.extend(self._handle_extraneous_overload())
        elif dominant_load == LoadType.GERMANE:
            adaptations.extend(self._handle_germane_overload())

        # 根据具体瓶颈生成策略
        for bottleneck in self.current_load.bottlenecks:
            bottleneck_adaptations = self._handle_specific_bottleneck(bottleneck)
            adaptations.extend(bottleneck_adaptations)

        return adaptations

    def _handle_intrinsic_overload(self) -> List[AdaptationAction]:
        """处理内在负荷过载"""
        adaptations = []

        # 降低问题复杂度
        adaptations.append(AdaptationAction(
            strategy=LoadAdaptationStrategy.REDUCE_COMPLEXITY,
            action="分解复杂问题为更小的子问题",
            reasoning="内在负荷过高，问题本身过于复杂",
            expected_load_reduction=0.3,
            implementation_details={
                "decomposition_depth": 2,
                "max_subproblem_size": 5,
                "use_incremental_approach": True
            }
        ))

        # 优化认知分块
        adaptations.append(AdaptationAction(
            strategy=LoadAdaptationStrategy.OPTIMIZE_CHUNKING,
            action="将代码组织为更小的认知块",
            reasoning="内在复杂度需要更好的信息组织",
            expected_load_reduction=0.2,
            implementation_details={
                "chunk_size": min(5, self.strategy.chunking_size),
                "use_meaningful_grouping": True,
                "add_chunk_separators": True
            }
        ))

        return adaptations

    def _handle_extraneous_overload(self) -> List[AdaptationAction]:
        """处理外在负荷过载"""
        adaptations = []

        # 增强代码清晰度
        adaptations.append(AdaptationAction(
            strategy=LoadAdaptationStrategy.ENHANCE_CLARITY,
            action="改进代码结构和命名清晰度",
            reasoning="外在负荷过高，存在不必要的复杂度",
            expected_load_reduction=0.4,
            implementation_details={
                "improve_naming": True,
                "add_type_hints": True,
                "simplify_expressions": True,
                "remove_redundancy": True
            }
        ))

        # 增加脚手架支持
        adaptations.append(AdaptationAction(
            strategy=LoadAdaptationStrategy.INCREASE_SCAFFOLDING,
            action="增加代码注释和结构说明",
            reasoning="外在负荷需要更多支持性信息",
            expected_load_reduction=0.3,
            implementation_details={
                "add_docstrings": True,
                "add_inline_comments": True,
                "add_structure_comments": True,
                "explain_complex_logic": True
            }
        ))

        return adaptations

    def _handle_germane_overload(self) -> List[AdaptationAction]:
        """处理有效负荷过载"""
        adaptations = []

        # 提供更多指导
        adaptations.append(AdaptationAction(
            strategy=LoadAdaptationStrategy.PROVIDE_GUIDANCE,
            action="增加学习指导和解释",
            reasoning="有效负荷过高，需要更多学习支持",
            expected_load_reduction=0.2,
            implementation_details={
                "add_learning_notes": True,
                "explain_patterns": True,
                "provide_examples": True,
                "highlight_key_concepts": True
            }
        ))

        # 自适应节奏控制
        adaptations.append(AdaptationAction(
            strategy=LoadAdaptationStrategy.ADAPTIVE_PACING,
            action="调整生成节奏，允许更多思考时间",
            reasoning="学习负荷需要更合适的节奏",
            expected_load_reduction=0.15,
            implementation_details={
                "slower_pace": True,
                "add_checkpoints": True,
                "encourage_reflection": True
            }
        ))

        return adaptations

    def _handle_specific_bottleneck(self, bottleneck: str) -> List[AdaptationAction]:
        """处理特定瓶颈"""
        adaptations = []

        if "圈复杂度过高" in bottleneck:
            adaptations.append(AdaptationAction(
                strategy=LoadAdaptationStrategy.REDUCE_COMPLEXITY,
                action="简化控制流逻辑",
                reasoning=f"检测到瓶颈: {bottleneck}",
                expected_load_reduction=0.25,
                implementation_details={
                    "extract_methods": True,
                    "reduce_branching": True,
                    "use_early_returns": True
                }
            ))

        elif "嵌套层次过深" in bottleneck:
            adaptations.append(AdaptationAction(
                strategy=LoadAdaptationStrategy.ENHANCE_CLARITY,
                action="减少代码嵌套深度",
                reasoning=f"检测到瓶颈: {bottleneck}",
                expected_load_reduction=0.3,
                implementation_details={
                    "flatten_nesting": True,
                    "use_guard_clauses": True,
                    "extract_nested_logic": True
                }
            ))

        elif "变量数量过多" in bottleneck:
            adaptations.append(AdaptationAction(
                strategy=LoadAdaptationStrategy.OPTIMIZE_CHUNKING,
                action="组织变量为数据结构",
                reasoning=f"检测到瓶颈: {bottleneck}",
                expected_load_reduction=0.2,
                implementation_details={
                    "group_related_variables": True,
                    "use_data_classes": True,
                    "reduce_variable_scope": True
                }
            ))

        elif "函数过长" in bottleneck:
            adaptations.append(AdaptationAction(
                strategy=LoadAdaptationStrategy.REDUCE_COMPLEXITY,
                action="将长函数分解为较小函数",
                reasoning=f"检测到瓶颈: {bottleneck}",
                expected_load_reduction=0.35,
                implementation_details={
                    "extract_methods": True,
                    "single_responsibility": True,
                    "logical_grouping": True
                }
            ))

        return adaptations

    def _update_generation_config(self, adaptations: List[AdaptationAction]) -> Dict[str, Any]:
        """更新生成配置"""
        config = {
            "max_function_length": 20,
            "max_nesting_depth": 3,
            "use_type_hints": False,
            "add_comments": False,
            "code_style": "concise",
            "explanation_level": "basic"
        }

        # 根据适应策略调整配置
        for adaptation in adaptations:
            if adaptation.strategy == LoadAdaptationStrategy.REDUCE_COMPLEXITY:
                config["max_function_length"] = 15
                config["max_nesting_depth"] = 2
                config["prefer_simple_logic"] = True

            elif adaptation.strategy == LoadAdaptationStrategy.INCREASE_SCAFFOLDING:
                config["add_comments"] = True
                config["add_docstrings"] = True
                config["explanation_level"] = "detailed"

            elif adaptation.strategy == LoadAdaptationStrategy.ENHANCE_CLARITY:
                config["use_type_hints"] = True
                config["use_descriptive_names"] = True
                config["code_style"] = "readable"

            elif adaptation.strategy == LoadAdaptationStrategy.OPTIMIZE_CHUNKING:
                config["group_related_code"] = True
                config["add_section_comments"] = True
                config["logical_organization"] = True

            elif adaptation.strategy == LoadAdaptationStrategy.PROVIDE_GUIDANCE:
                config["add_learning_notes"] = True
                config["explain_patterns"] = True
                config["explanation_level"] = "educational"

        return config

    def get_load_trend(self) -> str:
        """获取负荷趋势"""
        if len(self.load_history) < 2:
            return "insufficient_data"

        recent_loads = [load.total_load for load in self.load_history[-3:]]

        if len(recent_loads) >= 2:
            trend = recent_loads[-1] - recent_loads[0]
            if trend > 0.1:
                return "increasing"
            elif trend < -0.1:
                return "decreasing"

        return "stable"

    def get_adaptation_summary(self) -> Dict[str, Any]:
        """获取适应性摘要"""
        if not self.adaptation_history:
            return {"total_adaptations": 0}

        strategy_counts = {}
        total_expected_reduction = 0

        for adaptation in self.adaptation_history:
            strategy = adaptation.strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            total_expected_reduction += adaptation.expected_load_reduction

        avg_expected_reduction = total_expected_reduction / len(self.adaptation_history)

        return {
            "total_adaptations": len(self.adaptation_history),
            "strategy_distribution": strategy_counts,
            "average_expected_reduction": avg_expected_reduction,
            "most_used_strategy": max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else None,
            "load_trend": self.get_load_trend(),
            "current_load": self.current_load.total_load if self.current_load else None
        }

    def should_trigger_emergency_simplification(self) -> bool:
        """检查是否应触发紧急简化"""
        if not self.current_load:
            return False

        # 负荷持续过高
        if self.current_load.total_load > 0.9:
            return True

        # 负荷持续上升
        if len(self.load_history) >= 3:
            recent_loads = [load.total_load for load in self.load_history[-3:]]
            if all(recent_loads[i] < recent_loads[i+1] for i in range(len(recent_loads)-1)):
                return True

        return False

    def generate_emergency_simplification_plan(self) -> Dict[str, Any]:
        """生成紧急简化计划"""
        return {
            "action": "emergency_simplification",
            "strategies": [
                "将问题分解为最小可行单元",
                "使用最简单的实现方式",
                "减少所有非必要功能",
                "增加大量解释性注释",
                "降低抽象层次"
            ],
            "target_load": 0.5,
            "implementation": {
                "max_function_lines": 10,
                "no_complex_patterns": True,
                "explicit_variable_names": True,
                "step_by_step_comments": True
            }
        }
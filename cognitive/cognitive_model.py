"""认知编程模型

模拟人类程序员的认知过程，包括问题理解、解决方案设计、
代码实现和验证等阶段的认知状态变化。
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import time
from dataclasses import dataclass


class ThinkingStage(Enum):
    """认知思维阶段"""
    PROBLEM_COMPREHENSION = "problem_comprehension"      # 问题理解
    SOLUTION_PLANNING = "solution_planning"              # 解决方案规划
    ALGORITHM_DESIGN = "algorithm_design"                # 算法设计
    IMPLEMENTATION = "implementation"                     # 代码实现
    VALIDATION = "validation"                            # 验证测试
    OPTIMIZATION = "optimization"                        # 优化改进
    REFLECTION = "reflection"                            # 反思总结


class CognitiveState(BaseModel):
    """认知状态"""
    stage: ThinkingStage = Field(description="当前思维阶段")
    confidence: float = Field(description="置信度 (0-1)", ge=0, le=1)
    mental_effort: float = Field(description="心理努力程度 (0-1)", ge=0, le=1)
    working_memory_load: float = Field(description="工作记忆负荷 (0-1)", ge=0, le=1)
    focused_concepts: List[str] = Field(description="当前关注的概念")
    discovered_insights: List[str] = Field(description="发现的洞察")
    pending_questions: List[str] = Field(description="待解决的问题")

    class Config:
        extra = "forbid"


@dataclass
class CognitiveTransition:
    """认知状态转移"""
    from_stage: ThinkingStage
    to_stage: ThinkingStage
    trigger: str  # 触发转移的条件
    duration: float  # 转移耗时
    confidence_change: float  # 置信度变化


class CognitiveModel(BaseModel):
    """认知编程模型

    模拟人类程序员的完整认知过程，包括各个思维阶段的状态变化、
    认知负荷评估和决策制定过程。
    """

    current_state: CognitiveState = Field(description="当前认知状态")
    state_history: List[CognitiveState] = Field(default_factory=list, description="状态历史")
    transitions: List[CognitiveTransition] = Field(default_factory=list, description="状态转移记录")
    cognitive_biases: Dict[str, float] = Field(default_factory=dict, description="认知偏见")
    problem_context: Dict[str, Any] = Field(default_factory=dict, description="问题上下文")

    class Config:
        extra = "forbid"

    def __init__(self, **data):
        if "current_state" not in data:
            data["current_state"] = CognitiveState(
                stage=ThinkingStage.PROBLEM_COMPREHENSION,
                confidence=0.3,
                mental_effort=0.5,
                working_memory_load=0.2,
                focused_concepts=[],
                discovered_insights=[],
                pending_questions=[]
            )
        super().__init__(**data)

    def transition_to_stage(self, new_stage: ThinkingStage, trigger: str = "") -> bool:
        """转移到新的认知阶段"""
        start_time = time.time()

        # 检查转移是否合理
        if not self._is_valid_transition(self.current_state.stage, new_stage):
            return False

        # 保存当前状态到历史
        self.state_history.append(self.current_state.model_copy())

        # 计算新状态
        new_state = self._compute_new_state(new_stage)

        # 记录转移
        duration = time.time() - start_time
        transition = CognitiveTransition(
            from_stage=self.current_state.stage,
            to_stage=new_stage,
            trigger=trigger,
            duration=duration,
            confidence_change=new_state.confidence - self.current_state.confidence
        )
        self.transitions.append(transition)

        # 更新当前状态
        self.current_state = new_state
        return True

    def add_insight(self, insight: str) -> None:
        """添加发现的洞察"""
        if insight not in self.current_state.discovered_insights:
            new_insights = self.current_state.discovered_insights + [insight]
            self.current_state.discovered_insights = new_insights
            # 洞察会提高置信度
            self.current_state.confidence = min(1.0, self.current_state.confidence + 0.1)

    def add_question(self, question: str) -> None:
        """添加待解决的问题"""
        if question not in self.current_state.pending_questions:
            new_questions = self.current_state.pending_questions + [question]
            self.current_state.pending_questions = new_questions
            # 问题会降低置信度
            self.current_state.confidence = max(0.0, self.current_state.confidence - 0.05)

    def resolve_question(self, question: str, solution: str) -> None:
        """解决问题"""
        if question in self.current_state.pending_questions:
            # 移除问题
            new_questions = [q for q in self.current_state.pending_questions if q != question]
            self.current_state.pending_questions = new_questions

            # 添加解决方案作为洞察
            self.add_insight(f"解决方案: {solution}")

    def focus_on_concepts(self, concepts: List[str]) -> None:
        """聚焦于特定概念"""
        self.current_state.focused_concepts = concepts
        # 更新工作记忆负荷
        self.current_state.working_memory_load = min(1.0, len(concepts) * 0.1)

    def get_cognitive_summary(self) -> Dict[str, Any]:
        """获取认知过程摘要"""
        return {
            "current_stage": self.current_state.stage.value,
            "overall_confidence": self.current_state.confidence,
            "mental_effort": self.current_state.mental_effort,
            "total_insights": len(self.current_state.discovered_insights),
            "pending_questions": len(self.current_state.pending_questions),
            "stage_transitions": len(self.transitions),
            "time_per_stage": self._calculate_time_per_stage(),
            "cognitive_load_trend": self._analyze_load_trend()
        }

    def _is_valid_transition(self, from_stage: ThinkingStage, to_stage: ThinkingStage) -> bool:
        """检查状态转移是否有效"""
        # 定义允许的转移路径
        valid_transitions = {
            ThinkingStage.PROBLEM_COMPREHENSION: [
                ThinkingStage.SOLUTION_PLANNING,
                ThinkingStage.PROBLEM_COMPREHENSION  # 可以重新理解
            ],
            ThinkingStage.SOLUTION_PLANNING: [
                ThinkingStage.ALGORITHM_DESIGN,
                ThinkingStage.PROBLEM_COMPREHENSION,  # 可以回到理解阶段
                ThinkingStage.SOLUTION_PLANNING  # 可以重新规划
            ],
            ThinkingStage.ALGORITHM_DESIGN: [
                ThinkingStage.IMPLEMENTATION,
                ThinkingStage.SOLUTION_PLANNING,  # 可以回到规划
                ThinkingStage.ALGORITHM_DESIGN  # 可以重新设计
            ],
            ThinkingStage.IMPLEMENTATION: [
                ThinkingStage.VALIDATION,
                ThinkingStage.ALGORITHM_DESIGN,  # 发现设计问题
                ThinkingStage.IMPLEMENTATION  # 继续实现
            ],
            ThinkingStage.VALIDATION: [
                ThinkingStage.OPTIMIZATION,
                ThinkingStage.IMPLEMENTATION,  # 需要修改实现
                ThinkingStage.REFLECTION,
                ThinkingStage.VALIDATION  # 继续验证
            ],
            ThinkingStage.OPTIMIZATION: [
                ThinkingStage.VALIDATION,  # 验证优化效果
                ThinkingStage.REFLECTION,
                ThinkingStage.OPTIMIZATION  # 继续优化
            ],
            ThinkingStage.REFLECTION: [
                ThinkingStage.PROBLEM_COMPREHENSION,  # 重新开始
                ThinkingStage.REFLECTION  # 继续反思
            ]
        }

        return to_stage in valid_transitions.get(from_stage, [])

    def _compute_new_state(self, new_stage: ThinkingStage) -> CognitiveState:
        """计算新认知状态"""
        # 基于阶段特征计算新状态
        stage_characteristics = {
            ThinkingStage.PROBLEM_COMPREHENSION: {
                "confidence": 0.3, "mental_effort": 0.6, "working_memory_load": 0.4
            },
            ThinkingStage.SOLUTION_PLANNING: {
                "confidence": 0.5, "mental_effort": 0.8, "working_memory_load": 0.7
            },
            ThinkingStage.ALGORITHM_DESIGN: {
                "confidence": 0.6, "mental_effort": 0.9, "working_memory_load": 0.8
            },
            ThinkingStage.IMPLEMENTATION: {
                "confidence": 0.7, "mental_effort": 0.7, "working_memory_load": 0.6
            },
            ThinkingStage.VALIDATION: {
                "confidence": 0.8, "mental_effort": 0.5, "working_memory_load": 0.4
            },
            ThinkingStage.OPTIMIZATION: {
                "confidence": 0.9, "mental_effort": 0.6, "working_memory_load": 0.5
            },
            ThinkingStage.REFLECTION: {
                "confidence": 0.8, "mental_effort": 0.3, "working_memory_load": 0.2
            }
        }

        characteristics = stage_characteristics[new_stage]

        # 保留一些历史信息
        return CognitiveState(
            stage=new_stage,
            confidence=characteristics["confidence"],
            mental_effort=characteristics["mental_effort"],
            working_memory_load=characteristics["working_memory_load"],
            focused_concepts=self.current_state.focused_concepts,
            discovered_insights=self.current_state.discovered_insights,
            pending_questions=self.current_state.pending_questions
        )

    def _calculate_time_per_stage(self) -> Dict[str, float]:
        """计算每个阶段的平均时间"""
        stage_times = {}
        for transition in self.transitions:
            stage = transition.from_stage.value
            if stage not in stage_times:
                stage_times[stage] = []
            stage_times[stage].append(transition.duration)

        return {
            stage: sum(times) / len(times) if times else 0
            for stage, times in stage_times.items()
        }

    def _analyze_load_trend(self) -> str:
        """分析认知负荷趋势"""
        if len(self.state_history) < 2:
            return "insufficient_data"

        recent_loads = [state.working_memory_load for state in self.state_history[-3:]]
        if len(recent_loads) >= 2:
            if recent_loads[-1] > recent_loads[0]:
                return "increasing"
            elif recent_loads[-1] < recent_loads[0]:
                return "decreasing"
        return "stable"
"""
认知决策追踪器

记录和分析编程过程中的认知决策，为可解释性和研究提供详细的思维过程数据。
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import json


class DecisionType(Enum):
    """决策类型"""
    STRATEGY_SELECTION = "strategy_selection"       # 策略选择
    TOOL_SELECTION = "tool_selection"               # 工具选择
    APPROACH_CHANGE = "approach_change"             # 方法改变
    OPTIMIZATION_CHOICE = "optimization_choice"     # 优化选择
    VALIDATION_STRATEGY = "validation_strategy"     # 验证策略
    ERROR_HANDLING = "error_handling"               # 错误处理
    REFINEMENT_DIRECTION = "refinement_direction"   # 优化方向


class CognitiveDecision(BaseModel):
    """单个认知决策记录"""
    decision_id: str = Field(description="决策唯一标识")
    timestamp: datetime = Field(description="决策时间")
    stage: str = Field(description="决策阶段")
    decision_type: DecisionType = Field(description="决策类型")
    decision: str = Field(description="具体决策内容")
    reasoning: str = Field(description="决策推理过程")
    alternatives_considered: List[str] = Field(description="考虑过的其他选项", default_factory=list)
    confidence: float = Field(description="决策置信度 (0-1)", ge=0, le=1)
    context: Dict[str, Any] = Field(description="决策上下文", default_factory=dict)
    outcome_expectation: str = Field(description="预期结果")
    actual_outcome: Optional[str] = Field(description="实际结果", default=None)


class CognitiveTrace(BaseModel):
    """完整的认知追踪记录"""
    session_id: str = Field(description="会话标识")
    start_time: datetime = Field(description="开始时间")
    end_time: Optional[datetime] = Field(description="结束时间", default=None)
    problem_statement: str = Field(description="问题陈述")
    decisions: List[CognitiveDecision] = Field(description="决策序列", default_factory=list)
    cognitive_load_evolution: List[Dict[str, float]] = Field(description="认知负荷演化", default_factory=list)
    strategy_adaptations: List[Dict[str, Any]] = Field(description="策略适应", default_factory=list)
    final_outcome: Optional[Dict[str, Any]] = Field(description="最终结果", default=None)


class CognitiveDecisionTracker:
    """认知决策追踪器"""

    def __init__(self, session_id: str, problem_statement: str):
        self.trace = CognitiveTrace(
            session_id=session_id,
            start_time=datetime.now(),
            problem_statement=problem_statement
        )
        self.decision_counter = 0

    def record_decision(self,
                       stage: str,
                       decision_type: DecisionType,
                       decision: str,
                       reasoning: str,
                       confidence: float = 0.7,
                       alternatives: Optional[List[str]] = None,
                       context: Optional[Dict[str, Any]] = None,
                       expected_outcome: str = "") -> str:
        """记录一个认知决策

        Args:
            stage: 决策阶段
            decision_type: 决策类型
            decision: 具体决策内容
            reasoning: 决策推理过程
            confidence: 置信度
            alternatives: 考虑过的其他选项
            context: 决策上下文
            expected_outcome: 预期结果

        Returns:
            决策ID
        """
        self.decision_counter += 1
        decision_id = f"{self.trace.session_id}_decision_{self.decision_counter}"

        cognitive_decision = CognitiveDecision(
            decision_id=decision_id,
            timestamp=datetime.now(),
            stage=stage,
            decision_type=decision_type,
            decision=decision,
            reasoning=reasoning,
            alternatives_considered=alternatives or [],
            confidence=confidence,
            context=context or {},
            outcome_expectation=expected_outcome
        )

        self.trace.decisions.append(cognitive_decision)
        return decision_id

    def update_decision_outcome(self, decision_id: str, actual_outcome: str):
        """更新决策的实际结果"""
        for decision in self.trace.decisions:
            if decision.decision_id == decision_id:
                decision.actual_outcome = actual_outcome
                break

    def record_cognitive_load(self, stage: str, intrinsic: float, extraneous: float, germane: float):
        """记录认知负荷变化"""
        self.trace.cognitive_load_evolution.append({
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "intrinsic_load": intrinsic,
            "extraneous_load": extraneous,
            "germane_load": germane,
            "total_load": intrinsic + extraneous + germane
        })

    def record_strategy_adaptation(self, old_strategy: str, new_strategy: str, trigger: str, reasoning: str):
        """记录策略适应"""
        self.trace.strategy_adaptations.append({
            "timestamp": datetime.now().isoformat(),
            "old_strategy": old_strategy,
            "new_strategy": new_strategy,
            "trigger": trigger,
            "reasoning": reasoning
        })

    def finalize_session(self, final_outcome: Dict[str, Any]):
        """结束会话并记录最终结果"""
        self.trace.end_time = datetime.now()
        self.trace.final_outcome = final_outcome

    def get_decision_summary(self) -> Dict[str, Any]:
        """获取决策摘要统计"""
        if not self.trace.decisions:
            return {"total_decisions": 0}

        decision_types = {}
        avg_confidence = 0
        successful_decisions = 0

        for decision in self.trace.decisions:
            decision_type = decision.decision_type.value
            decision_types[decision_type] = decision_types.get(decision_type, 0) + 1
            avg_confidence += decision.confidence

            if decision.actual_outcome and "success" in decision.actual_outcome.lower():
                successful_decisions += 1

        avg_confidence /= len(self.trace.decisions)
        success_rate = successful_decisions / len(self.trace.decisions)

        return {
            "total_decisions": len(self.trace.decisions),
            "decision_types": decision_types,
            "average_confidence": avg_confidence,
            "success_rate": success_rate,
            "session_duration": self._calculate_duration(),
            "cognitive_load_trend": self._analyze_cognitive_load_trend()
        }

    def get_decision_chain(self) -> List[Dict[str, Any]]:
        """获取决策链条"""
        chain = []
        for decision in self.trace.decisions:
            chain.append({
                "stage": decision.stage,
                "type": decision.decision_type.value,
                "decision": decision.decision,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "alternatives": decision.alternatives_considered,
                "expected": decision.outcome_expectation,
                "actual": decision.actual_outcome
            })
        return chain

    def export_trace(self) -> Dict[str, Any]:
        """导出完整的认知追踪数据"""
        return {
            "trace": self.trace.model_dump(),
            "summary": self.get_decision_summary(),
            "decision_chain": self.get_decision_chain(),
            "insights": self._generate_insights()
        }

    def _calculate_duration(self) -> float:
        """计算会话持续时间（秒）"""
        if self.trace.end_time:
            return (self.trace.end_time - self.trace.start_time).total_seconds()
        return (datetime.now() - self.trace.start_time).total_seconds()

    def _analyze_cognitive_load_trend(self) -> str:
        """分析认知负荷趋势"""
        if len(self.trace.cognitive_load_evolution) < 2:
            return "insufficient_data"

        loads = [item["total_load"] for item in self.trace.cognitive_load_evolution]

        if loads[-1] > loads[0] * 1.2:
            return "increasing"
        elif loads[-1] < loads[0] * 0.8:
            return "decreasing"
        else:
            return "stable"

    def _generate_insights(self) -> List[str]:
        """生成认知洞察"""
        insights = []

        # 决策类型分析
        decision_types = {}
        for decision in self.trace.decisions:
            dt = decision.decision_type.value
            decision_types[dt] = decision_types.get(dt, 0) + 1

        most_common_type = max(decision_types.items(), key=lambda x: x[1])[0] if decision_types else None
        if most_common_type:
            insights.append(f"主要决策类型是 {most_common_type}")

        # 置信度分析
        avg_confidence = sum(d.confidence for d in self.trace.decisions) / len(self.trace.decisions) if self.trace.decisions else 0
        if avg_confidence > 0.8:
            insights.append("决策置信度较高，表明思路清晰")
        elif avg_confidence < 0.5:
            insights.append("决策置信度较低，可能存在不确定性")

        # 策略适应分析
        if len(self.trace.strategy_adaptations) > 2:
            insights.append("策略适应频繁，显示了灵活的问题解决能力")
        elif len(self.trace.strategy_adaptations) == 0:
            insights.append("坚持初始策略，表明策略选择恰当")

        # 认知负荷分析
        load_trend = self._analyze_cognitive_load_trend()
        if load_trend == "increasing":
            insights.append("认知负荷递增，问题复杂度可能超出预期")
        elif load_trend == "decreasing":
            insights.append("认知负荷递减，问题理解逐渐深入")

        return insights


class CognitiveDecisionManager:
    """认知决策管理器

    管理多个会话的认知决策追踪
    """

    def __init__(self):
        self.active_trackers: Dict[str, CognitiveDecisionTracker] = {}
        self.completed_sessions: List[Dict[str, Any]] = []

    def start_session(self, session_id: str, problem_statement: str) -> CognitiveDecisionTracker:
        """开始新的认知追踪会话"""
        tracker = CognitiveDecisionTracker(session_id, problem_statement)
        self.active_trackers[session_id] = tracker
        return tracker

    def end_session(self, session_id: str, final_outcome: Dict[str, Any]):
        """结束认知追踪会话"""
        if session_id in self.active_trackers:
            tracker = self.active_trackers[session_id]
            tracker.finalize_session(final_outcome)

            # 保存到已完成会话
            self.completed_sessions.append(tracker.export_trace())

            # 从活跃追踪器中移除
            del self.active_trackers[session_id]

    def get_tracker(self, session_id: str) -> Optional[CognitiveDecisionTracker]:
        """获取指定会话的追踪器"""
        return self.active_trackers.get(session_id)

    def export_all_sessions(self) -> List[Dict[str, Any]]:
        """导出所有会话数据"""
        all_sessions = self.completed_sessions.copy()

        # 包含当前活跃的会话
        for tracker in self.active_trackers.values():
            all_sessions.append(tracker.export_trace())

        return all_sessions

    def save_to_file(self, filepath: str):
        """保存所有会话数据到文件"""
        data = {
            "export_time": datetime.now().isoformat(),
            "total_sessions": len(self.completed_sessions) + len(self.active_trackers),
            "sessions": self.export_all_sessions()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
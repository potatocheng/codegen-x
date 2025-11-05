"""
协同代码生成框架

实现Master-Worker协同机制：
- Master Agent作为裁判和流程推动者
- 多个Worker Agent作为专业化代码生成器
- 基于DAG的认知阶段流程控制
- 智能融合和迭代优化机制
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import time

from pydantic import BaseModel, Field
from llm.structured_llm import StructuredLLM


class CognitiveStage(Enum):
    """认知阶段枚举"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    ALGORITHM_SELECTION = "algorithm_selection"
    INTERFACE_DESIGN = "interface_design"
    CORE_IMPLEMENTATION = "core_implementation"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    TESTING_STRATEGY = "testing_strategy"
    INTEGRATION = "integration"


class FusionStrategy(Enum):
    """融合策略枚举"""
    BEST_SINGLE = "best_single"
    WEIGHTED_MERGE = "weighted_merge"
    FEATURE_COMBINATION = "feature_combination"
    HIERARCHICAL_FUSION = "hierarchical_fusion"
    CONSENSUS_VOTING = "consensus_voting"


@dataclass
class QualityMetrics:
    """质量指标"""
    creativity: float = 0.0
    correctness: float = 0.0
    efficiency: float = 0.0
    completeness: float = 0.0
    maintainability: float = 0.0
    security: float = 0.0

    @property
    def overall_score(self) -> float:
        """综合得分"""
        weights = {
            'correctness': 0.3,
            'efficiency': 0.2,
            'completeness': 0.2,
            'maintainability': 0.15,
            'creativity': 0.1,
            'security': 0.05
        }
        return sum(getattr(self, key) * weight for key, weight in weights.items())


@dataclass
class StageOutput:
    """阶段输出"""
    stage: CognitiveStage
    worker_id: str
    content: Any
    confidence: float
    quality_metrics: QualityMetrics
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'stage': self.stage.value,
            'worker_id': self.worker_id,
            'content': self.content,
            'confidence': self.confidence,
            'quality_metrics': {
                'creativity': self.quality_metrics.creativity,
                'correctness': self.quality_metrics.correctness,
                'efficiency': self.quality_metrics.efficiency,
                'completeness': self.quality_metrics.completeness,
                'maintainability': self.quality_metrics.maintainability,
                'security': self.quality_metrics.security,
                'overall_score': self.quality_metrics.overall_score
            },
            'reasoning': self.reasoning,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


@dataclass
class FusionResult:
    """融合结果"""
    stage: CognitiveStage
    fused_content: Any
    fusion_strategy: FusionStrategy
    source_workers: List[str]
    confidence: float
    quality_metrics: QualityMetrics
    fusion_reasoning: str = ""
    alternative_versions: List[StageOutput] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'stage': self.stage.value,
            'fused_content': self.fused_content,
            'fusion_strategy': self.fusion_strategy.value,
            'source_workers': self.source_workers,
            'confidence': self.confidence,
            'quality_metrics': {
                'creativity': self.quality_metrics.creativity,
                'correctness': self.quality_metrics.correctness,
                'efficiency': self.quality_metrics.efficiency,
                'completeness': self.quality_metrics.completeness,
                'maintainability': self.quality_metrics.maintainability,
                'security': self.quality_metrics.security,
                'overall_score': self.quality_metrics.overall_score
            },
            'fusion_reasoning': self.fusion_reasoning,
            'timestamp': self.timestamp
        }


class StageOutputSchema(BaseModel):
    """阶段输出的Pydantic模式"""
    content: str = Field(description="该阶段的具体输出内容")
    reasoning: str = Field(description="生成该内容的推理过程")
    confidence: float = Field(description="对输出质量的置信度 (0-1)", ge=0, le=1)
    key_features: List[str] = Field(description="该输出的关键特征")
    potential_issues: List[str] = Field(description="可能存在的问题", default=[])
    suggestions: List[str] = Field(description="改进建议", default=[])


class FusionAnalysisSchema(BaseModel):
    """融合分析的Pydantic模式"""
    quality_analysis: Dict[str, float] = Field(description="各输出的质量分析")
    compatibility_matrix: Dict[str, Dict[str, float]] = Field(description="兼容性矩阵")
    recommended_strategy: str = Field(description="推荐的融合策略")
    fusion_plan: str = Field(description="融合计划描述")
    expected_improvements: List[str] = Field(description="预期改进点")


class DAGNode:
    """DAG节点"""
    def __init__(self, stage: CognitiveStage, dependencies: List[CognitiveStage] = None):
        self.stage = stage
        self.dependencies = dependencies or []
        self.dependents: List[CognitiveStage] = []
        self.completed = False
        self.result: Optional[FusionResult] = None


class DAGWorkflow:
    """DAG工作流引擎"""

    def __init__(self):
        self.nodes: Dict[CognitiveStage, DAGNode] = {}
        self.execution_order: List[CognitiveStage] = []

    def add_stage(self, stage: CognitiveStage, dependencies: List[CognitiveStage] = None):
        """添加认知阶段"""
        node = DAGNode(stage, dependencies or [])
        self.nodes[stage] = node

        # 更新依赖关系
        for dep in node.dependencies:
            if dep in self.nodes:
                self.nodes[dep].dependents.append(stage)

    def get_ready_stages(self) -> List[CognitiveStage]:
        """获取可以执行的阶段"""
        ready = []
        for stage, node in self.nodes.items():
            if not node.completed and all(
                self.nodes[dep].completed for dep in node.dependencies
            ):
                ready.append(stage)
        return ready

    def mark_completed(self, stage: CognitiveStage, result: FusionResult):
        """标记阶段完成"""
        if stage in self.nodes:
            self.nodes[stage].completed = True
            self.nodes[stage].result = result

    def get_execution_order(self) -> List[CognitiveStage]:
        """获取拓扑排序的执行顺序"""
        if self.execution_order:
            return self.execution_order

        # 拓扑排序
        visited = set()
        temp_visited = set()
        order = []

        def dfs(stage: CognitiveStage):
            if stage in temp_visited:
                raise ValueError(f"检测到循环依赖: {stage}")
            if stage in visited:
                return

            temp_visited.add(stage)
            for dep in self.nodes[stage].dependencies:
                dfs(dep)
            temp_visited.remove(stage)
            visited.add(stage)
            order.append(stage)

        for stage in self.nodes:
            if stage not in visited:
                dfs(stage)

        self.execution_order = order
        return order

    def get_context_for_stage(self, stage: CognitiveStage) -> Dict[str, Any]:
        """获取阶段所需的上下文"""
        context = {}
        node = self.nodes[stage]

        for dep in node.dependencies:
            dep_node = self.nodes[dep]
            if dep_node.result:
                context[f"{dep.value}_result"] = dep_node.result.fused_content
                context[f"{dep.value}_quality"] = dep_node.result.quality_metrics.overall_score

        return context

    def is_completed(self) -> bool:
        """检查是否全部完成"""
        return all(node.completed for node in self.nodes.values())

    def get_progress(self) -> float:
        """获取进度百分比"""
        if not self.nodes:
            return 0.0
        completed_count = sum(1 for node in self.nodes.values() if node.completed)
        return completed_count / len(self.nodes)


def create_default_workflow() -> DAGWorkflow:
    """创建默认的工作流"""
    workflow = DAGWorkflow()

    # 添加阶段及依赖关系
    workflow.add_stage(CognitiveStage.REQUIREMENT_ANALYSIS, [])
    workflow.add_stage(CognitiveStage.ARCHITECTURE_DESIGN, [CognitiveStage.REQUIREMENT_ANALYSIS])
    workflow.add_stage(CognitiveStage.ALGORITHM_SELECTION, [CognitiveStage.REQUIREMENT_ANALYSIS])
    workflow.add_stage(CognitiveStage.INTERFACE_DESIGN, [CognitiveStage.ARCHITECTURE_DESIGN])
    workflow.add_stage(CognitiveStage.CORE_IMPLEMENTATION, [
        CognitiveStage.ARCHITECTURE_DESIGN,
        CognitiveStage.ALGORITHM_SELECTION,
        CognitiveStage.INTERFACE_DESIGN
    ])
    workflow.add_stage(CognitiveStage.ERROR_HANDLING, [CognitiveStage.CORE_IMPLEMENTATION])
    workflow.add_stage(CognitiveStage.PERFORMANCE_OPTIMIZATION, [CognitiveStage.CORE_IMPLEMENTATION])
    workflow.add_stage(CognitiveStage.TESTING_STRATEGY, [CognitiveStage.CORE_IMPLEMENTATION])
    workflow.add_stage(CognitiveStage.INTEGRATION, [
        CognitiveStage.ERROR_HANDLING,
        CognitiveStage.PERFORMANCE_OPTIMIZATION,
        CognitiveStage.TESTING_STRATEGY
    ])

    return workflow


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborativeCodeGenerator:
    """协作代码生成器主类

    整合Master Agent、Worker Agents和DAG工作流，
    实现完整的多模型协作代码生成流程。
    """

    def __init__(
        self,
        master_llm: StructuredLLM,
        worker_configs: List[Dict[str, Any]],
        workflow: DAGWorkflow = None,
        max_concurrent_workers: int = 3,
        fusion_threshold: float = 0.7
    ):
        """
        Args:
            master_llm: Master Agent使用的LLM
            worker_configs: Worker配置列表
            workflow: DAG工作流（默认使用标准工作流）
            max_concurrent_workers: 最大并发Worker数
            fusion_threshold: 融合阈值
        """
        self.master_llm = master_llm
        self.workflow = workflow or create_default_workflow()
        self.max_concurrent_workers = max_concurrent_workers
        self.fusion_threshold = fusion_threshold

        # 初始化Master Agent
        self.master_agent = None  # 延迟初始化，避免循环导入

        # 初始化Worker Agents
        self.workers = []
        self._initialize_workers(worker_configs)

        # 执行状态
        self.current_stage = None
        self.stage_results = {}  # 保存每个阶段的融合结果
        self.execution_history = []  # 执行历史

        logger.info(f"协作代码生成器初始化: {len(self.workers)} 个Workers")

    def _initialize_workers(self, worker_configs: List[Dict[str, Any]]):
        """初始化Worker Agents"""
        from .worker_agent import WorkerAgent, WorkerConfig

        for config in worker_configs:
            try:
                # 创建LLM实例
                worker_llm = StructuredLLM(
                    model=config.get('model', 'gpt-4o'),
                    api_key=config.get('api_key'),
                    base_url=config.get('base_url')
                )

                # 创建Worker配置
                worker_config = WorkerConfig(
                    model_name=config.get('model', 'gpt-4o'),
                    specialization=config.get('specialization', 'general'),
                    temperature=config.get('temperature', 0.3),
                    max_tokens=config.get('max_tokens', 2000),
                    expertise_areas=config.get('expertise_areas', []),
                    preferred_stages=config.get('preferred_stages', [])
                )

                # 创建Worker
                worker = WorkerAgent(worker_llm, worker_config)
                self.workers.append(worker)

            except Exception as e:
                logger.error(f"初始化Worker失败: {e}")

    def _initialize_master_agent(self):
        """延迟初始化Master Agent"""
        if self.master_agent is None:
            from .master_agent import MasterAgent
            self.master_agent = MasterAgent(self.master_llm, self.fusion_threshold)

    def generate_code(
        self,
        requirement: str,
        additional_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        协作生成代码

        Args:
            requirement: 用户需求描述
            additional_context: 额外上下文信息

        Returns:
            生成结果，包含最终代码和过程信息
        """
        self._initialize_master_agent()

        logger.info(f"开始协作代码生成: {requirement[:100]}...")

        start_time = time.time()
        context = {
            'requirement': requirement,
            'timestamp': start_time,
            **(additional_context or {})
        }

        try:
            # 重置状态
            self._reset_state()

            # 执行DAG工作流
            execution_order = self.workflow.get_execution_order()
            logger.info(f"执行顺序: {[stage.value for stage in execution_order]}")

            for stage in execution_order:
                if self.workflow.nodes[stage].completed:
                    continue

                logger.info(f"开始执行阶段: {stage.value}")
                stage_result = self._execute_stage(stage, context)

                if stage_result:
                    self.workflow.mark_completed(stage, stage_result)
                    self.stage_results[stage] = stage_result

                    # 更新上下文
                    context.update(self.workflow.get_context_for_stage(stage))

                    logger.info(f"阶段 {stage.value} 完成，质量得分: {stage_result.quality_metrics.overall_score:.2f}")
                else:
                    logger.error(f"阶段 {stage.value} 执行失败")
                    break

            # 生成最终结果
            final_result = self._generate_final_result(context, time.time() - start_time)

            logger.info(f"协作代码生成完成，总耗时: {time.time() - start_time:.2f}秒")
            return final_result

        except Exception as e:
            logger.error(f"协作代码生成失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'partial_results': self.stage_results,
                'execution_time': time.time() - start_time
            }

    def _reset_state(self):
        """重置执行状态"""
        self.current_stage = None
        self.stage_results.clear()
        self.execution_history.clear()

        # 重置工作流状态
        for node in self.workflow.nodes.values():
            node.completed = False
            node.result = None

    def _execute_stage(
        self,
        stage: CognitiveStage,
        context: Dict[str, Any]
    ) -> Optional[FusionResult]:
        """
        执行单个认知阶段

        Args:
            stage: 当前阶段
            context: 上下文信息

        Returns:
            融合结果
        """
        self.current_stage = stage

        # 选择适合的Workers
        suitable_workers = self._select_suitable_workers(stage)

        if not suitable_workers:
            logger.warning(f"没有找到适合阶段 {stage.value} 的Workers，使用所有Workers")
            suitable_workers = self.workers[:self.max_concurrent_workers]

        # 获取前置结果
        previous_results = {
            dep_stage: self.stage_results[dep_stage]
            for dep_stage in self.workflow.nodes[stage].dependencies
            if dep_stage in self.stage_results
        }

        # 并行执行Workers
        stage_outputs = []

        if len(suitable_workers) <= self.max_concurrent_workers:
            # 可以并行执行所有Workers
            stage_outputs = self._execute_workers_parallel(
                suitable_workers, stage, context, previous_results
            )
        else:
            # 分批执行
            stage_outputs = self._execute_workers_batched(
                suitable_workers, stage, context, previous_results
            )

        if not stage_outputs:
            logger.error(f"阶段 {stage.value} 没有收到任何有效输出")
            return None

        # Master融合
        try:
            fusion_result = self.master_agent.judge_stage_outputs(
                stage, stage_outputs, context
            )

            # 记录执行历史
            self.execution_history.append({
                'stage': stage.value,
                'workers_used': [output.worker_id for output in stage_outputs],
                'fusion_strategy': fusion_result.fusion_strategy.value,
                'quality_score': fusion_result.quality_metrics.overall_score,
                'confidence': fusion_result.confidence,
                'timestamp': time.time()
            })

            return fusion_result

        except Exception as e:
            logger.error(f"Master融合阶段 {stage.value} 失败: {e}")
            return None

    def _select_suitable_workers(self, stage: CognitiveStage) -> List:
        """选择适合当前阶段的Workers"""
        from .worker_agent import WorkerAgent

        suitable = []
        general_workers = []

        for worker in self.workers:
            if isinstance(worker, WorkerAgent) and worker.is_suitable_for_stage(stage):
                suitable.append(worker)
            elif hasattr(worker, 'config') and worker.config.specialization == 'general':
                general_workers.append(worker)

        # 如果专业Workers不足，补充通用Workers
        if len(suitable) < 2 and general_workers:
            needed = min(2 - len(suitable), len(general_workers))
            suitable.extend(general_workers[:needed])

        return suitable

    def _execute_workers_parallel(
        self,
        workers: List,
        stage: CognitiveStage,
        context: Dict[str, Any],
        previous_results: Dict[CognitiveStage, Any]
    ) -> List[StageOutput]:
        """并行执行Workers"""
        stage_outputs = []

        with ThreadPoolExecutor(max_workers=len(workers)) as executor:
            # 提交任务
            future_to_worker = {}
            for worker in workers:
                future = executor.submit(
                    worker.process_stage,
                    stage, context, previous_results
                )
                future_to_worker[future] = worker

            # 收集结果
            for future in as_completed(future_to_worker, timeout=120):
                worker = future_to_worker[future]
                try:
                    output = future.result()
                    if output:
                        stage_outputs.append(output)
                        logger.info(f"Worker {worker.worker_id} 完成阶段 {stage.value}")
                except Exception as e:
                    logger.error(f"Worker {worker.worker_id} 执行失败: {e}")

        return stage_outputs

    def _execute_workers_batched(
        self,
        workers: List,
        stage: CognitiveStage,
        context: Dict[str, Any],
        previous_results: Dict[CognitiveStage, Any]
    ) -> List[StageOutput]:
        """分批执行Workers"""
        stage_outputs = []
        batch_size = self.max_concurrent_workers

        for i in range(0, len(workers), batch_size):
            batch = workers[i:i + batch_size]
            batch_outputs = self._execute_workers_parallel(
                batch, stage, context, previous_results
            )
            stage_outputs.extend(batch_outputs)

        return stage_outputs

    def _generate_final_result(self, context: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
        """生成最终结果"""

        # 获取最终集成结果
        final_stage = CognitiveStage.INTEGRATION
        final_result = self.stage_results.get(final_stage)

        if not final_result:
            # 如果没有集成阶段，使用核心实现阶段
            final_stage = CognitiveStage.CORE_IMPLEMENTATION
            final_result = self.stage_results.get(final_stage)

        if not final_result:
            return {
                'success': False,
                'error': '没有可用的最终结果',
                'partial_results': self.stage_results,
                'execution_time': execution_time
            }

        # 计算总体统计
        quality_scores = [
            result.quality_metrics.overall_score
            for result in self.stage_results.values()
        ]

        confidence_scores = [
            result.confidence
            for result in self.stage_results.values()
        ]

        return {
            'success': True,
            'final_code': final_result.fused_content,
            'final_quality_score': final_result.quality_metrics.overall_score,
            'final_confidence': final_result.confidence,
            'requirement': context['requirement'],

            # 过程信息
            'stages_completed': len(self.stage_results),
            'total_stages': len(self.workflow.nodes),
            'execution_time': execution_time,
            'execution_history': self.execution_history,

            # 统计信息
            'avg_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
            'min_quality_score': min(quality_scores) if quality_scores else 0,
            'max_quality_score': max(quality_scores) if quality_scores else 0,
            'avg_confidence': statistics.mean(confidence_scores) if confidence_scores else 0,

            # 详细结果
            'stage_results': {
                stage.value: result.to_dict()
                for stage, result in self.stage_results.items()
            },

            # Worker统计
            'worker_stats': {
                worker.worker_id: worker.get_performance_stats()
                for worker in self.workers
            }
        }

    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度"""
        return {
            'current_stage': self.current_stage.value if self.current_stage else None,
            'stages_completed': len(self.stage_results),
            'total_stages': len(self.workflow.nodes),
            'progress_percentage': self.workflow.get_progress() * 100,
            'execution_history': self.execution_history
        }

    def add_worker(self, worker_config: Dict[str, Any]) -> bool:
        """动态添加Worker"""
        try:
            self._initialize_workers([worker_config])
            logger.info(f"成功添加Worker: {worker_config.get('specialization', 'general')}")
            return True
        except Exception as e:
            logger.error(f"添加Worker失败: {e}")
            return False

    def remove_worker(self, worker_id: str) -> bool:
        """移除Worker"""
        for i, worker in enumerate(self.workers):
            if worker.worker_id == worker_id:
                self.workers.pop(i)
                logger.info(f"移除Worker: {worker_id}")
                return True

        logger.warning(f"未找到Worker: {worker_id}")
        return False

    def get_worker_stats(self) -> Dict[str, Any]:
        """获取Worker统计信息"""
        return {
            'total_workers': len(self.workers),
            'worker_details': [
                {
                    'id': worker.worker_id,
                    'specialization': worker.config.specialization,
                    'model': worker.config.model_name,
                    'stats': worker.get_performance_stats()
                }
                for worker in self.workers
            ]
        }

    def customize_workflow(self, custom_workflow: DAGWorkflow):
        """自定义工作流"""
        self.workflow = custom_workflow
        logger.info("工作流已更新")

    def __str__(self) -> str:
        return f"CollaborativeCodeGenerator(workers={len(self.workers)}, stages={len(self.workflow.nodes)})"

    def __repr__(self) -> str:
        return self.__str__()
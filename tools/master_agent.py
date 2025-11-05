"""
Master Agent - 协同代码生成的裁判和融合器

负责：
1. 评判各Worker的输出质量
2. 选择最佳融合策略
3. 执行智能融合
4. 推动整个协作流程
"""

import re
import ast
import statistics
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .collaborative_framework import (
    CognitiveStage, FusionStrategy, StageOutput, FusionResult, QualityMetrics,
    StageOutputSchema, FusionAnalysisSchema, logger
)
from llm.structured_llm import StructuredLLM


class MasterAgent:
    """Master Agent - 协作流程的指挥官和裁判"""

    def __init__(self, llm: StructuredLLM, fusion_threshold: float = 0.7):
        """
        Args:
            llm: 用于智能分析和融合的LLM
            fusion_threshold: 触发融合的质量阈值（低于此值会考虑融合）
        """
        self.llm = llm
        self.fusion_threshold = fusion_threshold
        self.fusion_strategies = {
            FusionStrategy.BEST_SINGLE: self._select_best_single,
            FusionStrategy.WEIGHTED_MERGE: self._weighted_merge,
            FusionStrategy.FEATURE_COMBINATION: self._combine_features,
            FusionStrategy.HIERARCHICAL_FUSION: self._hierarchical_fusion,
            FusionStrategy.CONSENSUS_VOTING: self._consensus_voting
        }
        logger.info("Master Agent initialized")

    def judge_stage_outputs(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        context: Dict[str, Any] = None
    ) -> FusionResult:
        """
        评判并融合阶段输出

        Args:
            stage: 当前认知阶段
            outputs: 各Worker的输出
            context: 上下文信息

        Returns:
            融合后的结果
        """
        logger.info(f"开始评判阶段 {stage.value}，收到 {len(outputs)} 个输出")

        if not outputs:
            raise ValueError(f"阶段 {stage.value} 没有收到任何输出")

        if len(outputs) == 1:
            # 只有一个输出，直接返回
            output = outputs[0]
            return FusionResult(
                stage=stage,
                fused_content=output.content,
                fusion_strategy=FusionStrategy.BEST_SINGLE,
                source_workers=[output.worker_id],
                confidence=output.confidence,
                quality_metrics=output.quality_metrics,
                fusion_reasoning="只有单个输出，无需融合",
                alternative_versions=[]
            )

        # 多个输出需要分析和融合
        try:
            # 1. 分析质量和兼容性
            analysis = self._analyze_outputs(stage, outputs, context)

            # 2. 选择融合策略
            strategy = self._select_fusion_strategy(stage, outputs, analysis)

            # 3. 执行融合
            fusion_result = self.fusion_strategies[strategy](stage, outputs, analysis)

            logger.info(f"阶段 {stage.value} 融合完成，策略: {strategy.value}")
            return fusion_result

        except Exception as e:
            logger.error(f"融合失败: {e}")
            # 降级到选择最佳单个输出
            return self._select_best_single(stage, outputs, {})

    def _analyze_outputs(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """分析各输出的质量和兼容性"""

        # 构建分析提示
        analysis_prompt = self._build_analysis_prompt(stage, outputs, context)

        try:
            # 使用LLM进行智能分析
            analysis = self.llm.generate_structured(
                prompt=analysis_prompt,
                output_schema=FusionAnalysisSchema,
                temperature=0.3
            )

            # 补充量化分析
            quantitative_analysis = self._quantitative_analysis(outputs)

            return {
                'llm_analysis': analysis.model_dump(),
                'quantitative': quantitative_analysis,
                'stage': stage,
                'output_count': len(outputs)
            }

        except Exception as e:
            logger.warning(f"LLM分析失败，降级到基础分析: {e}")
            return self._basic_analysis(outputs)

    def _build_analysis_prompt(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        context: Dict[str, Any] = None
    ) -> str:
        """构建分析提示"""

        context_str = ""
        if context:
            context_str = f"\n## 上下文信息\n{json.dumps(context, indent=2, ensure_ascii=False)}"

        outputs_str = ""
        for i, output in enumerate(outputs, 1):
            outputs_str += f"""
### 输出 {i} (来自 {output.worker_id})
**内容:** {output.content}
**推理:** {output.reasoning}
**置信度:** {output.confidence:.2f}
**质量得分:** {output.quality_metrics.overall_score:.2f}
"""

        return f"""作为代码生成协作的Master Agent，请分析以下 {stage.value} 阶段的多个输出。

## 当前阶段
{stage.value} - {self._get_stage_description(stage)}

{context_str}

## 各Worker输出
{outputs_str}

## 分析任务
请从以下维度分析各输出：

1. **质量分析**: 评估每个输出在创意性、正确性、效率、完整性、可维护性、安全性方面的表现
2. **兼容性分析**: 分析各输出之间是否可以融合，哪些部分可以组合
3. **融合策略**: 推荐最适合的融合策略
4. **融合计划**: 描述具体如何融合这些输出
5. **预期改进**: 融合后相比单个输出的预期改进点

请基于技术准确性和代码质量进行客观分析。"""

    def _get_stage_description(self, stage: CognitiveStage) -> str:
        """获取阶段描述"""
        descriptions = {
            CognitiveStage.REQUIREMENT_ANALYSIS: "分析用户需求，明确功能要求和约束条件",
            CognitiveStage.ARCHITECTURE_DESIGN: "设计整体架构，定义组件和接口",
            CognitiveStage.ALGORITHM_SELECTION: "选择合适的算法和数据结构",
            CognitiveStage.INTERFACE_DESIGN: "设计函数签名和API接口",
            CognitiveStage.CORE_IMPLEMENTATION: "实现核心功能逻辑",
            CognitiveStage.ERROR_HANDLING: "设计错误处理和异常管理",
            CognitiveStage.PERFORMANCE_OPTIMIZATION: "优化性能和资源使用",
            CognitiveStage.TESTING_STRATEGY: "设计测试用例和验证策略",
            CognitiveStage.INTEGRATION: "整合各部分成完整的解决方案"
        }
        return descriptions.get(stage, "")

    def _quantitative_analysis(self, outputs: List[StageOutput]) -> Dict[str, Any]:
        """量化分析"""
        if not outputs:
            return {}

        # 质量指标统计
        quality_stats = {}
        metrics = ['creativity', 'correctness', 'efficiency', 'completeness', 'maintainability', 'security']

        for metric in metrics:
            values = [getattr(output.quality_metrics, metric) for output in outputs]
            quality_stats[metric] = {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values)
            }

        # 置信度统计
        confidences = [output.confidence for output in outputs]
        confidence_stats = {
            'mean': statistics.mean(confidences),
            'std': statistics.stdev(confidences) if len(confidences) > 1 else 0,
            'min': min(confidences),
            'max': max(confidences)
        }

        # 内容长度统计
        content_lengths = [len(str(output.content)) for output in outputs]
        length_stats = {
            'mean': statistics.mean(content_lengths),
            'std': statistics.stdev(content_lengths) if len(content_lengths) > 1 else 0,
            'min': min(content_lengths),
            'max': max(content_lengths)
        }

        return {
            'quality_stats': quality_stats,
            'confidence_stats': confidence_stats,
            'length_stats': length_stats,
            'output_count': len(outputs)
        }

    def _basic_analysis(self, outputs: List[StageOutput]) -> Dict[str, Any]:
        """基础分析（当LLM分析失败时的降级方案）"""
        if not outputs:
            return {}

        # 简单的得分排序
        sorted_outputs = sorted(outputs, key=lambda x: x.quality_metrics.overall_score, reverse=True)

        return {
            'basic_analysis': True,
            'best_output_id': sorted_outputs[0].worker_id,
            'quality_ranking': [output.worker_id for output in sorted_outputs],
            'avg_quality': statistics.mean([output.quality_metrics.overall_score for output in outputs]),
            'should_fuse': len(outputs) > 1 and sorted_outputs[0].quality_metrics.overall_score < self.fusion_threshold * 100
        }

    def _select_fusion_strategy(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        analysis: Dict[str, Any]
    ) -> FusionStrategy:
        """选择融合策略"""

        if 'llm_analysis' in analysis:
            # 基于LLM分析选择策略
            recommended = analysis['llm_analysis'].get('recommended_strategy', '')
            strategy_mapping = {
                'best_single': FusionStrategy.BEST_SINGLE,
                'weighted_merge': FusionStrategy.WEIGHTED_MERGE,
                'feature_combination': FusionStrategy.FEATURE_COMBINATION,
                'hierarchical_fusion': FusionStrategy.HIERARCHICAL_FUSION,
                'consensus_voting': FusionStrategy.CONSENSUS_VOTING
            }

            if recommended in strategy_mapping:
                return strategy_mapping[recommended]

        # 降级到基于规则的策略选择
        quality_scores = [output.quality_metrics.overall_score for output in outputs]
        max_quality = max(quality_scores)
        quality_variance = statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0

        # 如果有一个明显更好的输出
        if max_quality >= self.fusion_threshold * 100 and quality_variance > 15:
            return FusionStrategy.BEST_SINGLE

        # 如果质量相近，尝试融合
        if quality_variance < 10:
            return FusionStrategy.CONSENSUS_VOTING
        elif stage in [CognitiveStage.CORE_IMPLEMENTATION, CognitiveStage.INTEGRATION]:
            return FusionStrategy.FEATURE_COMBINATION
        else:
            return FusionStrategy.WEIGHTED_MERGE

    def _select_best_single(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        analysis: Dict[str, Any]
    ) -> FusionResult:
        """选择最佳单个输出"""
        best_output = max(outputs, key=lambda x: (
            x.quality_metrics.overall_score,
            x.confidence
        ))

        return FusionResult(
            stage=stage,
            fused_content=best_output.content,
            fusion_strategy=FusionStrategy.BEST_SINGLE,
            source_workers=[best_output.worker_id],
            confidence=best_output.confidence,
            quality_metrics=best_output.quality_metrics,
            fusion_reasoning=f"选择质量最高的单个输出 (得分: {best_output.quality_metrics.overall_score:.2f})",
            alternative_versions=[output for output in outputs if output.worker_id != best_output.worker_id]
        )

    def _weighted_merge(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        analysis: Dict[str, Any]
    ) -> FusionResult:
        """加权融合多个输出"""
        # 计算权重（基于质量得分和置信度）
        weights = []
        total_score = sum(output.quality_metrics.overall_score * output.confidence for output in outputs)

        for output in outputs:
            weight = (output.quality_metrics.overall_score * output.confidence) / total_score
            weights.append(weight)

        # 构建融合提示
        fusion_prompt = self._build_weighted_merge_prompt(stage, outputs, weights)

        try:
            # 使用LLM进行智能融合
            fused_content = self.llm.generate_structured(
                prompt=fusion_prompt,
                output_schema=StageOutputSchema,
                temperature=0.3
            )

            # 计算融合后的质量指标
            fused_quality = self._calculate_weighted_quality(outputs, weights)
            fused_confidence = sum(output.confidence * weight for output, weight in zip(outputs, weights))

            return FusionResult(
                stage=stage,
                fused_content=fused_content.content,
                fusion_strategy=FusionStrategy.WEIGHTED_MERGE,
                source_workers=[output.worker_id for output in outputs],
                confidence=fused_confidence,
                quality_metrics=fused_quality,
                fusion_reasoning=f"基于质量得分加权融合 {len(outputs)} 个输出",
                alternative_versions=outputs
            )

        except Exception as e:
            logger.warning(f"加权融合失败，降级到最佳单个: {e}")
            return self._select_best_single(stage, outputs, analysis)

    def _combine_features(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        analysis: Dict[str, Any]
    ) -> FusionResult:
        """特征组合融合"""
        # 分析各输出的特征
        feature_analysis = self._analyze_features(stage, outputs)

        # 构建特征组合提示
        combination_prompt = self._build_feature_combination_prompt(stage, outputs, feature_analysis)

        try:
            # 使用LLM进行特征组合
            combined_content = self.llm.generate_structured(
                prompt=combination_prompt,
                output_schema=StageOutputSchema,
                temperature=0.4
            )

            # 计算组合后的质量指标
            combined_quality = self._calculate_combined_quality(outputs, feature_analysis)
            combined_confidence = min(0.9, max(output.confidence for output in outputs) * 1.1)

            return FusionResult(
                stage=stage,
                fused_content=combined_content.content,
                fusion_strategy=FusionStrategy.FEATURE_COMBINATION,
                source_workers=[output.worker_id for output in outputs],
                confidence=combined_confidence,
                quality_metrics=combined_quality,
                fusion_reasoning=f"组合各输出的最佳特征",
                alternative_versions=outputs
            )

        except Exception as e:
            logger.warning(f"特征组合失败，降级到加权融合: {e}")
            return self._weighted_merge(stage, outputs, analysis)

    def _hierarchical_fusion(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        analysis: Dict[str, Any]
    ) -> FusionResult:
        """分层次融合"""
        if len(outputs) <= 2:
            return self._weighted_merge(stage, outputs, analysis)

        # 分层次两两融合
        current_outputs = outputs.copy()

        while len(current_outputs) > 1:
            next_round = []

            for i in range(0, len(current_outputs), 2):
                if i + 1 < len(current_outputs):
                    # 融合两个输出
                    pair_result = self._weighted_merge(stage, [current_outputs[i], current_outputs[i + 1]], analysis)
                    # 转换回StageOutput格式
                    next_round.append(StageOutput(
                        stage=stage,
                        worker_id=f"fused_{i//2}",
                        content=pair_result.fused_content,
                        confidence=pair_result.confidence,
                        quality_metrics=pair_result.quality_metrics,
                        reasoning=f"分层融合第{len(current_outputs)//2}轮"
                    ))
                else:
                    next_round.append(current_outputs[i])

            current_outputs = next_round

        final_output = current_outputs[0]

        return FusionResult(
            stage=stage,
            fused_content=final_output.content,
            fusion_strategy=FusionStrategy.HIERARCHICAL_FUSION,
            source_workers=[output.worker_id for output in outputs],
            confidence=final_output.confidence,
            quality_metrics=final_output.quality_metrics,
            fusion_reasoning=f"分层次融合 {len(outputs)} 个输出",
            alternative_versions=outputs
        )

    def _consensus_voting(
        self,
        stage: CognitiveStage,
        outputs: List[StageOutput],
        analysis: Dict[str, Any]
    ) -> FusionResult:
        """共识投票融合"""
        # 构建投票提示
        voting_prompt = self._build_consensus_voting_prompt(stage, outputs)

        try:
            # 使用LLM进行共识分析
            consensus_result = self.llm.generate_structured(
                prompt=voting_prompt,
                output_schema=StageOutputSchema,
                temperature=0.2
            )

            # 计算共识置信度
            consensus_confidence = self._calculate_consensus_confidence(outputs)
            consensus_quality = self._calculate_consensus_quality(outputs)

            return FusionResult(
                stage=stage,
                fused_content=consensus_result.content,
                fusion_strategy=FusionStrategy.CONSENSUS_VOTING,
                source_workers=[output.worker_id for output in outputs],
                confidence=consensus_confidence,
                quality_metrics=consensus_quality,
                fusion_reasoning=f"基于共识投票融合 {len(outputs)} 个输出",
                alternative_versions=outputs
            )

        except Exception as e:
            logger.warning(f"共识投票失败，降级到最佳单个: {e}")
            return self._select_best_single(stage, outputs, analysis)

    def _build_weighted_merge_prompt(self, stage: CognitiveStage, outputs: List[StageOutput], weights: List[float]) -> str:
        """构建加权融合提示"""
        outputs_str = ""
        for output, weight in zip(outputs, weights):
            outputs_str += f"""
### 输出 (权重: {weight:.3f})
来源: {output.worker_id}
内容: {output.content}
推理: {output.reasoning}
"""

        return f"""请对以下 {stage.value} 阶段的多个输出进行加权融合。

{outputs_str}

融合要求：
1. 根据权重重要性整合各输出的优点
2. 保持技术准确性和逻辑一致性
3. 权重较高的输出应该有更大影响
4. 最终结果应该优于任何单个输出

请提供融合后的内容，包括详细的推理过程。"""

    def _build_feature_combination_prompt(self, stage: CognitiveStage, outputs: List[StageOutput], features: Dict) -> str:
        """构建特征组合提示"""
        outputs_str = ""
        for i, output in enumerate(outputs, 1):
            outputs_str += f"""
### 输出 {i}
来源: {output.worker_id}
内容: {output.content}
关键特征: {output.metadata.get('key_features', [])}
"""

        return f"""请组合以下 {stage.value} 阶段输出的最佳特征。

{outputs_str}

组合策略：
1. 识别每个输出的独特优势
2. 选择最佳的算法、架构或实现方式
3. 避免功能重复，保持简洁性
4. 确保组合后的方案在技术上可行

请提供组合后的最优方案。"""

    def _build_consensus_voting_prompt(self, stage: CognitiveStage, outputs: List[StageOutput]) -> str:
        """构建共识投票提示"""
        outputs_str = ""
        for i, output in enumerate(outputs, 1):
            outputs_str += f"""
### 输出 {i}
来源: {output.worker_id}
内容: {output.content}
置信度: {output.confidence:.2f}
质量得分: {output.quality_metrics.overall_score:.2f}
"""

        return f"""分析以下 {stage.value} 阶段的多个输出，寻找共识。

{outputs_str}

分析任务：
1. 识别各输出的共同点和分歧点
2. 评估不同方案的技术优劣
3. 基于工程最佳实践选择共识方案
4. 如果无法达成共识，选择技术上最可靠的方案

请提供基于共识的最终方案。"""

    def _calculate_weighted_quality(self, outputs: List[StageOutput], weights: List[float]) -> QualityMetrics:
        """计算加权质量指标"""
        metrics = QualityMetrics()

        for attr in ['creativity', 'correctness', 'efficiency', 'completeness', 'maintainability', 'security']:
            weighted_value = sum(
                getattr(output.quality_metrics, attr) * weight
                for output, weight in zip(outputs, weights)
            )
            setattr(metrics, attr, weighted_value)

        return metrics

    def _calculate_combined_quality(self, outputs: List[StageOutput], features: Dict) -> QualityMetrics:
        """计算组合质量指标"""
        # 取各指标的最大值（假设组合取优）
        metrics = QualityMetrics()

        for attr in ['creativity', 'correctness', 'efficiency', 'completeness', 'maintainability', 'security']:
            max_value = max(getattr(output.quality_metrics, attr) for output in outputs)
            # 组合通常能稍微提升质量
            setattr(metrics, attr, min(100.0, max_value * 1.05))

        return metrics

    def _calculate_consensus_confidence(self, outputs: List[StageOutput]) -> float:
        """计算共识置信度"""
        if not outputs:
            return 0.0

        confidences = [output.confidence for output in outputs]
        # 共识置信度基于一致性
        mean_confidence = statistics.mean(confidences)
        std_confidence = statistics.stdev(confidences) if len(confidences) > 1 else 0

        # 一致性越高，共识置信度越高
        consensus_factor = max(0.5, 1.0 - std_confidence)
        return min(0.95, mean_confidence * consensus_factor)

    def _calculate_consensus_quality(self, outputs: List[StageOutput]) -> QualityMetrics:
        """计算共识质量指标"""
        metrics = QualityMetrics()

        for attr in ['creativity', 'correctness', 'efficiency', 'completeness', 'maintainability', 'security']:
            values = [getattr(output.quality_metrics, attr) for output in outputs]
            # 共识取中位数（更稳健）
            consensus_value = statistics.median(values)
            setattr(metrics, attr, consensus_value)

        return metrics

    def _analyze_features(self, stage: CognitiveStage, outputs: List[StageOutput]) -> Dict[str, Any]:
        """分析各输出的特征"""
        features = {
            'common_patterns': [],
            'unique_approaches': {},
            'best_aspects': {}
        }

        # 简单的特征分析（实际项目中可以更复杂）
        for output in outputs:
            content_str = str(output.content)
            # 代码特征分析
            if stage == CognitiveStage.CORE_IMPLEMENTATION:
                if 'class ' in content_str:
                    features['unique_approaches'][output.worker_id] = 'object_oriented'
                elif 'def ' in content_str:
                    features['unique_approaches'][output.worker_id] = 'functional'

        return features


import json
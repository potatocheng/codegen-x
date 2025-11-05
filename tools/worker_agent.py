"""
Worker Agent - 专业化代码生成器

每个Worker专注于特定的认知阶段和专业领域，
生成高质量的阶段性输出供Master融合选择。
"""

from typing import Dict, List, Any, Optional, Set
import re
import ast
import time
from dataclasses import dataclass

from .collaborative_framework import (
    CognitiveStage, StageOutput, QualityMetrics,
    StageOutputSchema, logger
)
from llm.structured_llm import StructuredLLM


class WorkerSpecialization:
    """Worker专业化领域"""
    ALGORITHM = "algorithm"          # 算法专家
    ARCHITECTURE = "architecture"    # 架构专家
    PERFORMANCE = "performance"      # 性能专家
    SECURITY = "security"           # 安全专家
    TESTING = "testing"             # 测试专家
    UI_UX = "ui_ux"                # 用户体验专家
    DATA_SCIENCE = "data_science"   # 数据科学专家
    GENERAL = "general"             # 通用专家


@dataclass
class WorkerConfig:
    """Worker配置"""
    model_name: str
    specialization: str
    temperature: float = 0.3
    max_tokens: int = 2000
    expertise_areas: List[str] = None
    preferred_stages: List[CognitiveStage] = None


class WorkerAgent:
    """Worker Agent - 专业化代码生成器"""

    def __init__(self, llm: StructuredLLM, config: WorkerConfig):
        """
        Args:
            llm: LLM实例
            config: Worker配置
        """
        self.llm = llm
        self.config = config
        self.worker_id = f"{config.model_name}_{config.specialization}"
        self.expertise_areas = config.expertise_areas or []
        self.preferred_stages = config.preferred_stages or []

        # 性能统计
        self.stats = {
            'stages_processed': 0,
            'avg_quality_score': 0.0,
            'avg_confidence': 0.0,
            'processing_times': []
        }

        logger.info(f"Worker Agent初始化: {self.worker_id} (专业: {config.specialization})")

    def process_stage(
        self,
        stage: CognitiveStage,
        context: Dict[str, Any],
        previous_results: Dict[CognitiveStage, Any] = None
    ) -> StageOutput:
        """
        处理特定认知阶段

        Args:
            stage: 当前认知阶段
            context: 上下文信息（包含用户需求等）
            previous_results: 前面阶段的结果

        Returns:
            该阶段的输出
        """
        start_time = time.time()

        try:
            logger.info(f"Worker {self.worker_id} 开始处理阶段 {stage.value}")

            # 1. 构建阶段特定的提示
            prompt = self._build_stage_prompt(stage, context, previous_results)

            # 2. 调用LLM生成内容
            output = self.llm.generate_structured(
                prompt=prompt,
                output_schema=StageOutputSchema,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            # 3. 评估输出质量
            quality_metrics = self._evaluate_output_quality(stage, output, context)

            # 4. 计算置信度
            confidence = self._calculate_confidence(stage, output, quality_metrics)

            # 5. 创建StageOutput
            stage_output = StageOutput(
                stage=stage,
                worker_id=self.worker_id,
                content=output.content,
                confidence=confidence,
                quality_metrics=quality_metrics,
                reasoning=output.reasoning,
                metadata={
                    'key_features': output.key_features,
                    'potential_issues': output.potential_issues,
                    'suggestions': output.suggestions,
                    'specialization': self.config.specialization,
                    'processing_time': time.time() - start_time
                }
            )

            # 6. 更新统计信息
            self._update_stats(stage_output, time.time() - start_time)

            logger.info(f"Worker {self.worker_id} 完成阶段 {stage.value} (质量: {quality_metrics.overall_score:.2f})")
            return stage_output

        except Exception as e:
            logger.error(f"Worker {self.worker_id} 处理阶段 {stage.value} 失败: {e}")
            # 返回默认输出
            return self._create_fallback_output(stage, context, str(e))

    def _build_stage_prompt(
        self,
        stage: CognitiveStage,
        context: Dict[str, Any],
        previous_results: Dict[CognitiveStage, Any] = None
    ) -> str:
        """构建阶段特定的提示"""

        # 基础信息
        requirement = context.get('requirement', '')

        # 专业化指导
        specialization_guide = self._get_specialization_guide(stage)

        # 前置结果
        previous_context = self._format_previous_results(previous_results or {})

        # 阶段特定的提示模板
        stage_prompts = {
            CognitiveStage.REQUIREMENT_ANALYSIS: self._build_requirement_analysis_prompt,
            CognitiveStage.ARCHITECTURE_DESIGN: self._build_architecture_design_prompt,
            CognitiveStage.ALGORITHM_SELECTION: self._build_algorithm_selection_prompt,
            CognitiveStage.INTERFACE_DESIGN: self._build_interface_design_prompt,
            CognitiveStage.CORE_IMPLEMENTATION: self._build_core_implementation_prompt,
            CognitiveStage.ERROR_HANDLING: self._build_error_handling_prompt,
            CognitiveStage.PERFORMANCE_OPTIMIZATION: self._build_performance_optimization_prompt,
            CognitiveStage.TESTING_STRATEGY: self._build_testing_strategy_prompt,
            CognitiveStage.INTEGRATION: self._build_integration_prompt
        }

        prompt_builder = stage_prompts.get(stage, self._build_generic_prompt)
        return prompt_builder(requirement, specialization_guide, previous_context, context)

    def _get_specialization_guide(self, stage: CognitiveStage) -> str:
        """获取专业化指导"""
        specialization_guides = {
            WorkerSpecialization.ALGORITHM: {
                CognitiveStage.ALGORITHM_SELECTION: "重点关注算法复杂度、效率和适用场景",
                CognitiveStage.CORE_IMPLEMENTATION: "优先选择高效、可读性强的算法实现",
                CognitiveStage.PERFORMANCE_OPTIMIZATION: "专注于算法层面的性能优化"
            },
            WorkerSpecialization.ARCHITECTURE: {
                CognitiveStage.REQUIREMENT_ANALYSIS: "从架构角度分析系统需求和约束",
                CognitiveStage.ARCHITECTURE_DESIGN: "设计清晰、可扩展的系统架构",
                CognitiveStage.INTERFACE_DESIGN: "设计简洁、一致的接口规范"
            },
            WorkerSpecialization.PERFORMANCE: {
                CognitiveStage.ALGORITHM_SELECTION: "选择性能最优的算法",
                CognitiveStage.CORE_IMPLEMENTATION: "编写高性能、低延迟的代码",
                CognitiveStage.PERFORMANCE_OPTIMIZATION: "全面的性能分析和优化"
            },
            WorkerSpecialization.SECURITY: {
                CognitiveStage.REQUIREMENT_ANALYSIS: "识别安全需求和威胁模型",
                CognitiveStage.CORE_IMPLEMENTATION: "确保代码安全，防范常见漏洞",
                CognitiveStage.ERROR_HANDLING: "安全的错误处理，避免信息泄露"
            },
            WorkerSpecialization.TESTING: {
                CognitiveStage.INTERFACE_DESIGN: "设计便于测试的接口",
                CognitiveStage.TESTING_STRATEGY: "全面的测试策略和用例设计",
                CognitiveStage.CORE_IMPLEMENTATION: "编写可测试性强的代码"
            }
        }

        guides = specialization_guides.get(self.config.specialization, {})
        return guides.get(stage, f"从{self.config.specialization}专业角度分析和实现")

    def _format_previous_results(self, previous_results: Dict[CognitiveStage, Any]) -> str:
        """格式化前置结果"""
        if not previous_results:
            return ""

        context_str = "## 前置阶段结果:\n"
        for stage, result in previous_results.items():
            if hasattr(result, 'fused_content'):
                context_str += f"### {stage.value}:\n{result.fused_content}\n\n"
            else:
                context_str += f"### {stage.value}:\n{result}\n\n"

        return context_str

    def _build_requirement_analysis_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建需求分析提示"""
        return f"""作为{self.config.specialization}专家，请分析以下需求。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 分析任务
请从专业角度分析需求，包括：
1. 核心功能要求
2. 性能和质量要求
3. 技术约束和限制
4. 潜在的挑战和风险
5. 成功标准

提供详细的需求分析和专业建议。"""

    def _build_architecture_design_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建架构设计提示"""
        return f"""作为{self.config.specialization}专家，请设计系统架构。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 设计任务
请设计清晰的系统架构，包括：
1. 主要组件和模块
2. 组件间的关系和交互
3. 数据流和控制流
4. 接口定义
5. 技术栈选择

提供架构设计图和详细说明。"""

    def _build_algorithm_selection_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建算法选择提示"""
        return f"""作为{self.config.specialization}专家，请选择合适的算法。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 算法选择任务
请选择最适合的算法，考虑：
1. 时间复杂度和空间复杂度
2. 实现复杂度
3. 在不同数据规模下的表现
4. 算法的稳定性和可靠性
5. 相关的数据结构选择

提供算法选择理由和复杂度分析。"""

    def _build_interface_design_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建接口设计提示"""
        return f"""作为{self.config.specialization}专家，请设计函数接口。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 接口设计任务
请设计清晰的接口，包括：
1. 函数签名（参数和返回值）
2. 参数类型和约束
3. 异常处理策略
4. 使用示例
5. 文档字符串

确保接口简洁、一致且易于使用。"""

    def _build_core_implementation_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建核心实现提示"""
        return f"""作为{self.config.specialization}专家，请实现核心功能。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 实现任务
请提供高质量的代码实现：
1. 遵循前面设计的架构和接口
2. 使用选定的算法
3. 代码清晰、可读性强
4. 包含必要的注释
5. 考虑边界条件和异常情况

确保代码的正确性和可维护性。"""

    def _build_error_handling_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建错误处理提示"""
        return f"""作为{self.config.specialization}专家，请设计错误处理机制。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 错误处理任务
请设计完善的错误处理：
1. 识别可能的错误类型
2. 设计异常层次结构
3. 错误恢复策略
4. 用户友好的错误信息
5. 日志记录策略

确保系统的健壮性和可调试性。"""

    def _build_performance_optimization_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建性能优化提示"""
        return f"""作为{self.config.specialization}专家，请优化系统性能。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 性能优化任务
请提供性能优化方案：
1. 识别性能瓶颈
2. 算法层面的优化
3. 数据结构优化
4. 内存使用优化
5. 并发和并行优化

提供具体的优化措施和预期效果。"""

    def _build_testing_strategy_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建测试策略提示"""
        return f"""作为{self.config.specialization}专家，请设计测试策略。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 测试策略任务
请设计全面的测试策略：
1. 单元测试用例
2. 集成测试方案
3. 边界条件测试
4. 性能测试
5. 错误情况测试

确保测试覆盖率和有效性。"""

    def _build_integration_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建集成提示"""
        return f"""作为{self.config.specialization}专家，请整合所有组件。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

## 集成任务
请将各阶段结果整合成完整方案：
1. 整合所有组件
2. 确保接口兼容性
3. 解决集成冲突
4. 验证整体功能
5. 最终质量检查

提供完整的、可运行的解决方案。"""

    def _build_generic_prompt(self, requirement: str, guide: str, previous: str, context: Dict) -> str:
        """构建通用提示"""
        return f"""作为{self.config.specialization}专家，请处理当前任务。

## 用户需求
{requirement}

## 专业指导
{guide}

{previous}

请从专业角度提供高质量的输出。"""

    def _evaluate_output_quality(
        self,
        stage: CognitiveStage,
        output: StageOutputSchema,
        context: Dict[str, Any]
    ) -> QualityMetrics:
        """评估输出质量"""
        metrics = QualityMetrics()

        try:
            # 1. 创意性评估
            metrics.creativity = self._evaluate_creativity(stage, output)

            # 2. 正确性评估
            metrics.correctness = self._evaluate_correctness(stage, output, context)

            # 3. 效率评估
            metrics.efficiency = self._evaluate_efficiency(stage, output)

            # 4. 完整性评估
            metrics.completeness = self._evaluate_completeness(stage, output)

            # 5. 可维护性评估
            metrics.maintainability = self._evaluate_maintainability(stage, output)

            # 6. 安全性评估
            metrics.security = self._evaluate_security(stage, output)

        except Exception as e:
            logger.warning(f"质量评估失败: {e}")
            # 设置默认值
            for attr in ['creativity', 'correctness', 'efficiency', 'completeness', 'maintainability', 'security']:
                setattr(metrics, attr, 60.0)

        return metrics

    def _evaluate_creativity(self, stage: CognitiveStage, output: StageOutputSchema) -> float:
        """评估创意性"""
        content = output.content.lower()
        key_features = output.key_features

        score = 50.0  # 基础分

        # 基于关键特征数量
        if len(key_features) > 3:
            score += 15.0
        elif len(key_features) > 1:
            score += 10.0

        # 基于内容复杂度
        if len(content) > 500:
            score += 10.0

        # 创新关键词检测
        innovation_keywords = [
            'innovative', 'creative', 'novel', 'unique', 'optimization',
            'efficient', 'elegant', 'creative', '创新', '优化', '高效'
        ]

        for keyword in innovation_keywords:
            if keyword in content:
                score += 5.0

        # 专业化加分
        if self.config.specialization in ['algorithm', 'architecture']:
            score += 5.0

        return min(100.0, score)

    def _evaluate_correctness(self, stage: CognitiveStage, output: StageOutputSchema, context: Dict) -> float:
        """评估正确性"""
        content = output.content
        reasoning = output.reasoning

        score = 60.0  # 基础分

        # 检查推理质量
        if len(reasoning) > 100:
            score += 15.0
        elif len(reasoning) > 50:
            score += 10.0

        # 检查潜在问题识别
        if output.potential_issues:
            score += 10.0  # 能识别问题是好的

        # 针对代码实现阶段的特殊检查
        if stage == CognitiveStage.CORE_IMPLEMENTATION:
            score += self._evaluate_code_correctness(content)

        # 专业化加分
        if stage in self.preferred_stages:
            score += 10.0

        return min(100.0, score)

    def _evaluate_code_correctness(self, content: str) -> float:
        """评估代码正确性"""
        score = 0.0

        try:
            # 尝试解析Python代码
            if 'def ' in content:
                # 简单的语法检查
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('def '):
                        if ':' in line:
                            score += 5.0
                        if '(' in line and ')' in line:
                            score += 5.0

            # 检查基本编程结构
            if 'if ' in content and ':' in content:
                score += 5.0
            if 'for ' in content or 'while ' in content:
                score += 5.0
            if 'return ' in content:
                score += 5.0

        except Exception:
            pass  # 语法错误，分数为0

        return min(20.0, score)

    def _evaluate_efficiency(self, stage: CognitiveStage, output: StageOutputSchema) -> float:
        """评估效率"""
        content = output.content.lower()
        score = 50.0

        # 效率相关关键词
        efficiency_keywords = [
            'complexity', 'o(', 'time', 'space', 'performance',
            '复杂度', '性能', '效率', 'efficient', 'optimize'
        ]

        keyword_count = sum(1 for keyword in efficiency_keywords if keyword in content)
        score += min(30.0, keyword_count * 5.0)

        # 专业化加分
        if self.config.specialization in ['performance', 'algorithm']:
            score += 10.0

        # 算法选择阶段特殊评估
        if stage == CognitiveStage.ALGORITHM_SELECTION:
            if any(word in content for word in ['o(n)', 'o(log n)', 'o(1)']):
                score += 10.0

        return min(100.0, score)

    def _evaluate_completeness(self, stage: CognitiveStage, output: StageOutputSchema) -> float:
        """评估完整性"""
        content = output.content
        score = 30.0

        # 基于内容长度
        if len(content) > 1000:
            score += 30.0
        elif len(content) > 500:
            score += 20.0
        elif len(content) > 200:
            score += 10.0

        # 基于结构完整性
        if output.key_features and len(output.key_features) > 2:
            score += 15.0

        if output.suggestions and len(output.suggestions) > 0:
            score += 10.0

        # 专业指导遵循度
        specialization_keywords = {
            'algorithm': ['algorithm', 'complexity', '算法'],
            'architecture': ['architecture', 'component', 'module', '架构'],
            'performance': ['performance', 'optimization', '性能'],
            'security': ['security', 'vulnerability', '安全'],
            'testing': ['test', 'testing', '测试']
        }

        if self.config.specialization in specialization_keywords:
            keywords = specialization_keywords[self.config.specialization]
            if any(keyword in content.lower() for keyword in keywords):
                score += 15.0

        return min(100.0, score)

    def _evaluate_maintainability(self, stage: CognitiveStage, output: StageOutputSchema) -> float:
        """评估可维护性"""
        content = output.content.lower()
        score = 40.0

        # 可维护性关键词
        maintainability_keywords = [
            'modular', 'clean', 'readable', 'documentation',
            'comment', 'maintainable', '可维护', '模块化', '注释'
        ]

        keyword_count = sum(1 for keyword in maintainability_keywords if keyword in content)
        score += min(25.0, keyword_count * 5.0)

        # 代码实现阶段特殊检查
        if stage == CognitiveStage.CORE_IMPLEMENTATION:
            if '"""' in output.content or "'''" in output.content:  # 文档字符串
                score += 15.0
            if '#' in output.content:  # 注释
                score += 10.0

        # 架构设计专业化加分
        if self.config.specialization == 'architecture':
            score += 10.0

        return min(100.0, score)

    def _evaluate_security(self, stage: CognitiveStage, output: StageOutputSchema) -> float:
        """评估安全性"""
        content = output.content.lower()
        score = 70.0  # 默认较高分，除非发现问题

        # 安全相关关键词（正面）
        security_keywords = [
            'validation', 'sanitize', 'secure', 'encryption',
            'authentication', 'authorization', '验证', '安全'
        ]

        keyword_count = sum(1 for keyword in security_keywords if keyword in content)
        score += min(20.0, keyword_count * 3.0)

        # 安全问题检测（负面）
        security_issues = [
            'eval(', 'exec(', 'input(', 'raw_input(',
            'sql', 'shell', 'command'
        ]

        issue_count = sum(1 for issue in security_issues if issue in content)
        score -= issue_count * 10.0

        # 安全专家加分
        if self.config.specialization == 'security':
            score += 10.0

        return max(0.0, min(100.0, score))

    def _calculate_confidence(
        self,
        stage: CognitiveStage,
        output: StageOutputSchema,
        quality_metrics: QualityMetrics
    ) -> float:
        """计算置信度"""
        base_confidence = 0.6  # 基础置信度

        # 基于质量得分调整
        quality_factor = quality_metrics.overall_score / 100.0
        confidence = base_confidence + (quality_factor * 0.3)

        # 基于内容长度调整
        content_length = len(output.content)
        if content_length > 500:
            confidence += 0.1
        elif content_length < 100:
            confidence -= 0.1

        # 基于专业匹配度调整
        if stage in self.preferred_stages:
            confidence += 0.1

        # 基于推理质量调整
        if len(output.reasoning) > 100:
            confidence += 0.05

        # 基于问题识别能力调整
        if output.potential_issues:
            confidence += 0.05

        return max(0.1, min(0.95, confidence))

    def _create_fallback_output(self, stage: CognitiveStage, context: Dict, error_msg: str) -> StageOutput:
        """创建降级输出"""
        fallback_content = f"由于处理过程中遇到错误，提供基础的{stage.value}输出。\n错误信息: {error_msg}"

        return StageOutput(
            stage=stage,
            worker_id=self.worker_id,
            content=fallback_content,
            confidence=0.3,
            quality_metrics=QualityMetrics(
                creativity=30.0,
                correctness=40.0,
                efficiency=30.0,
                completeness=30.0,
                maintainability=40.0,
                security=50.0
            ),
            reasoning="处理过程中遇到错误，生成降级输出",
            metadata={
                'is_fallback': True,
                'error': error_msg,
                'specialization': self.config.specialization
            }
        )

    def _update_stats(self, stage_output: StageOutput, processing_time: float):
        """更新统计信息"""
        self.stats['stages_processed'] += 1
        self.stats['processing_times'].append(processing_time)

        # 更新平均质量得分
        current_avg = self.stats['avg_quality_score']
        new_score = stage_output.quality_metrics.overall_score
        self.stats['avg_quality_score'] = (
            (current_avg * (self.stats['stages_processed'] - 1) + new_score) /
            self.stats['stages_processed']
        )

        # 更新平均置信度
        current_conf = self.stats['avg_confidence']
        new_conf = stage_output.confidence
        self.stats['avg_confidence'] = (
            (current_conf * (self.stats['stages_processed'] - 1) + new_conf) /
            self.stats['stages_processed']
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.stats['processing_times']:
            return self.stats

        import statistics
        times = self.stats['processing_times']

        return {
            **self.stats,
            'avg_processing_time': statistics.mean(times),
            'min_processing_time': min(times),
            'max_processing_time': max(times),
            'total_processing_time': sum(times)
        }

    def is_suitable_for_stage(self, stage: CognitiveStage) -> bool:
        """判断是否适合处理该阶段"""
        if stage in self.preferred_stages:
            return True

        # 基于专业化的适合度
        specialization_suitability = {
            WorkerSpecialization.ALGORITHM: [
                CognitiveStage.ALGORITHM_SELECTION,
                CognitiveStage.CORE_IMPLEMENTATION,
                CognitiveStage.PERFORMANCE_OPTIMIZATION
            ],
            WorkerSpecialization.ARCHITECTURE: [
                CognitiveStage.REQUIREMENT_ANALYSIS,
                CognitiveStage.ARCHITECTURE_DESIGN,
                CognitiveStage.INTERFACE_DESIGN
            ],
            WorkerSpecialization.PERFORMANCE: [
                CognitiveStage.ALGORITHM_SELECTION,
                CognitiveStage.PERFORMANCE_OPTIMIZATION,
                CognitiveStage.CORE_IMPLEMENTATION
            ],
            WorkerSpecialization.SECURITY: [
                CognitiveStage.REQUIREMENT_ANALYSIS,
                CognitiveStage.ERROR_HANDLING,
                CognitiveStage.CORE_IMPLEMENTATION
            ],
            WorkerSpecialization.TESTING: [
                CognitiveStage.TESTING_STRATEGY,
                CognitiveStage.INTERFACE_DESIGN,
                CognitiveStage.INTEGRATION
            ]
        }

        suitable_stages = specialization_suitability.get(self.config.specialization, [])
        return stage in suitable_stages

    def __str__(self) -> str:
        return f"WorkerAgent({self.worker_id}, specialization={self.config.specialization})"

    def __repr__(self) -> str:
        return self.__str__()


# Factory function for creating specialized workers
def create_worker_team(models_config: List[Dict[str, Any]]) -> List[WorkerAgent]:
    """创建专业化的Worker团队"""
    workers = []

    specializations = [
        WorkerSpecialization.ALGORITHM,
        WorkerSpecialization.ARCHITECTURE,
        WorkerSpecialization.PERFORMANCE,
        WorkerSpecialization.SECURITY,
        WorkerSpecialization.TESTING,
        WorkerSpecialization.GENERAL
    ]

    for i, model_config in enumerate(models_config):
        specialization = specializations[i % len(specializations)]

        # 创建LLM实例
        llm = StructuredLLM(
            model=model_config.get('model', 'gpt-4o'),
            api_key=model_config.get('api_key'),
            base_url=model_config.get('base_url')
        )

        # 创建Worker配置
        worker_config = WorkerConfig(
            model_name=model_config.get('model', 'gpt-4o'),
            specialization=specialization,
            temperature=model_config.get('temperature', 0.3),
            max_tokens=model_config.get('max_tokens', 2000)
        )

        # 创建Worker
        worker = WorkerAgent(llm, worker_config)
        workers.append(worker)

    logger.info(f"创建了 {len(workers)} 个专业化Worker")
    return workers
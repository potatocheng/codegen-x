"""多模型协作机制

通过使用多个LLM模型生成不同的代码实现，然后通过质量评估选择最佳实现。
这种方法可以克服单一模型的局限性，提高代码生成的质量和多样性。
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm.structured_llm import StructuredLLM
from tools.spec_tool import FunctionSpec
from tools.implement_tool import ImplementTool, Implementation
from tools.validate_tool import ValidateTool
from tools.quality_checker import CodeQualityChecker, QualityMetrics
from tools.performance_benchmark import PerformanceBenchmark


@dataclass
class ModelImplementation:
    """单个模型的实现结果"""
    model_name: str
    implementation: Implementation
    validation_result: Any  # ValidationResult
    quality_metrics: QualityMetrics
    performance_result: Any  # PerformanceResult
    overall_score: float


@dataclass
class CollaborationResult:
    """协作结果"""
    best_implementation: ModelImplementation
    all_implementations: List[ModelImplementation]
    consensus_score: float  # 模型间一致性分数
    diversity_score: float  # 实现多样性分数
    selection_reason: str   # 选择最佳实现的原因


class MultiModelCollaborator:
    """多模型协作器"""

    def __init__(self, models_config: Dict[str, Dict[str, Any]]):
        """
        Args:
            models_config: 模型配置字典
            格式: {
                "model1": {"model": "gpt-4o", "api_key": "...", "base_url": "..."},
                "model2": {"model": "deepseek-coder", "api_key": "...", "base_url": "..."},
            }
        """
        self.models_config = models_config
        self.quality_checker = CodeQualityChecker()
        self.benchmark = PerformanceBenchmark()
        self.validate_tool = ValidateTool()

        # 初始化LLM实例
        self.llms = {}
        for name, config in models_config.items():
            try:
                self.llms[name] = StructuredLLM(
                    model=config["model"],
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url")
                )
            except Exception as e:
                print(f"初始化模型 {name} 失败: {e}")

    def collaborate_generate(
        self,
        spec: FunctionSpec,
        style: str = "concise",
        max_workers: int = 3
    ) -> CollaborationResult:
        """多模型协作生成代码

        Args:
            spec: 函数规范
            style: 代码风格
            max_workers: 最大并行工作线程数

        Returns:
            协作结果
        """
        implementations = []

        # 并行生成实现
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_model = {}
            for model_name, llm in self.llms.items():
                future = executor.submit(
                    self._generate_single_implementation,
                    model_name, llm, spec, style
                )
                future_to_model[future] = model_name

            # 收集结果
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    impl = future.result(timeout=120)  # 2分钟超时
                    if impl:
                        implementations.append(impl)
                except Exception as e:
                    print(f"模型 {model_name} 生成失败: {e}")

        if not implementations:
            raise RuntimeError("所有模型都生成失败")

        # 选择最佳实现
        best_impl = self._select_best_implementation(implementations)

        # 计算协作指标
        consensus_score = self._calculate_consensus_score(implementations)
        diversity_score = self._calculate_diversity_score(implementations)

        return CollaborationResult(
            best_implementation=best_impl,
            all_implementations=implementations,
            consensus_score=consensus_score,
            diversity_score=diversity_score,
            selection_reason=self._explain_selection(best_impl, implementations)
        )

    def _generate_single_implementation(
        self,
        model_name: str,
        llm: StructuredLLM,
        spec: FunctionSpec,
        style: str
    ) -> Optional[ModelImplementation]:
        """单个模型生成实现"""
        try:
            # 生成代码
            impl_tool = ImplementTool(llm)
            impl_result = impl_tool.execute(
                impl_tool.input_schema(spec=spec, style=style)
            )

            if not impl_result.success:
                return None

            implementation = impl_result.data

            # 验证代码
            validation_result = self.validate_tool.execute(
                self.validate_tool.input_schema(
                    code=implementation.code,
                    spec=spec
                )
            ).data

            # 质量检查
            quality_metrics = self.quality_checker.analyze_code(
                implementation.code,
                spec.name
            )

            # 性能测试
            test_cases = [
                {"inputs": example.inputs, "expected": example.expected_output}
                for example in spec.examples
            ]

            performance_result = None
            if test_cases:
                try:
                    performance_result = self.benchmark.benchmark_code_string(
                        implementation.code,
                        spec.name,
                        test_cases,
                        runs=3
                    )
                except:
                    pass

            # 计算综合得分
            overall_score = self._calculate_overall_score(
                validation_result,
                quality_metrics,
                performance_result
            )

            return ModelImplementation(
                model_name=model_name,
                implementation=implementation,
                validation_result=validation_result,
                quality_metrics=quality_metrics,
                performance_result=performance_result,
                overall_score=overall_score
            )

        except Exception as e:
            print(f"模型 {model_name} 实现过程出错: {e}")
            return None

    def _calculate_overall_score(
        self,
        validation_result: Any,
        quality_metrics: QualityMetrics,
        performance_result: Any
    ) -> float:
        """计算综合得分"""
        score = 0.0

        # 功能正确性权重 40%
        if validation_result and validation_result.is_valid:
            score += 40.0
        elif validation_result:
            # 部分通过的测试也给一些分数
            pass_rate = validation_result.passed_count / max(validation_result.total_tests, 1)
            score += 40.0 * pass_rate

        # 代码质量权重 35%
        score += (quality_metrics.overall_score / 100) * 35.0

        # 性能权重 25%
        if performance_result and performance_result.avg_time != float('inf'):
            # 基于执行时间给分（越快分数越高）
            if performance_result.avg_time < 0.001:  # 小于1ms
                score += 25.0
            elif performance_result.avg_time < 0.01:  # 小于10ms
                score += 20.0
            elif performance_result.avg_time < 0.1:   # 小于100ms
                score += 15.0
            else:
                score += 10.0

        return score

    def _select_best_implementation(
        self,
        implementations: List[ModelImplementation]
    ) -> ModelImplementation:
        """选择最佳实现"""
        # 首先过滤出功能正确的实现
        valid_implementations = [
            impl for impl in implementations
            if impl.validation_result and impl.validation_result.is_valid
        ]

        if valid_implementations:
            # 如果有功能正确的实现，选择综合得分最高的
            return max(valid_implementations, key=lambda x: x.overall_score)
        else:
            # 如果没有完全正确的实现，选择通过测试最多的
            return max(implementations, key=lambda x: (
                x.validation_result.passed_count if x.validation_result else 0,
                x.overall_score
            ))

    def _calculate_consensus_score(
        self,
        implementations: List[ModelImplementation]
    ) -> float:
        """计算模型间一致性分数

        基于不同模型对于相同问题的解决方案的相似性
        """
        if len(implementations) < 2:
            return 1.0

        # 计算功能正确性的一致性
        correctness_scores = [
            1.0 if impl.validation_result and impl.validation_result.is_valid else 0.0
            for impl in implementations
        ]

        # 计算质量评分的一致性
        quality_scores = [impl.quality_metrics.overall_score for impl in implementations]

        # 使用变异系数衡量一致性（越小越一致）
        correctness_consensus = 1.0 - (statistics.stdev(correctness_scores) if len(set(correctness_scores)) > 1 else 0.0)

        if len(set(quality_scores)) > 1:
            quality_cv = statistics.stdev(quality_scores) / statistics.mean(quality_scores)
            quality_consensus = max(0.0, 1.0 - quality_cv)
        else:
            quality_consensus = 1.0

        return (correctness_consensus + quality_consensus) / 2

    def _calculate_diversity_score(
        self,
        implementations: List[ModelImplementation]
    ) -> float:
        """计算实现多样性分数

        基于不同实现在代码结构、算法选择等方面的差异性
        """
        if len(implementations) < 2:
            return 0.0

        # 简单的多样性计算：基于代码长度和复杂度的差异
        code_lengths = [len(impl.implementation.code) for impl in implementations]
        complexities = [impl.quality_metrics.cyclomatic_complexity for impl in implementations]

        # 使用变异系数衡量多样性（越大越多样）
        length_cv = statistics.stdev(code_lengths) / statistics.mean(code_lengths) if statistics.mean(code_lengths) > 0 else 0
        complexity_cv = statistics.stdev(complexities) / statistics.mean(complexities) if statistics.mean(complexities) > 0 else 0

        # 归一化多样性分数
        diversity = min(1.0, (length_cv + complexity_cv) / 2)
        return diversity

    def _explain_selection(
        self,
        best_impl: ModelImplementation,
        all_implementations: List[ModelImplementation]
    ) -> str:
        """解释选择最佳实现的原因"""
        reasons = []

        # 功能正确性
        if best_impl.validation_result and best_impl.validation_result.is_valid:
            reasons.append("通过所有功能测试")
        elif best_impl.validation_result:
            pass_rate = best_impl.validation_result.passed_count / max(best_impl.validation_result.total_tests, 1)
            reasons.append(f"通过{pass_rate:.1%}的功能测试（最高）")

        # 代码质量
        if best_impl.quality_metrics.overall_score >= 80:
            reasons.append("代码质量优秀")
        elif best_impl.quality_metrics.overall_score >= 60:
            reasons.append("代码质量良好")

        # 性能
        if (best_impl.performance_result and
            best_impl.performance_result.avg_time != float('inf') and
            best_impl.performance_result.avg_time < 0.01):
            reasons.append("执行性能优异")

        # 模型信息
        reasons.append(f"由模型 {best_impl.model_name} 生成")

        return "；".join(reasons)

    def get_collaboration_summary(self, result: CollaborationResult) -> Dict[str, Any]:
        """获取协作总结"""
        return {
            "best_model": result.best_implementation.model_name,
            "best_score": result.best_implementation.overall_score,
            "models_tested": len(result.all_implementations),
            "consensus_score": result.consensus_score,
            "diversity_score": result.diversity_score,
            "selection_reason": result.selection_reason,
            "all_scores": {
                impl.model_name: impl.overall_score
                for impl in result.all_implementations
            }
        }


# 使用示例
if __name__ == "__main__":
    # 配置多个模型
    models_config = {
        "gpt-4o": {
            "model": "gpt-4o-2024-08-06",
            "api_key": "your-openai-key"
        },
        "deepseek": {
            "model": "deepseek-coder",
            "api_key": "your-deepseek-key",
            "base_url": "https://api.deepseek.com"
        }
    }

    # 创建协作器
    collaborator = MultiModelCollaborator(models_config)

    # 示例规范
    from tools.spec_tool import FunctionSpec, Example

    spec = FunctionSpec(
        name="binary_search",
        purpose="在有序数组中查找目标值",
        parameters={
            "arr": "有序整数数组",
            "target": "要查找的目标值"
        },
        return_type="int",
        return_description="目标值的索引，如果不存在则返回-1",
        examples=[
            Example(
                inputs={"arr": [1, 2, 3, 4, 5], "target": 3},
                expected_output=2,
                description="查找存在的元素"
            ),
            Example(
                inputs={"arr": [1, 2, 3, 4, 5], "target": 6},
                expected_output=-1,
                description="查找不存在的元素"
            )
        ],
        edge_cases=["空数组", "单元素数组", "目标值在边界"],
        constraints=["数组已排序", "时间复杂度O(log n)"]
    )

    # 进行协作生成
    result = collaborator.collaborate_generate(spec)

    # 输出结果
    summary = collaborator.get_collaboration_summary(result)
    print("协作生成结果:", json.dumps(summary, indent=2, ensure_ascii=False))
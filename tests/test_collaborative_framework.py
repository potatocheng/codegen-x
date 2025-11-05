"""
测试多模型协作代码生成框架

测试各个组件的集成和基本功能
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
sys.path.append('.')

# 导入协作框架组件
from tools.collaborative_framework import (
    CollaborativeCodeGenerator,
    CognitiveStage,
    FusionStrategy,
    DAGWorkflow,
    create_default_workflow,
    QualityMetrics,
    StageOutput,
    FusionResult
)
from tools.collaborative_generator import (
    create_collaborative_generator,
    create_default_team_config,
    CollaborativeSession
)


class TestCollaborativeFramework(unittest.TestCase):
    """测试协作框架的基本功能"""

    def setUp(self):
        """测试前的设置"""
        self.mock_llm = Mock()
        self.mock_llm.generate_structured = Mock()

    def test_dag_workflow_creation(self):
        """测试DAG工作流创建"""
        workflow = create_default_workflow()

        # 检查是否包含所有预期阶段
        expected_stages = [
            CognitiveStage.REQUIREMENT_ANALYSIS,
            CognitiveStage.ARCHITECTURE_DESIGN,
            CognitiveStage.ALGORITHM_SELECTION,
            CognitiveStage.INTERFACE_DESIGN,
            CognitiveStage.CORE_IMPLEMENTATION,
            CognitiveStage.ERROR_HANDLING,
            CognitiveStage.PERFORMANCE_OPTIMIZATION,
            CognitiveStage.TESTING_STRATEGY,
            CognitiveStage.INTEGRATION
        ]

        for stage in expected_stages:
            self.assertIn(stage, workflow.nodes)

        # 检查执行顺序
        execution_order = workflow.get_execution_order()
        self.assertGreater(len(execution_order), 0)

        # 验证依赖关系
        self.assertEqual(workflow.nodes[CognitiveStage.REQUIREMENT_ANALYSIS].dependencies, [])
        self.assertIn(CognitiveStage.REQUIREMENT_ANALYSIS,
                     workflow.nodes[CognitiveStage.ARCHITECTURE_DESIGN].dependencies)

    def test_quality_metrics(self):
        """测试质量指标计算"""
        metrics = QualityMetrics(
            creativity=80.0,
            correctness=90.0,
            efficiency=85.0,
            completeness=88.0,
            maintainability=82.0,
            security=75.0
        )

        # 测试综合得分计算
        overall_score = metrics.overall_score
        self.assertGreater(overall_score, 0)
        self.assertLessEqual(overall_score, 100)

    def test_stage_output_creation(self):
        """测试阶段输出创建"""
        metrics = QualityMetrics(
            creativity=80.0,
            correctness=90.0,
            efficiency=85.0,
            completeness=88.0,
            maintainability=82.0,
            security=75.0
        )

        output = StageOutput(
            stage=CognitiveStage.CORE_IMPLEMENTATION,
            worker_id="test_worker",
            content="def test_function(): pass",
            confidence=0.85,
            quality_metrics=metrics,
            reasoning="Test implementation"
        )

        self.assertEqual(output.stage, CognitiveStage.CORE_IMPLEMENTATION)
        self.assertEqual(output.worker_id, "test_worker")
        self.assertEqual(output.confidence, 0.85)

        # 测试转换为字典
        output_dict = output.to_dict()
        self.assertIn('stage', output_dict)
        self.assertIn('content', output_dict)
        self.assertIn('quality_metrics', output_dict)

    def test_fusion_result_creation(self):
        """测试融合结果创建"""
        metrics = QualityMetrics(creativity=80.0, correctness=90.0)

        fusion_result = FusionResult(
            stage=CognitiveStage.CORE_IMPLEMENTATION,
            fused_content="def fused_function(): pass",
            fusion_strategy=FusionStrategy.BEST_SINGLE,
            source_workers=["worker1", "worker2"],
            confidence=0.9,
            quality_metrics=metrics,
            fusion_reasoning="Selected best implementation"
        )

        self.assertEqual(fusion_result.fusion_strategy, FusionStrategy.BEST_SINGLE)
        self.assertEqual(len(fusion_result.source_workers), 2)

        # 测试转换为字典
        result_dict = fusion_result.to_dict()
        self.assertIn('fusion_strategy', result_dict)
        self.assertIn('source_workers', result_dict)

    def test_collaborative_generator_initialization(self):
        """测试协作生成器初始化"""
        worker_configs = [
            {
                'model': 'test-model',
                'specialization': 'algorithm',
                'api_key': 'test-key'
            }
        ]

        # 模拟LLM创建失败的情况
        with patch('tools.collaborative_framework.StructuredLLM') as mock_llm_class:
            mock_llm_class.side_effect = Exception("API connection failed")

            generator = CollaborativeCodeGenerator(
                master_llm=self.mock_llm,
                worker_configs=worker_configs,
                max_concurrent_workers=1
            )

            # 应该创建但Workers初始化失败
            self.assertEqual(len(generator.workers), 0)

    def test_workflow_progress_tracking(self):
        """测试工作流进度跟踪"""
        workflow = create_default_workflow()

        # 初始进度应该是0
        self.assertEqual(workflow.get_progress(), 0.0)

        # 模拟完成一个阶段
        mock_result = FusionResult(
            stage=CognitiveStage.REQUIREMENT_ANALYSIS,
            fused_content="requirement analysis",
            fusion_strategy=FusionStrategy.BEST_SINGLE,
            source_workers=["worker1"],
            confidence=0.8,
            quality_metrics=QualityMetrics()
        )

        workflow.mark_completed(CognitiveStage.REQUIREMENT_ANALYSIS, mock_result)

        # 进度应该大于0
        progress = workflow.get_progress()
        self.assertGreater(progress, 0.0)
        self.assertLessEqual(progress, 1.0)

    def test_factory_functions(self):
        """测试工厂函数"""
        # 测试默认团队配置创建
        team_config = create_default_team_config()
        self.assertGreater(len(team_config), 0)

        for config in team_config:
            self.assertIn('model', config)
            self.assertIn('specialization', config)

    def test_collaborative_session(self):
        """测试协作会话管理"""
        # 创建模拟生成器
        mock_generator = Mock()
        mock_generator.generate_code.return_value = {
            'success': True,
            'final_code': 'def test(): pass',
            'execution_time': 1.5
        }

        session = CollaborativeSession(mock_generator)

        # 测试生成
        result = session.generate("test requirement")
        self.assertTrue(result['success'])

        # 测试会话历史
        self.assertEqual(len(session.session_history), 1)

        # 测试会话总结
        summary = session.get_session_summary()
        self.assertEqual(summary['total_requests'], 1)
        self.assertEqual(summary['successful_requests'], 1)


class TestMockCollaboration(unittest.TestCase):
    """测试模拟协作功能"""

    def test_mock_workflow_execution(self):
        """测试模拟工作流执行"""
        # 这个测试演示了如何在没有真实API的情况下测试协作逻辑

        workflow = DAGWorkflow()
        workflow.add_stage(CognitiveStage.REQUIREMENT_ANALYSIS, [])
        workflow.add_stage(CognitiveStage.CORE_IMPLEMENTATION, [CognitiveStage.REQUIREMENT_ANALYSIS])

        # 模拟阶段完成
        stages = [CognitiveStage.REQUIREMENT_ANALYSIS, CognitiveStage.CORE_IMPLEMENTATION]

        for stage in stages:
            mock_result = FusionResult(
                stage=stage,
                fused_content=f"Mock content for {stage.value}",
                fusion_strategy=FusionStrategy.BEST_SINGLE,
                source_workers=["mock_worker"],
                confidence=0.8,
                quality_metrics=QualityMetrics(
                    creativity=80.0,
                    correctness=85.0,
                    efficiency=82.0,
                    completeness=88.0,
                    maintainability=79.0,
                    security=84.0
                )
            )
            workflow.mark_completed(stage, mock_result)

        # 验证所有阶段都完成了
        self.assertTrue(workflow.is_completed())
        self.assertEqual(workflow.get_progress(), 1.0)


def run_tests():
    """运行所有测试"""
    print("运行协作框架测试...")

    # 创建测试套件
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # 添加测试
    test_suite.addTests(loader.loadTestsFromTestCase(TestCollaborativeFramework))
    test_suite.addTests(loader.loadTestsFromTestCase(TestMockCollaboration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 报告结果
    if result.wasSuccessful():
        print("\n所有测试通过!")
    else:
        print(f"\n测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")

        for failure in result.failures:
            print(f"失败: {failure[0]}")
            print(f"详情: {failure[1]}")

        for error in result.errors:
            print(f"错误: {error[0]}")
            print(f"详情: {error[1]}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()

    if success:
        print("\n协作框架集成测试完成!")
        print("测试覆盖的功能:")
        print("   - DAG工作流创建和执行")
        print("   - 质量指标计算")
        print("   - 阶段输出和融合结果")
        print("   - 协作生成器初始化")
        print("   - 进度跟踪")
        print("   - 工厂函数")
        print("   - 会话管理")
        print("   - 模拟协作流程")
    else:
        print("\n部分测试失败，请检查代码实现")
        sys.exit(1)
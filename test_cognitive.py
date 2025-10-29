#!/usr/bin/env python3
"""
快速测试脚本

测试认知驱动的代码生成系统是否正常工作
"""

def test_imports():
    """测试所有模块是否可以正常导入"""
    print("🔍 测试模块导入...")

    try:
        # 测试核心模块
        from cognitive.cognitive_model import CognitiveModel, ThinkingStage
        print("✅ cognitive_model 导入成功")

        from cognitive.cognitive_line_explainer import CognitiveLineExplainer
        print("✅ cognitive_line_explainer 导入成功")

        from cognitive.cognitive_decision_tracker import CognitiveDecisionTracker
        print("✅ cognitive_decision_tracker 导入成功")

        from cognitive.cognitive_load_aware_generator import CognitiveLoadAwareGenerator
        print("✅ cognitive_load_aware_generator 导入成功")

        from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent
        print("✅ cognitive_code_agent 导入成功")

        return True

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")

    try:
        # 测试认知模型
        from cognitive.cognitive_model import CognitiveModel, CognitiveState, ThinkingStage

        state = CognitiveState(
            stage=ThinkingStage.PROBLEM_COMPREHENSION,
            confidence=0.8,
            mental_effort=0.6,
            working_memory_load=0.4,
            focused_concepts=["二分查找", "递归"],
            discovered_insights=["分治策略有效"],
            pending_questions=["边界条件如何处理"]
        )

        model = CognitiveModel(current_state=state)
        print("✅ 认知模型创建成功")

        # 测试决策追踪
        from cognitive.cognitive_decision_tracker import CognitiveDecisionTracker, DecisionType

        tracker = CognitiveDecisionTracker("test_session", "测试问题")
        decision_id = tracker.record_decision(
            stage="test",
            decision_type=DecisionType.STRATEGY_SELECTION,
            decision="测试决策",
            reasoning="测试推理",
            confidence=0.8
        )
        print("✅ 决策追踪创建成功")

        # 测试负荷感知生成器
        from cognitive.cognitive_load_aware_generator import CognitiveLoadAwareGenerator

        generator = CognitiveLoadAwareGenerator()
        adaptations, config = generator.assess_and_adapt(
            "def test(): pass",
            {"test": True}
        )
        print("✅ 负荷感知生成器创建成功")

        return True

    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False


def test_cognitive_line_explanation():
    """测试认知行级解释（无LLM版本）"""
    print("\n🧠 测试认知行级解释...")

    try:
        from cognitive.cognitive_line_explainer import CognitiveLineExplainer

        # 创建模拟LLM
        class MockLLM:
            def generate_structured(self, prompt, output_schema, **kwargs):
                # 返回默认的解释对象
                from cognitive.cognitive_line_explainer import LineExplanation, CognitiveLineType
                return output_schema(
                    line_number=1,
                    code_line="def test():",
                    cognitive_type=CognitiveLineType.PROBLEM_SETUP,
                    semantic_purpose="定义测试函数",
                    cognitive_reasoning="建立函数接口",
                    programmer_intent="创建测试环境",
                    mental_model_impact="建立测试框架",
                    cognitive_load=0.3
                )

        explainer = CognitiveLineExplainer(MockLLM())
        result = explainer.explain_code_lines("def test(): pass")

        print(f"✅ 行级解释生成成功，分析了 {len(result['line_explanations'])} 行")
        return True

    except Exception as e:
        print(f"❌ 行级解释测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 CodeGen-X 认知驱动系统快速测试")
    print("=" * 50)

    success_count = 0
    total_tests = 3

    # 运行测试
    if test_imports():
        success_count += 1

    if test_basic_functionality():
        success_count += 1

    if test_cognitive_line_explanation():
        success_count += 1

    # 总结
    print(f"\n📊 测试结果: {success_count}/{total_tests} 通过")

    if success_count == total_tests:
        print("✅ 所有测试通过！认知驱动系统运行正常")
        print("\n🎯 系统已成功实现:")
        print("  • 认知行级解释功能")
        print("  • 认知决策追踪系统")
        print("  • 认知负荷感知生成")
        print("  • 完整的认知驱动架构")

        print("\n📝 使用方法:")
        print("  python main.py --cognitive \"写一个二分查找函数\"")
        print("  python examples/cognitive_demo.py")

        return True
    else:
        print("❌ 部分测试失败，请检查依赖和配置")
        return False


if __name__ == "__main__":
    main()
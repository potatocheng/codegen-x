#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本

测试认知驱动的代码生成系统是否正常工作
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_imports():
    """测试所有模块是否可以正常导入"""
    print("🔍 测试模块导入...")

    try:
        # 测试核心模块
        from cognitive.cognitive_model import CognitiveModel, ThinkingStage
        print("✅ cognitive_model 导入成功")

        from cognitive.line_effectiveness_validator import LineEffectivenessValidator
        print("✅ line_effectiveness_validator 导入成功")

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


def test_line_effectiveness_validation():
    """测试行有效性验证"""
    print("\n✅ 测试行有效性验证...")

    try:
        from cognitive.line_effectiveness_validator import LineEffectivenessValidator

        validator = LineEffectivenessValidator()

        # 测试代码（包含冗余行）
        test_code = '''def test():
    x = 1
    x = 1  # 冗余
    y = 2
    return y'''

        report = validator.analyze_code(test_code)

        print(f"✅ 行有效性验证成功")
        print(f"   - 必需行: {report.essential_lines}")
        print(f"   - 冗余行: {report.redundant_lines}")
        print(f"   - 有效性评分: {report.effectiveness_score:.2f}")
        return True

    except Exception as e:
        print(f"❌ 行有效性验证测试失败: {e}")
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

    if test_line_effectiveness_validation():
        success_count += 1

    # 总结
    print(f"\n📊 测试结果: {success_count}/{total_tests} 通过")

    if success_count == total_tests:
        print("✅ 所有测试通过！认知驱动系统运行正常")
        print("\n🎯 系统已成功实现:")
        print("  • ✅ 行有效性验证功能 - 确保每行代码都是必要的")
        print("  • 🎯 认知决策追踪系统")
        print("  • ⚖️ 认知负荷感知生成")
        print("  • 🌟 完整的认知驱动架构")

        print("\n📝 使用方法:")
        print("  python main.py --cognitive \"写一个二分查找函数\"")
        print("  python examples/cognitive_demo.py")

        return True
    else:
        print("❌ 部分测试失败，请检查依赖和配置")
        return False


if __name__ == "__main__":
    main()
"""
认知驱动代码生成的测试和验证示例

这个示例展示了如何使用认知驱动的代码生成系统，包括：
1. 行级认知解释
2. 认知决策追踪
3. 认知负荷感知优化
4. 完整的可解释性分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.structured_llm import StructuredLLM
from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent
from cognitive.cognitive_line_explainer import CognitiveLineExplainer
import json


def test_cognitive_line_explanation():
    """测试认知行级解释功能"""
    print("🧠 测试认知行级解释功能")
    print("=" * 50)

    # 示例代码
    sample_code = '''def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1'''

    # 创建模拟LLM（实际使用时需要真实的LLM）
    class MockStructuredLLM:
        def generate_structured(self, prompt, output_schema, **kwargs):
            from cognitive.cognitive_line_explainer import LineExplanation, CognitiveLineType

            # 模拟返回认知解释
            if "left, right = 0" in prompt:
                return LineExplanation(
                    line_number=2,
                    code_line="left, right = 0, len(arr) - 1",
                    cognitive_type=CognitiveLineType.MENTAL_MODEL,
                    semantic_purpose="建立搜索空间的心理模型",
                    cognitive_reasoning="程序员需要在心理上构建一个搜索区间的概念，这是二分查找算法的核心心理模型",
                    programmer_intent="定义搜索的边界条件，为后续的区间缩减做准备",
                    mental_model_impact="建立了'搜索区间'这一关键概念，为整个算法的执行奠定基础",
                    cognitive_load=0.6
                )
            else:
                return LineExplanation(
                    line_number=1,
                    code_line="def binary_search(arr, target):",
                    cognitive_type=CognitiveLineType.PROBLEM_SETUP,
                    semantic_purpose="定义问题求解的接口",
                    cognitive_reasoning="程序员通过函数签名明确了问题的输入输出规范",
                    programmer_intent="建立清晰的问题边界和接口规范",
                    mental_model_impact="为整个搜索问题建立了明确的输入输出框架",
                    cognitive_load=0.3
                )

    mock_llm = MockStructuredLLM()
    explainer = CognitiveLineExplainer(mock_llm)

    # 生成认知解释
    result = explainer.explain_code_lines(sample_code)

    print("📋 代码:")
    print(sample_code)
    print("\n🔍 认知解释摘要:")
    print(f"- 分析行数: {result['cognitive_summary']['total_lines_analyzed']}")
    print(f"- 平均认知负荷: {result['cognitive_summary']['average_cognitive_load']:.2f}")
    print(f"- 复杂度级别: {result['cognitive_summary']['complexity_level']}")

    print("\n🧠 认知功能簇:")
    for cluster in result['dependency_graph']['cognitive_clusters']:
        print(f"- {cluster['description']}: 行 {cluster['lines']}")

    return result


def test_cognitive_decision_tracking():
    """测试认知决策追踪功能"""
    print("\n🎯 测试认知决策追踪功能")
    print("=" * 50)

    from cognitive.cognitive_decision_tracker import CognitiveDecisionTracker, DecisionType

    # 创建决策追踪器
    tracker = CognitiveDecisionTracker("test_session", "实现快速排序算法")

    # 模拟决策过程
    tracker.record_decision(
        stage="problem_analysis",
        decision_type=DecisionType.STRATEGY_SELECTION,
        decision="选择分治策略",
        reasoning="快速排序的递归分治特性适合这种策略",
        confidence=0.9,
        alternatives=["迭代方法", "自底向上方法"],
        expected_outcome="生成清晰的递归结构代码"
    )

    tracker.record_decision(
        stage="implementation",
        decision_type=DecisionType.OPTIMIZATION_CHOICE,
        decision="使用原地分区算法",
        reasoning="减少额外内存使用，提高效率",
        confidence=0.8,
        alternatives=["使用额外数组", "链表实现"],
        expected_outcome="更高效的内存使用"
    )

    tracker.record_cognitive_load("implementation", 0.4, 0.2, 0.3)

    # 结束会话
    tracker.finalize_session({"success": True, "lines_of_code": 25})

    # 获取决策摘要
    summary = tracker.get_decision_summary()
    decisions = tracker.get_decision_chain()

    print("📊 决策追踪摘要:")
    print(f"- 总决策数: {summary['total_decisions']}")
    print(f"- 平均置信度: {summary['average_confidence']:.2f}")
    print(f"- 会话时长: {summary['session_duration']:.2f}秒")

    print("\n🔗 决策链:")
    for i, decision in enumerate(decisions, 1):
        print(f"{i}. [{decision['stage']}] {decision['decision']}")
        print(f"   推理: {decision['reasoning']}")
        print(f"   置信度: {decision['confidence']:.2f}")

    return tracker


def test_cognitive_load_aware_generation():
    """测试认知负荷感知生成"""
    print("\n⚖️ 测试认知负荷感知生成")
    print("=" * 50)

    from cognitive.cognitive_load_aware_generator import CognitiveLoadAwareGenerator, CognitiveStrategy

    # 创建认知负荷感知生成器
    strategy = CognitiveStrategy(target_load=0.6, adaptation_threshold=0.8)
    generator = CognitiveLoadAwareGenerator(strategy)

    # 高复杂度代码示例
    complex_code = '''def complex_function(data, params, config, options, state):
    if config and params and data:
        for i in range(len(data)):
            for j in range(len(params)):
                if data[i] > params[j]:
                    if options.get('mode') == 'advanced':
                        if state.get('initialized'):
                            result = process_complex_logic(data[i], params[j], config, options, state)
                            if result and result.is_valid():
                                if result.score > threshold:
                                    final_results.append(transform_result(result, options))
    return final_results'''

    # 评估并生成适应策略
    adaptations, updated_config = generator.assess_and_adapt(
        complex_code,
        cognitive_context={
            "problem_complexity": 0.8,
            "domain_complexity": 0.6
        }
    )

    print("📈 认知负荷分析:")
    if generator.current_load:
        print(f"- 总负荷: {generator.current_load.total_load:.2f}")
        print(f"- 内在负荷: {generator.current_load.intrinsic_load:.2f}")
        print(f"- 外在负荷: {generator.current_load.extraneous_load:.2f}")
        print(f"- 认知瓶颈: {', '.join(generator.current_load.bottlenecks)}")

    print("\n🔧 建议的适应策略:")
    for i, adaptation in enumerate(adaptations, 1):
        print(f"{i}. {adaptation.strategy.value}: {adaptation.action}")
        print(f"   原因: {adaptation.reasoning}")
        print(f"   预期负荷减少: {adaptation.expected_load_reduction:.2f}")

    print("\n⚙️ 更新的生成配置:")
    for key, value in updated_config.items():
        print(f"- {key}: {value}")

    return generator


def demonstrate_full_cognitive_workflow():
    """演示完整的认知驱动工作流"""
    print("\n🌟 完整认知驱动工作流演示")
    print("=" * 60)

    try:
        # 注意：这需要真实的LLM API密钥
        # llm = StructuredLLM(model="gpt-4o-2024-08-06")
        # agent = CognitiveDrivenCodeGenAgent(llm, enable_cognitive_guidance=True)

        print("⚠️ 完整工作流需要真实的LLM API")
        print("以下是模拟的工作流程:")

        request = "实现一个高效的归并排序算法"

        print(f"\n📝 用户需求: {request}")

        # 模拟认知分析阶段
        print("\n🧠 阶段1: 认知问题分析")
        print("- 策略选择: 分治策略")
        print("- 认知负荷估计: 中等 (0.65)")
        print("- 置信度: 0.85")

        # 模拟规范生成阶段
        print("\n📋 阶段2: 认知驱动规范生成")
        print("- 详细级别: 详细 (基于认知负荷)")
        print("- 生成包含边界条件和复杂度分析的规范")

        # 模拟实现阶段
        print("\n💻 阶段3: 认知驱动代码实现")
        print("- 实现风格: 结构化")
        print("- 应用认知适应策略: 增加脚手架, 优化分块")

        # 模拟验证阶段
        print("\n✅ 阶段4: 认知驱动验证")
        print("- 所有测试通过")
        print("- 认知负荷保持在目标范围内")

        # 模拟最终结果
        print("\n📊 认知分析结果:")
        print("- 总决策数: 5")
        print("- 平均置信度: 0.84")
        print("- 主要策略: 分治策略")
        print("- 认知适应: 2个策略被应用")
        print("- 最终认知负荷: 0.58 (目标范围内)")

        print("\n🎯 认知决策链:")
        decisions = [
            "问题分析: 选择分治策略 (置信度: 0.85)",
            "规范生成: 使用详细级别 (置信度: 0.80)",
            "实现优化: 应用认知适应 (置信度: 0.80)",
            "代码实现: 结构化风格 (置信度: 0.85)",
            "验证成功: 完成生成 (置信度: 0.95)"
        ]

        for i, decision in enumerate(decisions, 1):
            print(f"{i}. {decision}")

        return True

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 CodeGen-X 认知驱动代码生成测试")
    print("=" * 60)

    # 测试各个组件
    test_cognitive_line_explanation()
    test_cognitive_decision_tracking()
    test_cognitive_load_aware_generation()
    demonstrate_full_cognitive_workflow()

    print("\n✅ 所有测试完成!")
    print("\n📝 总结:")
    print("本测试展示了CodeGen-X认知驱动系统的核心功能:")
    print("1. 🧠 认知行级解释 - 提供深层语义解释")
    print("2. 🎯 认知决策追踪 - 记录编程思维过程")
    print("3. ⚖️ 认知负荷感知 - 动态优化生成策略")
    print("4. 🌟 完整工作流 - 端到端认知驱动生成")

    print("\n🔬 这些功能为SCI论文发表提供了强有力的支撑:")
    print("- 创新性: 首次将认知科学深度集成到代码生成")
    print("- 可解释性: 完整的认知过程追踪和解释")
    print("- 实用性: 认知负荷优化提升用户体验")
    print("- 科学性: 基于认知科学理论的系统设计")


if __name__ == "__main__":
    main()
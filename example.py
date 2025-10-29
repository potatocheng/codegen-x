"""
CodeGen-X 使用示例

展示如何使用标准模式和认知驱动模式进行代码生成。
"""

from llm.structured_llm import StructuredLLM
from agent.code_agent import CodeGenAgent
from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent


def example_standard_mode():
    """标准模式示例"""
    print("=" * 60)
    print("示例 1: 标准代码生成模式")
    print("=" * 60)

    llm = StructuredLLM(model="gpt-4o-2024-08-06")
    agent = CodeGenAgent(llm, max_refine_attempts=3)

    request = "写一个函数，从有序数组中删除重复元素，返回新数组的长度"
    print(f"\n需求: {request}\n")

    result = agent.generate(request)

    if result["success"]:
        print("✅ 生成成功！\n")
        print(f"函数名: {result['spec']['name']}")
        print(f"目的: {result['spec']['purpose']}")
        print(f"\n生成的代码:\n{result['code']}")
        validation = result['validation']
        print(f"\n测试结果: {validation['passed_count']}/{validation['total_tests']} 通过")
        print(f"优化次数: {result['refine_attempts']}")
    else:
        print(f"❌ 生成失败: {result.get('message', result.get('error'))}")


def example_cognitive_mode():
    """认知驱动模式示例"""
    print("\n" + "=" * 60)
    print("示例 2: 认知驱动代码生成模式")
    print("=" * 60)

    llm = StructuredLLM(model="gpt-4o-2024-08-06")
    agent = CognitiveDrivenCodeGenAgent(llm, max_refine_attempts=3, enable_cognitive_guidance=True)

    request = "实现二分查找算法"
    print(f"\n需求: {request}\n")

    result = agent.generate(request)

    if result["success"]:
        print("✅ 认知驱动生成成功！\n")
        print(f"函数名: {result['spec']['name']}")

        # 显示认知分析
        if "cognitive_analysis" in result:
            analysis = result["cognitive_analysis"]
            print(f"🧠 认知策略: {analysis.get('strategy_selection', 'N/A')}")
            print(f"🎯 置信度: {analysis.get('confidence_level', 0):.2f}")

        # 显示决策链
        if "cognitive_decisions" in result:
            decisions = result["cognitive_decisions"]
            print(f"\n📋 认知决策 ({len(decisions)} 个):")
            for i, decision in enumerate(decisions[:3], 1):
                print(f"  {i}. [{decision['stage']}] {decision['decision']}")

        print(f"\n生成的代码:\n{result['code']}")
        print(f"\n✅ 优化次数: {result['refine_attempts']}")
    else:
        print(f"❌ 生成失败: {result.get('message', result.get('error'))}")


def example_compare_modes():
    """对比两种模式"""
    print("\n" + "=" * 60)
    print("示例 3: 对比标准模式和认知模式")
    print("=" * 60)

    llm = StructuredLLM(model="gpt-4o-2024-08-06")
    request = "写一个计算阶乘的递归函数"

    print(f"\n需求: {request}\n")

    # 标准模式
    print("📌 标准模式:")
    standard_agent = CodeGenAgent(llm, max_refine_attempts=2)
    standard_result = standard_agent.generate(request)
    if standard_result["success"]:
        print("✅ 成功生成")
        print(f"   优化次数: {standard_result.get('refine_attempts', 0)}")
    else:
        print(f"❌ 失败")

    # 认知模式
    print("\n🧠 认知驱动模式:")
    cognitive_agent = CognitiveDrivenCodeGenAgent(llm, max_refine_attempts=2, enable_cognitive_guidance=True)
    cognitive_result = cognitive_agent.generate(request)
    if cognitive_result["success"]:
        print("✅ 成功生成")
        print(f"   优化次数: {cognitive_result.get('refine_attempts', 0)}")
        if "cognitive_summary" in cognitive_result:
            summary = cognitive_result["cognitive_summary"]
            print(f"   认知负荷: {summary.get('current_load', 0):.2f}")
    else:
        print(f"❌ 失败")


if __name__ == "__main__":
    try:
        # 运行示例
        example_standard_mode()
        # example_cognitive_mode()
        # example_compare_modes()

        print("\n" + "=" * 60)
        print("💡 提示:")
        print("  - 取消注释其他 example_* 调用来运行更多示例")
        print("  - 确保设置了 OPENAI_API_KEY 环境变量")
        print("  - 使用 main.py --cognitive 来启用命令行认知模式")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

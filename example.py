"""
简单示例：使用新的CodeGen-X架构生成代码

这个示例展示了如何使用Agent + Tools架构生成代码。
"""
from llm.structured_llm import StructuredLLM
from agent.code_agent import CodeGenAgent
from logger import logger
import logging

# 配置日志级别
logging.basicConfig(level=logging.INFO)


def example_basic_usage():
    """基础用法示例"""
    print("=" * 60)
    print("示例 1: 基础用法")
    print("=" * 60)

    # 初始化
    llm = StructuredLLM(model="gpt-4o-2024-08-06")
    agent = CodeGenAgent(llm, max_refine_attempts=3)

    # 生成代码
    request = "写一个函数，从有序数组中删除重复元素，返回新数组的长度"
    print(f"\n需求: {request}\n")

    result = agent.generate(request)

    # 检查结果
    if result["success"]:
        print("✓ 生成成功！\n")
        print(f"函数名: {result['spec']['name']}")
        print(f"目的: {result['spec']['purpose']}")
        print(f"\n生成的代码:\n")
        print(result["code"])
        print(f"\n测试结果: {result['validation']['passed_count']}/{result['validation']['total_tests']} 通过")
        print(f"优化次数: {result['refine_attempts']}")
    else:
        print(f"✗ 生成失败: {result.get('message', result.get('error'))}")


def example_inspect_workflow():
    """详细查看工作流程"""
    print("\n" + "=" * 60)
    print("示例 2: 查看详细工作流程")
    print("=" * 60)

    llm = StructuredLLM(model="gpt-4o-2024-08-06")
    agent = CodeGenAgent(llm, max_refine_attempts=2)

    request = "实现二分查找算法"
    print(f"\n需求: {request}\n")

    result = agent.generate(request)

    if result["success"]:
        # 查看规范
        print("1. 生成的规范:")
        spec = result["spec"]
        print(f"   函数名: {spec['name']}")
        print(f"   参数: {[p['name'] for p in spec['parameters']]}")
        print(f"   返回类型: {spec['return_type']}")
        print(f"   示例数量: {len(spec['examples'])}")
        print(f"   边界情况: {len(spec['edge_cases'])} 个")

        # 查看验证结果
        print("\n2. 验证结果:")
        validation = result["validation"]
        for test in validation["test_results"]:
            status = "✓" if test["passed"] else "✗"
            print(f"   {status} {test['test_name']}: 输入={test['input_values']}")

        print(f"\n3. 最终代码已生成，经过 {result['refine_attempts']} 次优化")


def example_custom_parameters():
    """自定义参数示例"""
    print("\n" + "=" * 60)
    print("示例 3: 自定义参数")
    print("=" * 60)

    # 使用DeepSeek API（兼容OpenAI）
    llm = StructuredLLM(
        model="deepseek-chat",
        # base_url 和 api_key 从环境变量读取
    )

    # 自定义最大优化次数
    agent = CodeGenAgent(
        llm,
        max_refine_attempts=5,  # 最多优化5次
        max_iterations=15       # 最大总迭代次数
    )

    request = "写一个函数计算斐波那契数列的第n项"
    result = agent.generate(request)

    if result["success"]:
        print(f"✓ 成功生成代码")
        print(f"优化次数: {result['refine_attempts']}")
    else:
        print(f"✗ 失败: {result.get('message')}")


def example_tool_inspection():
    """检查可用工具"""
    print("\n" + "=" * 60)
    print("示例 4: 检查可用工具")
    print("=" * 60)

    llm = StructuredLLM()
    agent = CodeGenAgent(llm)

    print(f"\n可用工具数量: {len(agent.tools)}")
    print("\n工具列表:")
    for name, tool in agent.tools.items():
        print(f"  - {name}: {tool.description}")


if __name__ == "__main__":
    try:
        # 运行示例
        example_basic_usage()
        # example_inspect_workflow()
        # example_custom_parameters()
        # example_tool_inspection()

    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

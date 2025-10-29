"""
CodeGen-X - 简化的主入口

使用Agent + Tools架构的AI代码生成系统。
"""
import argparse
import json
from pathlib import Path
from typing import Optional

from llm import StructuredLLM
from agent import CodeGenAgent
from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent
from utils import logger, set_log_level


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="CodeGen-X: AI驱动的代码生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "写一个二分查找函数"
  %(prog)s "实现快速排序" --model gpt-4o-2024-08-06
  %(prog)s --interactive  # 交互模式
        """
    )

    parser.add_argument(
        "request",
        nargs="?",
        type=str,
        help="代码生成需求描述"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-2024-08-06",
        help="使用的模型名称 (默认: gpt-4o-2024-08-06)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="输出目录 (默认: output)"
    )
    parser.add_argument(
        "--max-refine",
        type=int,
        default=3,
        help="最大代码优化次数 (默认: 3)"
    )
    parser.add_argument(
        "--cognitive",
        action="store_true",
        help="启用认知驱动代码生成模式"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="启动交互模式"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )

    args = parser.parse_args()

    # 设置日志级别
    set_log_level(args.log_level)

    # 如果没有请求参数且不是交互模式，显示帮助
    if not args.request and not args.interactive:
        parser.print_help()
        return

    try:
        # 初始化LLM和Agent
        llm = StructuredLLM(model=args.model)

        if args.cognitive:
            logger.info(f"初始化认知驱动 CodeGen-X (模型: {args.model})")
            agent = CognitiveDrivenCodeGenAgent(llm, max_refine_attempts=args.max_refine)
        else:
            logger.info(f"初始化标准 CodeGen-X (模型: {args.model})")
            agent = CodeGenAgent(llm, max_refine_attempts=args.max_refine)

        if args.interactive:
            interactive_mode(agent, args.output, args.cognitive)
        else:
            single_request_mode(agent, args.request, args.output, args.cognitive)

    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        print(f"\n❌ 错误: {str(e)}")
        print("\n请检查:")
        print("1. 是否设置了 OPENAI_API_KEY 环境变量")
        print("2. 网络连接是否正常")
        print("3. API key 是否有效")


def single_request_mode(agent, request: str, output_dir: str, is_cognitive: bool = False):
    """单次请求模式"""
    logger.info(f"需求: {request}")

    mode_name = "认知驱动" if is_cognitive else "标准"
    print(f"🚀 开始生成代码... (模式: {mode_name})")
    print(f"📝 需求: {request}\n")

    # 生成代码
    result = agent.generate(request)

    # 处理结果
    if result["success"]:
        save_results(result, output_dir, is_cognitive)
        print_success_summary(result, output_dir, is_cognitive)
    else:
        print_failure_summary(result)


def interactive_mode(agent, output_dir: str, is_cognitive: bool = False):
    """交互模式"""
    mode_name = "认知驱动" if is_cognitive else "标准"
    print(f"🎉 欢迎使用 CodeGen-X 交互式代码生成 (模式: {mode_name})")
    print("💡 输入需求描述，或输入 'quit'/'exit' 退出\n")

    session_count = 0

    while True:
        try:
            request = input("请输入需求 > ").strip()

            if request.lower() in ["exit", "quit", "q"]:
                print("\n👋 再见！")
                break

            if not request:
                continue

            session_count += 1
            print(f"\n🚀 [{session_count}] 开始生成代码... (模式: {mode_name})")

            result = agent.generate(request)

            if result["success"]:
                # 为交互模式创建带session编号的输出目录
                session_output = f"{output_dir}/session_{session_count}"
                save_results(result, session_output, is_cognitive)
                print_success_summary(result, session_output, is_cognitive)
            else:
                print_failure_summary(result)

            print("\n" + "="*60 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            logger.error(f"处理请求时出错: {str(e)}")
            print(f"\n❌ 发生错误: {str(e)}\n")


def save_results(result: dict, output_dir: str, is_cognitive: bool = False):
    """保存生成结果"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 保存规范
    spec_file = output_path / "spec.json"
    with open(spec_file, "w", encoding="utf-8") as f:
        json.dump(result["spec"], f, indent=2, ensure_ascii=False)

    # 保存代码
    code_file = output_path / "implementation.py"
    with open(code_file, "w", encoding="utf-8") as f:
        f.write(result["code"])

    # 保存验证结果
    if "validation" in result:
        validation_file = output_path / "validation.json"
        with open(validation_file, "w", encoding="utf-8") as f:
            json.dump(result["validation"], f, indent=2, ensure_ascii=False)

    # 如果是认知模式，保存额外的认知信息
    if is_cognitive and "cognitive_analysis" in result:
        cognitive_file = output_path / "cognitive_analysis.json"
        with open(cognitive_file, "w", encoding="utf-8") as f:
            json.dump(result["cognitive_analysis"], f, indent=2, ensure_ascii=False)

        if "cognitive_decisions" in result:
            decisions_file = output_path / "cognitive_decisions.json"
            with open(decisions_file, "w", encoding="utf-8") as f:
                json.dump(result["cognitive_decisions"], f, indent=2, ensure_ascii=False)

    logger.info(f"结果保存到: {output_path}")


def print_success_summary(result: dict, output_dir: Optional[str] = None, is_cognitive: bool = False):
    """打印成功摘要"""
    validation = result.get("validation", {})
    spec = result["spec"]

    print("✅ 代码生成成功！")
    print(f"📋 函数名: {spec['name']}")

    if validation:
        print(f"📊 测试通过: {validation['passed_count']}/{validation['total_tests']}")

    print(f"🔄 优化次数: {result.get('refine_attempts', 0)}")

    # 如果是认知模式，显示额外信息
    if is_cognitive:
        if "cognitive_analysis" in result:
            strategy = result["cognitive_analysis"].get("strategy_selection", "未知")
            confidence = result["cognitive_analysis"].get("confidence_level", 0)
            print(f"🧠 认知策略: {strategy}")
            print(f"🎯 置信度: {confidence:.2f}")

        if "cognitive_decisions" in result:
            print(f"🔍 认知决策: {len(result['cognitive_decisions'])} 个决策点")

    if output_dir:
        print(f"📁 保存位置: {output_dir}/")

    print(f"\n📄 生成的代码:\n")
    print("```python")
    # 只显示前20行，避免输出过长
    code_lines = result["code"].split('\n')
    for i, line in enumerate(code_lines[:20]):
        print(line)
    if len(code_lines) > 20:
        print(f"... (还有 {len(code_lines) - 20} 行)")
    print("```")

    # 如果是认知模式，显示认知洞察
    if is_cognitive and "cognitive_decisions" in result:
        print(f"\n🧠 认知决策过程:")
        for i, decision in enumerate(result["cognitive_decisions"][:3], 1):  # 只显示前3个
            print(f"   {i}. [{decision['stage']}] {decision['decision']}")
        if len(result["cognitive_decisions"]) > 3:
            print(f"   ... (还有 {len(result['cognitive_decisions']) - 3} 个决策)")


def print_failure_summary(result: dict):
    """打印失败摘要"""
    print("❌ 代码生成未完全成功")

    if "error" in result:
        print(f"🔥 错误: {result['error']}")
    elif "message" in result:
        print(f"⚠️  警告: {result['message']}")

        if result.get("validation"):
            validation = result["validation"]
            print(f"📊 测试状态: {validation['passed_count']}/{validation['total_tests']} 通过")

    print("\n💡 建议:")
    print("- 尝试使用更具体的需求描述")
    print("- 检查网络连接和API配额")
    print("- 使用 --log-level DEBUG 查看详细日志")


if __name__ == "__main__":
    main()
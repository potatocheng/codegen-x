"""
多模型协作代码生成演示

演示如何使用协作框架进行代码生成，包括:
1. 基本使用方法
2. 不同工作流的对比
3. 性能和质量分析
4. 实际使用场景
"""

import os
import json
import time
from typing import Dict, Any

# 确保正确导入
import sys
sys.path.append('.')

from llm.structured_llm import StructuredLLM
from tools.collaborative_generator import (
    create_collaborative_generator,
    create_default_team_config,
    create_multi_model_team_config,
    quick_generate,
    CollaborativeSession
)


def demo_quick_generation():
    """演示快速生成功能"""
    print("🚀 演示1: 快速代码生成")
    print("="*50)

    requirements = [
        "实现一个二分查找函数",
        "编写一个快速排序算法",
        "创建一个简单的栈数据结构"
    ]

    for req in requirements:
        print(f"\n📝 需求: {req}")
        start_time = time.time()

        result = quick_generate(
            requirement=req,
            workflow_type="simple"
        )

        execution_time = time.time() - start_time

        if result['success']:
            print(f"✅ 生成成功! (耗时: {execution_time:.2f}秒)")
            print(f"   质量得分: {result['final_quality_score']:.2f}")
            print(f"   置信度: {result['final_confidence']:.2f}")
            print(f"   阶段完成: {result['stages_completed']}/{result['total_stages']}")

            # 显示部分代码
            code = result['final_code']
            if len(code) > 200:
                print(f"   代码预览: {code[:200]}...")
            else:
                print(f"   生成代码: {code}")
        else:
            print(f"❌ 生成失败: {result.get('error', '未知错误')}")

        print("-" * 30)


def demo_mock_collaboration():
    """模拟协作演示（当没有API密钥时）"""
    print("\n🎭 模拟协作演示")
    print("="*30)

    print("📝 模拟需求: 实现快速排序算法")

    # 模拟各个阶段的输出
    mock_stages = [
        ("需求分析", "分析排序算法的要求：时间复杂度O(n log n)，原地排序"),
        ("算法选择", "选择快速排序：分治策略，平均O(n log n)复杂度"),
        ("接口设计", "def quicksort(arr, low=0, high=None): ..."),
        ("核心实现", "实现partition函数和递归排序逻辑"),
        ("测试策略", "设计边界测试：空数组、单元素、重复元素")
    ]

    for i, (stage, content) in enumerate(mock_stages, 1):
        print(f"\n🔄 阶段 {i}: {stage}")
        print(f"   多Worker生成中...")
        time.sleep(0.5)  # 模拟处理时间
        print(f"   Master融合完成: {content}")

    print(f"\n✅ 模拟协作完成!")
    print(f"   总阶段: {len(mock_stages)}")
    print(f"   模拟质量得分: 85.6")
    print(f"   模拟置信度: 0.89")

    mock_code = '''
def quicksort(arr, low=0, high=None):
    """快速排序算法实现"""
    if high is None:
        high = len(arr) - 1

    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

    return arr

def partition(arr, low, high):
    """分区函数"""
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
'''

    print(f"\n📄 模拟生成代码:")
    print("```python")
    print(mock_code.strip())
    print("```")


def main():
    """主演示函数"""
    print("🎯 多模型协作代码生成演示")
    print("="*60)

    # 检查环境
    print("🔍 环境检查:")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ 找到API密钥: {api_key[:10]}...")
    else:
        print("   ⚠️  未找到OPENAI_API_KEY，将使用模拟模式")

    base_url = os.getenv('OPENAI_BASE_URL')
    if base_url:
        print(f"   📡 自定义API端点: {base_url}")

    try:
        # 演示1: 快速生成
        demo_quick_generation()

        # 演示2: 模拟协作（如果没有API密钥）
        if not api_key:
            demo_mock_collaboration()

        print(f"\n🎉 演示完成!")
        print(f"💡 提示: 配置OPENAI_API_KEY环境变量以体验完整功能")

    except KeyboardInterrupt:
        print(f"\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n💥 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
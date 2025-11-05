"""
协作代码生成器 - 工厂函数和便捷接口

提供简化的API来使用多模型协作代码生成功能。
"""

import os
import json
from typing import Dict, List, Any, Optional
from llm.structured_llm import StructuredLLM
from .collaborative_framework import (
    CollaborativeCodeGenerator, DAGWorkflow, create_default_workflow,
    CognitiveStage, logger
)


def create_collaborative_generator(
    master_model_config: Dict[str, Any],
    worker_configs: List[Dict[str, Any]],
    workflow_type: str = "default",
    max_concurrent_workers: int = 3,
    fusion_threshold: float = 0.7
) -> CollaborativeCodeGenerator:
    """
    创建协作代码生成器

    Args:
        master_model_config: Master Agent的模型配置
        worker_configs: Worker Agent的配置列表
        workflow_type: 工作流类型 ("default", "simple", "custom")
        max_concurrent_workers: 最大并发Worker数
        fusion_threshold: 融合质量阈值

    Returns:
        协作代码生成器实例
    """
    # 创建Master LLM
    master_llm = StructuredLLM(
        model=master_model_config.get('model', 'gpt-4o'),
        api_key=master_model_config.get('api_key'),
        base_url=master_model_config.get('base_url')
    )

    # 选择工作流
    workflow = None
    if workflow_type == "default":
        workflow = create_default_workflow()
    elif workflow_type == "simple":
        workflow = create_simple_workflow()
    elif workflow_type == "research":
        workflow = create_research_workflow()

    # 创建协作生成器
    generator = CollaborativeCodeGenerator(
        master_llm=master_llm,
        worker_configs=worker_configs,
        workflow=workflow,
        max_concurrent_workers=max_concurrent_workers,
        fusion_threshold=fusion_threshold
    )

    return generator


def create_simple_workflow() -> DAGWorkflow:
    """创建简化的工作流（适合简单任务）"""
    workflow = DAGWorkflow()

    # 只包含核心阶段
    workflow.add_stage(CognitiveStage.REQUIREMENT_ANALYSIS, [])
    workflow.add_stage(CognitiveStage.ALGORITHM_SELECTION, [CognitiveStage.REQUIREMENT_ANALYSIS])
    workflow.add_stage(CognitiveStage.CORE_IMPLEMENTATION, [CognitiveStage.ALGORITHM_SELECTION])
    workflow.add_stage(CognitiveStage.TESTING_STRATEGY, [CognitiveStage.CORE_IMPLEMENTATION])

    return workflow


def create_research_workflow() -> DAGWorkflow:
    """创建研究导向的工作流（更注重分析和设计）"""
    workflow = DAGWorkflow()

    # 扩展的分析和设计阶段
    workflow.add_stage(CognitiveStage.REQUIREMENT_ANALYSIS, [])
    workflow.add_stage(CognitiveStage.ARCHITECTURE_DESIGN, [CognitiveStage.REQUIREMENT_ANALYSIS])
    workflow.add_stage(CognitiveStage.ALGORITHM_SELECTION, [CognitiveStage.REQUIREMENT_ANALYSIS])
    workflow.add_stage(CognitiveStage.INTERFACE_DESIGN, [CognitiveStage.ARCHITECTURE_DESIGN])
    workflow.add_stage(CognitiveStage.CORE_IMPLEMENTATION, [
        CognitiveStage.ARCHITECTURE_DESIGN,
        CognitiveStage.ALGORITHM_SELECTION,
        CognitiveStage.INTERFACE_DESIGN
    ])
    workflow.add_stage(CognitiveStage.PERFORMANCE_OPTIMIZATION, [CognitiveStage.CORE_IMPLEMENTATION])
    workflow.add_stage(CognitiveStage.TESTING_STRATEGY, [CognitiveStage.CORE_IMPLEMENTATION])

    return workflow


def create_default_team_config() -> List[Dict[str, Any]]:
    """创建默认的Worker团队配置"""
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')

    return [
        {
            'model': 'gpt-4o',
            'specialization': 'algorithm',
            'api_key': api_key,
            'base_url': base_url,
            'temperature': 0.2,
            'expertise_areas': ['algorithms', 'data_structures', 'complexity_analysis']
        },
        {
            'model': 'gpt-4o',
            'specialization': 'architecture',
            'api_key': api_key,
            'base_url': base_url,
            'temperature': 0.3,
            'expertise_areas': ['system_design', 'software_architecture', 'design_patterns']
        },
        {
            'model': 'gpt-4o',
            'specialization': 'performance',
            'api_key': api_key,
            'base_url': base_url,
            'temperature': 0.2,
            'expertise_areas': ['optimization', 'profiling', 'scalability']
        },
        {
            'model': 'gpt-4o',
            'specialization': 'testing',
            'api_key': api_key,
            'base_url': base_url,
            'temperature': 0.3,
            'expertise_areas': ['unit_testing', 'integration_testing', 'test_driven_development']
        }
    ]


def create_multi_model_team_config() -> List[Dict[str, Any]]:
    """创建多模型团队配置（如果有多个API密钥）"""
    openai_key = os.getenv('OPENAI_API_KEY')
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')

    configs = []

    # OpenAI模型
    if openai_key:
        configs.extend([
            {
                'model': 'gpt-4o',
                'specialization': 'algorithm',
                'api_key': openai_key,
                'temperature': 0.2
            },
            {
                'model': 'gpt-4o',
                'specialization': 'architecture',
                'api_key': openai_key,
                'temperature': 0.3
            }
        ])

    # DeepSeek模型
    if deepseek_key:
        configs.extend([
            {
                'model': 'deepseek-coder',
                'specialization': 'performance',
                'api_key': deepseek_key,
                'base_url': 'https://api.deepseek.com',
                'temperature': 0.2
            },
            {
                'model': 'deepseek-coder',
                'specialization': 'testing',
                'api_key': deepseek_key,
                'base_url': 'https://api.deepseek.com',
                'temperature': 0.3
            }
        ])

    # 如果没有配置多个模型，使用默认配置
    if not configs:
        configs = create_default_team_config()

    return configs


class CollaborativeSession:
    """协作会话管理器"""

    def __init__(self, generator: CollaborativeCodeGenerator):
        self.generator = generator
        self.session_history = []

    def generate(self, requirement: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成代码并记录会话历史"""
        result = self.generator.generate_code(requirement, context)

        # 记录会话
        session_record = {
            'requirement': requirement,
            'context': context,
            'result': result,
            'timestamp': result.get('timestamp', 0)
        }
        self.session_history.append(session_record)

        return result

    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度"""
        return self.generator.get_progress()

    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话总结"""
        if not self.session_history:
            return {'total_requests': 0}

        successful_requests = [r for r in self.session_history if r['result'].get('success', False)]

        return {
            'total_requests': len(self.session_history),
            'successful_requests': len(successful_requests),
            'success_rate': len(successful_requests) / len(self.session_history),
            'avg_execution_time': sum(r['result'].get('execution_time', 0) for r in self.session_history) / len(self.session_history),
            'worker_stats': self.generator.get_worker_stats()
        }

    def export_session(self, filepath: str):
        """导出会话历史"""
        session_data = {
            'session_summary': self.get_session_summary(),
            'history': self.session_history
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"会话历史已导出到: {filepath}")


def quick_generate(
    requirement: str,
    model_config: Dict[str, Any] = None,
    team_type: str = "default",
    workflow_type: str = "default"
) -> Dict[str, Any]:
    """
    快速生成代码（一次性使用）

    Args:
        requirement: 需求描述
        model_config: 模型配置（默认使用环境变量）
        team_type: 团队类型 ("default", "multi_model")
        workflow_type: 工作流类型 ("default", "simple", "research")

    Returns:
        生成结果
    """
    try:
        # 使用默认配置
        if not model_config:
            model_config = {
                'model': 'gpt-4o',
                'api_key': os.getenv('OPENAI_API_KEY'),
                'base_url': os.getenv('OPENAI_BASE_URL')
            }

        # 选择团队配置
        if team_type == "multi_model":
            worker_configs = create_multi_model_team_config()
        else:
            worker_configs = create_default_team_config()

        # 创建生成器
        generator = create_collaborative_generator(
            master_model_config=model_config,
            worker_configs=worker_configs,
            workflow_type=workflow_type
        )

        # 生成代码
        result = generator.generate_code(requirement)
        return result

    except Exception as e:
        logger.error(f"快速生成失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'requirement': requirement
        }


# 使用示例
if __name__ == "__main__":
    # 示例1: 快速生成
    print("=== 快速生成示例 ===")
    result = quick_generate(
        requirement="实现一个二分查找算法",
        workflow_type="simple"
    )

    if result['success']:
        print(f"生成成功! 质量得分: {result['final_quality_score']:.2f}")
        print(f"最终代码:\n{result['final_code']}")
    else:
        print(f"生成失败: {result.get('error', '未知错误')}")

    # 示例2: 完整会话
    print("\n=== 完整会话示例 ===")
    try:
        # 创建生成器
        master_config = {
            'model': 'gpt-4o',
            'api_key': os.getenv('OPENAI_API_KEY')
        }

        worker_configs = create_default_team_config()

        generator = create_collaborative_generator(
            master_model_config=master_config,
            worker_configs=worker_configs,
            workflow_type="default"
        )

        # 创建会话
        session = CollaborativeSession(generator)

        # 生成代码
        result = session.generate(
            requirement="实现一个高效的排序算法，支持自定义比较函数",
            context={'performance_priority': True}
        )

        # 显示结果
        if result['success']:
            print(f"生成成功! 执行时间: {result['execution_time']:.2f}秒")
            print(f"阶段完成: {result['stages_completed']}/{result['total_stages']}")

            # 获取会话总结
            summary = session.get_session_summary()
            print(f"会话总结: {summary}")

        # 导出会话（可选）
        # session.export_session("collaborative_session.json")

    except Exception as e:
        print(f"会话示例失败: {e}")
"""认知驱动代码生成模块

本模块实现了模拟人类程序员认知过程的代码生成系统。
主要组件：
1. CognitiveModel - 认知编程模型
2. ThinkingProcess - 思维过程建模
3. CognitiveLoad - 认知负荷评估
4. ProgrammingStrategy - 编程策略选择
"""

from .cognitive_model import CognitiveModel, ThinkingStage, CognitiveState
from .thinking_process import ThinkingProcess, ThoughtStep
from .cognitive_load import CognitiveLoadEvaluator, CognitiveComplexity
from .programming_strategy import ProgrammingStrategy, StrategyType

__all__ = [
    'CognitiveModel',
    'ThinkingStage',
    'CognitiveState',
    'ThinkingProcess',
    'ThoughtStep',
    'CognitiveLoadEvaluator',
    'CognitiveComplexity',
    'ProgrammingStrategy',
    'StrategyType'
]
from typing import Optional, Dict, Any, TypedDict, Literal, Union, cast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from llm.llm_interface import LLMInterface
from llm.deepseek import DeepSeekLLM


def create_llm(provider: str, model_name: str, config: Optional[Dict[str, Any]] = None) -> LLMInterface:
    """
    工厂函数创建LLM实例

    Args:
        provider: LLM提供商 ('deepseek', 'openao', etc.)
        model_name: 模型名称
        config: 配置参数

    Returns:
        LLM 实例
    """
    providers = {
        'deepseek': DeepSeekLLM,
    }

    provider = provider.lower()
    if provider not in providers:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    return providers[provider](model_name=model_name, config=config)

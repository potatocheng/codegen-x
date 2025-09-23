from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypedDict, List, Iterator, AsyncGenerator, Literal, Union, cast
from dataclasses import dataclass
from openai import OpenAI
from .message import Message

@dataclass
class LLMResponse:
    """
    LLM响应结果封装
    """
    content: str
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None
    response_time: Optional[float] = None

class LLMInterface(ABC):
    """
    抽象基类，定义了与LLM交互的接口。
    
    这个接口提供了基本的LLM调用方法，允许子类实现具体的LLM交互逻辑。
    """
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.model_name = model_name
        self.config = config
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = self._create_client()

        return self._client

    @abstractmethod
    def _create_client(self) -> Any:
        """
        Initialize the API client for the specific LLM provider.
        This is an abstract method that should be implemented by subclassee.
        """
        pass

    @abstractmethod
    def call(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """
        调用LLM生成回复。
        """
        pass

    @abstractmethod
    async def acall(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """
        异步调用LLM生成回复。
        """
        pass

    def stream(self, messages: List[Message], **kwargs: Any) -> Iterator[str]:
        """"流式响应生成器"""
        response = self.call(messages, **kwargs)
        yield response.content
    
    async def astream(self, messages: List[Message], **kwargs: Any) -> AsyncGenerator[str, Any]:
        """异步流式响应生成器"""
        # 默认实现，子类可以重写
        response = await self.acall(messages, **kwargs)
        yield response.content

    def validate_messages(self, messages: List[Message]):
        if not messages:
            raise ValueError("Messages list cannot be empty.")
        
        valid_roles = {"system", "user", "assistant"}
        for msg in messages:
            if msg.role not in valid_roles:
                raise ValueError(f"Invalid role '{msg.role}' in message. Valid roles are: {valid_roles}")
            if not isinstance(msg, Message):
                raise TypeError("Each message must be an instance of Message class.")
            if not msg.content.strip():
                raise ValueError("Message content cannot be empty or whitespace.")
            
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        if self._client is not None and hasattr(self._client, 'close'):
            self._client.close()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.model_name}')"
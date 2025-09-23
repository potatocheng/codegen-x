from .llm_interface import LLMInterface, LLMResponse
from .message import Message
from openai import OpenAI
from typing import List, Any, Dict, cast, Iterator, Optional
from logger import logger
import time
import os
import asyncio

class DeepSeekLLM(LLMInterface):
    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = self._create_client()

        return self._client

    def _create_client(self) -> OpenAI:
        """
        Initialize the API client for the specific LLM provider.
        This is an abstract method that should be implemented by subclasses.
        """
        api_key = (self.config or {}).get("api_key", os.getenv("DEEPSEEK_API_KEY"))
        base_url = self.config.get("base_url", "https://api.deepseek.com/v1/") if self.config else "https://api.deepseek.com/v1/"
        if not api_key:
            raise ValueError("API key is required for DeepSeek LLM.")
        
        return OpenAI(api_key=api_key,
                      base_url=base_url,
                      timeout=self.config.get("timeout", 60) if self.config else 60)
    
    def call(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """ 调用LLM生成回复。 """
        self.validate_messages(messages)
        start_time = time.time()

        try:
            # 正确的消息格式转换，使用类型转换解决兼容性问题
            msgs = [cast(Dict[str, Any], {"role": msg.role, "content": msg.content}) for msg in messages]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=msgs,  # type: ignore
                **kwargs
            )
           
            response_time = time.time() - start_time
            return LLMResponse(
                content=response.choices[0].message.content or "",
                usage=response.usage.model_dump() if response.usage else None,
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time
            )
           
        except Exception as e:
            logger.error(f"Error occurred while calling DeepSeek API: {e}")
            raise

    async def acall(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """ 异步调用LLM生成回复。"""
        # 使用线程池执行同步调用，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.call, messages, **kwargs)
    
    def stream(self, messages: List[Message], **kwargs: Any) -> Iterator[str]:
        """ 流式响应 """
        self.validate_messages(messages)
        msgs = [cast(Dict[str, Any], {"role": msg.role, "content": msg.content}) for msg in messages]

        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=msgs,  # type: ignore
                **kwargs
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"DeepSeek streaming failed: {e}")


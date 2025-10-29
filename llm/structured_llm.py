"""
结构化LLM接口

使用OpenAI的结构化输出API，支持任何兼容的API端点。
"""
from pydantic import BaseModel
from typing import Type, TypeVar, List, Dict, Any, Optional
import os
import logging

# 设置日志
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class StructuredLLM:
    """结构化LLM包装器

    支持OpenAI和兼容API（如DeepSeek）的结构化输出功能。
    """

    def __init__(
        self,
        model: str = "gpt-4o-2024-08-06",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0
    ):
        """初始化LLM

        Args:
            model: 模型名称
            api_key: API密钥，如果不提供则从环境变量读取
            base_url: API基础URL，用于支持兼容OpenAI的服务
            timeout: 请求超时时间
        """
        self.model = model
        self.timeout = timeout

        # 从环境变量读取配置
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        if not self.api_key:
            raise ValueError(
                "API key 未设置。请设置 OPENAI_API_KEY 环境变量或传入 api_key 参数。"
            )

        # 延迟导入，避免启动时的依赖检查
        self._client = None
        self._call_count = 0
        self._total_tokens = 0

    @property
    def client(self):
        """懒加载OpenAI客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=self.timeout
                )
            except ImportError:
                raise ImportError(
                    "需要安装 openai 库: pip install openai>=1.50.0"
                )
        return self._client

    def generate_structured(
        self,
        prompt: str,
        output_schema: Type[T],
        system: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> T:
        """生成结构化输出

        Args:
            prompt: 用户提示
            output_schema: 输出的Pydantic模型类
            system: 系统提示
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            符合schema的Pydantic对象

        Raises:
            ValueError: 当输出不符合schema时
            Exception: 当API调用失败时
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "response_format": output_schema,
                "temperature": temperature
            }

            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = self.client.beta.chat.completions.parse(**kwargs)

            # 更新统计信息
            self._call_count += 1
            if hasattr(response, 'usage') and response.usage:
                self._total_tokens += response.usage.total_tokens

            parsed_result = response.choices[0].message.parsed

            if parsed_result is None:
                raise ValueError("LLM返回的结果无法解析为指定的schema")

            logger.debug(f"结构化输出成功: {output_schema.__name__}")
            return parsed_result

        except Exception as e:
            logger.error(f"结构化输出失败: {str(e)}")
            raise

    def simple_call(
        self,
        prompt: str,
        system: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """简单的文本生成调用

        Args:
            prompt: 用户提示
            system: 系统提示
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            生成的文本
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature
            }

            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**kwargs)

            # 更新统计信息
            self._call_count += 1
            if hasattr(response, 'usage') and response.usage:
                self._total_tokens += response.usage.total_tokens

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"简单调用失败: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """获取调用统计信息"""
        return {
            "model": self.model,
            "call_count": self._call_count,
            "total_tokens": self._total_tokens,
            "average_tokens": self._total_tokens / max(1, self._call_count)
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return f"StructuredLLM(model='{self.model}', calls={self._call_count})"

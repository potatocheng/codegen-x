from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
import time
from enum import Enum


class ToolStatus(Enum):
    """工具执行状态"""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"


class ToolInput(BaseModel):
    """工具输入基类"""

    class Config:
        """Pydantic配置"""
        extra = "forbid"  # 禁止额外字段


class ToolOutput(BaseModel):
    """工具输出基类"""
    success: bool = Field(description="是否执行成功")
    status: ToolStatus = Field(description="执行状态")
    data: Optional[Any] = Field(default=None, description="返回数据")
    message: str = Field(default="", description="状态消息")
    execution_time: Optional[float] = Field(default=None, description="执行时间（秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")

    @classmethod
    def success_result(cls, data: Any, message: str = "", **metadata) -> "ToolOutput":
        """快速创建成功结果"""
        return cls(
            success=True,
            status=ToolStatus.SUCCESS,
            data=data,
            message=message,
            metadata=metadata
        )

    @classmethod
    def error_result(cls, message: str, **metadata) -> "ToolOutput":
        """快速创建错误结果"""
        return cls(
            success=False,
            status=ToolStatus.FAILURE,
            data=None,
            message=message,
            metadata=metadata
        )

    @classmethod
    def warning_result(cls, data: Any, message: str, **metadata) -> "ToolOutput":
        """快速创建警告结果"""
        return cls(
            success=True,
            status=ToolStatus.WARNING,
            data=data,
            message=message,
            metadata=metadata
        )


class Tool(ABC):
    """工具基类

    所有工具都应继承此类并实现execute方法。
    提供统一的工具接口和性能监控。
    """

    name: str
    description: str
    input_schema: type[ToolInput]

    def __init__(self):
        """初始化工具"""
        self._execution_count = 0
        self._total_time = 0.0

    @abstractmethod
    def _execute_impl(self, input_data: ToolInput) -> ToolOutput:
        """具体的工具执行逻辑，由子类实现"""
        pass

    def execute(self, input_data: ToolInput) -> ToolOutput:
        """执行工具，包含性能监控和错误处理"""
        start_time = time.time()

        try:
            # 验证输入类型
            if not isinstance(input_data, self.input_schema):
                return ToolOutput.error_result(
                    f"输入类型错误，期望 {self.input_schema.__name__}，实际 {type(input_data).__name__}"
                )

            # 执行具体逻辑
            result = self._execute_impl(input_data)

            # 更新统计信息
            execution_time = time.time() - start_time
            self._execution_count += 1
            self._total_time += execution_time

            # 设置执行时间
            result.execution_time = execution_time

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            return ToolOutput.error_result(
                f"工具 {self.name} 执行异常: {str(e)}",
                exception_type=type(e).__name__,
                execution_time=execution_time
            )

    def get_stats(self) -> Dict[str, Any]:
        """获取工具执行统计信息"""
        return {
            "name": self.name,
            "execution_count": self._execution_count,
            "total_time": self._total_time,
            "average_time": self._total_time / max(1, self._execution_count)
        }

    def to_openai_tool_schema(self) -> Dict[str, Any]:
        """转换为OpenAI工具schema格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema.model_json_schema()
            }
        }

    def __repr__(self) -> str:
        """工具的字符串表示"""
        return f"{self.__class__.__name__}(name='{self.name}', executions={self._execution_count})"

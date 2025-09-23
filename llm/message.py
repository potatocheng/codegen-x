from typing import TypedDict, Literal, cast, Union
from dataclasses import dataclass

class ChatMessage(TypedDict):
    role: str
    content: str

class UserMessage(TypedDict):
    role: Literal["user"]
    content: str

class SystemMessage(TypedDict):
    role: Literal["system"]
    content: str

class AssistantMessage(TypedDict):
    role: Literal["assistant"]
    content: str

MessageDict = Union[UserMessage, SystemMessage, AssistantMessage]

@dataclass
class Message:
    """
    消息类型定义，包含角色和内容。
    
    这个类用于定义与LLM交互时的消息格式。
    """
    role: str
    content: str

    def to_dict(self) -> MessageDict:
        if self.role not in {"system", "user", "assistant"}:
            raise ValueError(f"Invalid role '{self.role}'. Valid roles are: 'system', 'user', 'assistant'.")
        
        return cast(MessageDict, {
            "role": self.role,
            "content": self.content
        })
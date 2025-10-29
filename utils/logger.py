"""
简化的日志工具
"""
import logging
import sys
from typing import Any

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 创建全局logger实例
logger = logging.getLogger('codegen-x')

def set_log_level(level: str):
    """设置日志级别"""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    logger.setLevel(numeric_level)

def log_operation(operation: str, **kwargs: Any):
    """记录操作日志"""
    details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"[{operation}] {details}")

__all__ = ["logger", "set_log_level", "log_operation"]
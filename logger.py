import logging
import sys
from typing import Optional
from datetime import datetime

class ProjectLogger:
    """
    项目统一日志组件
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger('DAG_Coder')
            self._setup_logger()
            ProjectLogger._initialized = True
    
    def _setup_logger(self):
        """设置日志配置"""
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = logging.FileHandler('dag_coder.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """调试级别日志"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息级别日志"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告级别日志"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误级别日志"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误级别日志"""
        self.logger.critical(message, **kwargs)
    
    def log_graph_operation(self, operation: str, node_component: Optional[str] =  None, node_id: Optional[str] = None):
        """专门记录图操作的日志"""
        if node_component and node_id:
            self.info(f"Graph Operation: {operation} - Component: {node_component}, ID: {node_id}")
        else:
            self.info(f"Graph Operation: {operation}")

# 创建全局日志实例
logger = ProjectLogger()
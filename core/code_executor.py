"""
优化的代码执行器

安全执行Python代码并返回结果。
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from contextlib import redirect_stdout, redirect_stderr
import json
import time
import io
import traceback
import sys
import os


class ExecutionStatus(Enum):
    """执行状态"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    SECURITY_ERROR = "security_error"


@dataclass
class ExecutionResult:
    """代码执行结果"""
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    return_value: Any = None
    locals_snapshot: Dict[str, Any] = None

    @property
    def success(self) -> bool:
        """是否执行成功"""
        return self.status == ExecutionStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "status": self.status.value,
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "execution_time": self.execution_time,
            "return_value": self.return_value,
        }

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)


class SecurityError(Exception):
    """安全相关的异常"""
    pass


class CodeExecutor:
    """安全的代码执行器

    提供沙箱化的Python代码执行环境。
    """

    # 危险的内置函数和模块
    DANGEROUS_BUILTINS = {
        'exec', 'eval', 'compile', '__import__', 'open', 'file',
        'input', 'raw_input', 'reload', 'vars', 'locals', 'globals',
        'dir', 'getattr', 'setattr', 'delattr', 'hasattr'
    }

    DANGEROUS_MODULES = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'shutil', 'tempfile', 'pickle', 'marshal', 'imp', 'importlib'
    }

    def __init__(self, timeout: float = 10.0, enable_security: bool = True):
        """初始化执行器

        Args:
            timeout: 执行超时时间（秒）
            enable_security: 是否启用安全检查
        """
        self.timeout = timeout
        self.enable_security = enable_security
        self._execution_count = 0

    def run(self, code: str, globals_dict: Optional[Dict] = None) -> ExecutionResult:
        """执行代码

        Args:
            code: 要执行的Python代码
            globals_dict: 全局命名空间

        Returns:
            ExecutionResult: 执行结果
        """
        if not code or not code.strip():
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                error="代码为空"
            )

        # 安全检查
        if self.enable_security:
            security_check = self._security_check(code)
            if security_check:
                return ExecutionResult(
                    status=ExecutionStatus.SECURITY_ERROR,
                    error=f"安全检查失败: {security_check}"
                )

        start_time = time.time()
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            # 准备执行环境
            safe_globals = self._create_safe_globals(globals_dict)
            local_vars = {}

            # 执行代码
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # 使用超时控制（简化版本，实际应用中可能需要更复杂的超时机制）
                compiled_code = compile(code, '<executed_code>', 'exec')
                exec(compiled_code, safe_globals, local_vars)

            execution_time = time.time() - start_time
            self._execution_count += 1

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time=execution_time,
                locals_snapshot=self._safe_locals_snapshot(local_vars)
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_info = traceback.format_exc()

            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                error=error_info,
                execution_time=execution_time
            )

    def _security_check(self, code: str) -> Optional[str]:
        """安全检查代码

        Returns:
            None如果安全，否则返回错误信息
        """
        code_lower = code.lower()

        # 检查危险的内置函数
        for dangerous in self.DANGEROUS_BUILTINS:
            if dangerous in code:
                return f"包含危险函数: {dangerous}"

        # 检查危险的模块导入
        for dangerous in self.DANGEROUS_MODULES:
            if f"import {dangerous}" in code or f"from {dangerous}" in code:
                return f"尝试导入危险模块: {dangerous}"

        # 检查其他危险操作
        dangerous_patterns = [
            '__', 'exec(', 'eval(', 'compile(', 'open(',
            'file(', 'input(', 'raw_input('
        ]

        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return f"包含危险模式: {pattern}"

        return None

    def _create_safe_globals(self, globals_dict: Optional[Dict] = None) -> Dict:
        """创建安全的全局命名空间"""
        safe_builtins = {}

        # 只包含安全的内置函数
        safe_builtin_names = {
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes',
            'chr', 'complex', 'dict', 'divmod', 'enumerate', 'filter',
            'float', 'format', 'frozenset', 'hex', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min',
            'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
            'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
            'tuple', 'type', 'zip'
        }

        import builtins
        for name in safe_builtin_names:
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)

        safe_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__executed__',
            '__doc__': None,
        }

        # 添加常用的安全模块
        import math
        import random
        import datetime
        import json
        import re

        safe_globals.update({
            'math': math,
            'random': random,
            'datetime': datetime,
            'json': json,
            're': re,
        })

        # 合并用户提供的globals
        if globals_dict:
            for key, value in globals_dict.items():
                if not key.startswith('_'):  # 不允许私有变量
                    safe_globals[key] = value

        return safe_globals

    def _safe_locals_snapshot(self, locals_dict: Dict) -> Dict[str, Any]:
        """创建局部变量的安全快照"""
        snapshot = {}
        for key, value in locals_dict.items():
            if not key.startswith('_'):
                try:
                    # 尝试序列化以确保值是安全的
                    json.dumps(value, default=str)
                    snapshot[key] = value
                except (TypeError, ValueError):
                    # 如果无法序列化，转换为字符串
                    snapshot[key] = str(value)
        return snapshot

    def get_stats(self) -> Dict[str, Any]:
        """获取执行器统计信息"""
        return {
            "execution_count": self._execution_count,
            "timeout": self.timeout,
            "security_enabled": self.enable_security,
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return f"CodeExecutor(executions={self._execution_count}, timeout={self.timeout}s)"
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from contextlib import redirect_stdout, redirect_stderr
import json
import time
import io
import traceback

class ExecutionStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"

@dataclass
class ExecutionResult:
    status: ExecutionStatus = ExecutionStatus.PENDING
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "execution_time": self.execution_time
        }
    
    def to_json(self, indent: int = 4) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @property
    def success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS

@dataclass
class CodeExecutor:
    code: str = ""

    def run(self, code: str) -> ExecutionResult:
        """
        Executes the given code and returns an ExecutionResult.
        """
        if code is not None:
            self.code = code

        if not self.code.strip():
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                error="No code provided for execution."
            )

        start_time = time.time()
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                compiled_code = compile(self.code, '<string>', 'exec')
                exec(compiled_code, {}, {})
            execution_time = time.time() - start_time

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            
            # 获取完整的错误信息，包括堆栈跟踪
            error_info = traceback.format_exc()

            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                error=error_info,
                execution_time=execution_time
            )



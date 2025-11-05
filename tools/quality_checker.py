"""代码质量检查器

提供全面的代码质量评估，包括：
- 静态分析（pylint, mypy等）
- 性能基准测试
- 安全漏洞检查
- 代码复杂度分析
- 最佳实践检查
"""

import ast
import time
import timeit
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sys

@dataclass
class QualityMetrics:
    """代码质量指标"""

    # 静态分析
    pylint_score: Optional[float] = None
    pylint_issues: List[str] = field(default_factory=list)

    # 类型检查
    mypy_errors: List[str] = field(default_factory=list)

    # 复杂度分析
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0

    # 性能指标
    execution_time_avg: Optional[float] = None  # 平均执行时间（秒）
    execution_time_std: Optional[float] = None  # 执行时间标准差
    memory_usage: Optional[float] = None        # 内存使用量（MB）

    # 安全检查
    security_issues: List[str] = field(default_factory=list)

    # 代码风格
    pep8_violations: List[str] = field(default_factory=list)

    # 可维护性
    lines_of_code: int = 0
    comment_ratio: float = 0.0
    function_length: int = 0

    # 综合评分
    overall_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'static_analysis': {
                'pylint_score': self.pylint_score,
                'pylint_issues': self.pylint_issues,
                'mypy_errors': self.mypy_errors,
            },
            'complexity': {
                'cyclomatic': self.cyclomatic_complexity,
                'cognitive': self.cognitive_complexity,
            },
            'performance': {
                'execution_time_avg': self.execution_time_avg,
                'execution_time_std': self.execution_time_std,
                'memory_usage': self.memory_usage,
            },
            'security': {
                'issues': self.security_issues,
            },
            'style': {
                'pep8_violations': self.pep8_violations,
                'comment_ratio': self.comment_ratio,
            },
            'maintainability': {
                'lines_of_code': self.lines_of_code,
                'function_length': self.function_length,
            },
            'overall_score': self.overall_score,
        }


class CodeQualityChecker:
    """代码质量检查器"""

    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def analyze_code(self, code: str, function_name: str) -> QualityMetrics:
        """全面分析代码质量

        Args:
            code: 要分析的代码
            function_name: 主函数名称

        Returns:
            质量指标对象
        """
        metrics = QualityMetrics()

        # 创建临时文件
        temp_file = self.temp_dir / f"{function_name}.py"
        temp_file.write_text(code, encoding='utf-8')

        try:
            # 1. 静态分析
            self._run_static_analysis(str(temp_file), metrics)

            # 2. 复杂度分析
            self._analyze_complexity(code, metrics)

            # 3. 安全检查
            self._check_security(code, metrics)

            # 4. 代码风格检查
            self._check_style(str(temp_file), metrics)

            # 5. 可维护性分析
            self._analyze_maintainability(code, metrics)

            # 6. 性能基准测试（如果代码可以安全执行）
            if self._is_safe_to_execute(code):
                self._benchmark_performance(code, function_name, metrics)

            # 7. 计算综合评分
            self._calculate_overall_score(metrics)

        except Exception as e:
            print(f"质量检查出错: {e}")
        finally:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()

        return metrics

    def _run_static_analysis(self, file_path: str, metrics: QualityMetrics):
        """运行静态分析（pylint）"""
        try:
            # 运行pylint
            result = subprocess.run(
                [sys.executable, '-m', 'pylint', '--score=y', '--reports=no', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr

            # 解析pylint分数
            for line in output.split('\n'):
                if 'Your code has been rated at' in line:
                    try:
                        score_str = line.split('at ')[1].split('/')[0]
                        metrics.pylint_score = float(score_str)
                    except:
                        pass
                elif line.strip() and not line.startswith('*'):
                    # 收集错误和警告
                    if any(marker in line for marker in ['E:', 'W:', 'R:', 'C:']):
                        metrics.pylint_issues.append(line.strip())

        except (subprocess.TimeoutExpired, FileNotFoundError):
            metrics.pylint_issues.append("无法运行pylint检查")

    def _analyze_complexity(self, code: str, metrics: QualityMetrics):
        """分析代码复杂度"""
        try:
            tree = ast.parse(code)

            # 简单的圈复杂度计算
            complexity = 1  # 基础复杂度

            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1

            metrics.cyclomatic_complexity = complexity

            # 认知复杂度（简化版）
            metrics.cognitive_complexity = min(complexity + 2, 10)  # 简化计算

        except SyntaxError:
            metrics.cyclomatic_complexity = 999  # 语法错误

    def _check_security(self, code: str, metrics: QualityMetrics):
        """安全检查"""
        security_patterns = [
            ('eval(', '使用eval()可能存在代码注入风险'),
            ('exec(', '使用exec()可能存在代码执行风险'),
            ('subprocess.', '使用subprocess时需注意命令注入'),
            ('__import__', '动态导入可能存在安全风险'),
            ('pickle.load', 'pickle反序列化可能存在安全风险'),
            ('input(', '直接使用input()需要验证输入'),
        ]

        for pattern, message in security_patterns:
            if pattern in code:
                metrics.security_issues.append(message)

    def _check_style(self, file_path: str, metrics: QualityMetrics):
        """代码风格检查"""
        try:
            # 运行flake8进行PEP8检查
            result = subprocess.run(
                [sys.executable, '-m', 'flake8', '--max-line-length=88', file_path],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        metrics.pep8_violations.append(line.split(':', 3)[-1].strip())

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # flake8未安装或超时，跳过检查
            pass

    def _analyze_maintainability(self, code: str, metrics: QualityMetrics):
        """可维护性分析"""
        lines = code.split('\n')
        metrics.lines_of_code = len([line for line in lines if line.strip()])

        # 计算注释比例
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        metrics.comment_ratio = comment_lines / max(metrics.lines_of_code, 1)

        # 函数长度（主函数的行数）
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_end = getattr(node, 'end_lineno', node.lineno)
                    metrics.function_length = max(metrics.function_length,
                                                func_end - node.lineno + 1)
        except:
            metrics.function_length = metrics.lines_of_code

    def _is_safe_to_execute(self, code: str) -> bool:
        """检查代码是否可以安全执行"""
        unsafe_patterns = [
            'import os', 'import sys', 'import subprocess',
            'open(', 'file(', '__import__', 'eval(', 'exec(',
            'input(', 'raw_input('
        ]

        for pattern in unsafe_patterns:
            if pattern in code:
                return False

        return True

    def _benchmark_performance(self, code: str, function_name: str, metrics: QualityMetrics):
        """性能基准测试"""
        try:
            # 创建测试代码
            test_code = f"""
{code}

# 性能测试
import time
import random

# 生成测试数据
test_data = []
for _ in range(10):
    # 生成简单的测试参数
    args = [random.randint(1, 100) for _ in range(3)]
    test_data.append(args)

times = []
for args in test_data:
    start = time.perf_counter()
    try:
        # 尝试调用函数（假设最多3个参数）
        if len(args) == 1:
            result = {function_name}(args[0])
        elif len(args) == 2:
            result = {function_name}(args[0], args[1])
        else:
            result = {function_name}(args[0], args[1], args[2])
    except:
        # 如果参数不匹配，使用第一个参数
        result = {function_name}(args[0])
    end = time.perf_counter()
    times.append(end - start)

if times:
    avg_time = sum(times) / len(times)
    std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
    print(f"PERF_AVG: {{avg_time}}")
    print(f"PERF_STD: {{std_time}}")
"""

            # 在安全环境中执行
            result = subprocess.run(
                [sys.executable, '-c', test_code],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout
            for line in output.split('\n'):
                if line.startswith('PERF_AVG:'):
                    metrics.execution_time_avg = float(line.split(':')[1].strip())
                elif line.startswith('PERF_STD:'):
                    metrics.execution_time_std = float(line.split(':')[1].strip())

        except Exception:
            # 性能测试失败，跳过
            pass

    def _calculate_overall_score(self, metrics: QualityMetrics):
        """计算综合评分（0-100）"""
        score = 100.0

        # pylint分数权重 30%
        if metrics.pylint_score is not None:
            score = score * 0.7 + (metrics.pylint_score / 10) * 30

        # 复杂度扣分
        if metrics.cyclomatic_complexity > 10:
            score -= (metrics.cyclomatic_complexity - 10) * 2

        # 安全问题扣分
        score -= len(metrics.security_issues) * 10

        # PEP8违规扣分
        score -= len(metrics.pep8_violations) * 2

        # 注释比例加分
        if metrics.comment_ratio > 0.1:  # 超过10%注释率
            score += 5

        # 性能加分
        if metrics.execution_time_avg and metrics.execution_time_avg < 0.001:  # 小于1ms
            score += 5

        metrics.overall_score = max(0, min(100, score))


# 使用示例
if __name__ == "__main__":
    checker = CodeQualityChecker()

    sample_code = '''
def fibonacci(n):
    """计算斐波那契数列的第n项"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

    metrics = checker.analyze_code(sample_code, "fibonacci")
    print("质量分析结果:", metrics.to_dict())
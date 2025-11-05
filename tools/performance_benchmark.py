"""性能基准测试工具

提供代码性能测试和分析功能：
- 执行时间测试
- 内存使用监控
- 算法复杂度分析
- 性能对比测试
"""

import time
import tracemalloc
import gc
import statistics
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
import os

# 可选依赖
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class PerformanceResult:
    """性能测试结果"""
    function_name: str

    # 时间指标
    avg_time: float  # 平均执行时间（秒）
    min_time: float  # 最小执行时间
    max_time: float  # 最大执行时间
    std_time: float  # 时间标准差

    # 内存指标
    peak_memory: float  # 峰值内存使用（MB）
    memory_growth: float  # 内存增长（MB）

    # 效率指标
    operations_per_second: float  # 每秒操作数
    time_complexity_estimate: str  # 时间复杂度估计

    # 测试配置
    test_runs: int  # 测试运行次数
    input_size: int  # 输入数据大小

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'function_name': self.function_name,
            'timing': {
                'avg_time': self.avg_time,
                'min_time': self.min_time,
                'max_time': self.max_time,
                'std_time': self.std_time,
                'operations_per_second': self.operations_per_second,
            },
            'memory': {
                'peak_memory_mb': self.peak_memory,
                'memory_growth_mb': self.memory_growth,
            },
            'complexity': {
                'time_complexity_estimate': self.time_complexity_estimate,
            },
            'test_config': {
                'test_runs': self.test_runs,
                'input_size': self.input_size,
            }
        }


class PerformanceBenchmark:
    """性能基准测试器"""

    def __init__(self):
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process(os.getpid())
        else:
            self.process = None

    def benchmark_function(
        self,
        func: Callable,
        test_inputs: List[Any],
        runs: int = 10,
        warmup: int = 2
    ) -> PerformanceResult:
        """对函数进行性能基准测试

        Args:
            func: 要测试的函数
            test_inputs: 测试输入列表
            runs: 测试运行次数
            warmup: 预热运行次数

        Returns:
            性能测试结果
        """
        function_name = getattr(func, '__name__', 'unknown')

        # 预热运行
        for _ in range(warmup):
            for test_input in test_inputs[:min(3, len(test_inputs))]:
                try:
                    if isinstance(test_input, (list, tuple)):
                        func(*test_input)
                    else:
                        func(test_input)
                except:
                    pass

        # 开始正式测试
        times = []
        memory_snapshots = []

        # 记录初始内存
        gc.collect()  # 强制垃圾回收
        initial_memory = self._get_memory_usage()

        for run in range(runs):
            run_times = []

            # 开始内存跟踪
            tracemalloc.start()

            for test_input in test_inputs:
                start_time = time.perf_counter()

                try:
                    if isinstance(test_input, (list, tuple)):
                        result = func(*test_input)
                    else:
                        result = func(test_input)
                except Exception as e:
                    # 如果函数执行失败，记录但继续
                    pass

                end_time = time.perf_counter()
                run_times.append(end_time - start_time)

            # 记录内存使用
            current, peak = tracemalloc.get_traced_memory()
            memory_snapshots.append(peak / 1024 / 1024)  # 转换为MB
            tracemalloc.stop()

            # 记录此次运行的平均时间
            if run_times:
                times.append(statistics.mean(run_times))

        # 计算最终内存使用
        gc.collect()
        final_memory = self._get_memory_usage()

        # 分析结果
        if not times:
            # 如果没有成功的测试，返回默认结果
            return PerformanceResult(
                function_name=function_name,
                avg_time=0.0,
                min_time=0.0,
                max_time=0.0,
                std_time=0.0,
                peak_memory=0.0,
                memory_growth=0.0,
                operations_per_second=0.0,
                time_complexity_estimate="unknown",
                test_runs=0,
                input_size=len(test_inputs)
            )

        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0.0

        peak_memory = max(memory_snapshots) if memory_snapshots else 0.0
        memory_growth = final_memory - initial_memory

        operations_per_second = len(test_inputs) / avg_time if avg_time > 0 else 0.0

        # 估计时间复杂度
        complexity_estimate = self._estimate_time_complexity(times, test_inputs)

        return PerformanceResult(
            function_name=function_name,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_time=std_time,
            peak_memory=peak_memory,
            memory_growth=memory_growth,
            operations_per_second=operations_per_second,
            time_complexity_estimate=complexity_estimate,
            test_runs=runs,
            input_size=len(test_inputs)
        )

    def benchmark_code_string(
        self,
        code: str,
        function_name: str,
        test_cases: List[Dict[str, Any]],
        runs: int = 5
    ) -> PerformanceResult:
        """对代码字符串进行性能测试

        Args:
            code: 代码字符串
            function_name: 主函数名
            test_cases: 测试用例，格式 [{"inputs": {...}, "expected": ...}, ...]
            runs: 测试运行次数

        Returns:
            性能测试结果
        """
        try:
            # 创建执行环境
            exec_globals = {}
            exec(code, exec_globals)

            func = exec_globals.get(function_name)
            if not func:
                raise ValueError(f"函数 {function_name} 未找到")

            # 准备测试输入
            test_inputs = []
            for case in test_cases:
                inputs = case.get('inputs', {})
                if isinstance(inputs, dict):
                    # 将字典参数转换为位置参数
                    test_inputs.append(list(inputs.values()))
                else:
                    test_inputs.append(inputs)

            return self.benchmark_function(func, test_inputs, runs)

        except Exception as e:
            # 如果测试失败，返回错误结果
            return PerformanceResult(
                function_name=function_name,
                avg_time=float('inf'),
                min_time=float('inf'),
                max_time=float('inf'),
                std_time=0.0,
                peak_memory=0.0,
                memory_growth=0.0,
                operations_per_second=0.0,
                time_complexity_estimate="error",
                test_runs=0,
                input_size=len(test_cases)
            )

    def compare_implementations(
        self,
        implementations: Dict[str, str],
        function_name: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, PerformanceResult]:
        """比较多个实现的性能

        Args:
            implementations: 实现代码字典 {"version1": code1, "version2": code2}
            function_name: 函数名
            test_cases: 测试用例

        Returns:
            每个实现的性能结果
        """
        results = {}

        for name, code in implementations.items():
            result = self.benchmark_code_string(code, function_name, test_cases)
            results[name] = result

        return results

    def _get_memory_usage(self) -> float:
        """获取当前内存使用量（MB）"""
        try:
            if self.process:
                return self.process.memory_info().rss / 1024 / 1024
            else:
                return 0.0
        except:
            return 0.0

    def _estimate_time_complexity(
        self,
        times: List[float],
        inputs: List[Any]
    ) -> str:
        """估计时间复杂度

        基于执行时间和输入大小的关系进行简单估计
        """
        if len(times) < 3:
            return "insufficient_data"

        # 简化的复杂度估计
        time_ratio = max(times) / min(times) if min(times) > 0 else float('inf')

        if time_ratio < 1.5:
            return "O(1)"  # 常数时间
        elif time_ratio < 3:
            return "O(log n)"  # 对数时间
        elif time_ratio < 10:
            return "O(n)"  # 线性时间
        elif time_ratio < 100:
            return "O(n log n)"  # 线性对数时间
        else:
            return "O(n²) or worse"  # 二次或更差


class PerformanceProfiler:
    """性能分析器 - 提供更详细的性能分析"""

    def __init__(self):
        self.benchmark = PerformanceBenchmark()

    def profile_function_scalability(
        self,
        code: str,
        function_name: str,
        input_generator: Callable[[int], Any],
        sizes: List[int] = None
    ) -> Dict[str, Any]:
        """分析函数的可扩展性

        Args:
            code: 函数代码
            function_name: 函数名
            input_generator: 输入生成器，接收大小参数
            sizes: 测试的输入大小列表

        Returns:
            可扩展性分析结果
        """
        if sizes is None:
            sizes = [10, 50, 100, 500, 1000]

        results = []

        for size in sizes:
            try:
                # 生成测试用例
                test_input = input_generator(size)
                test_cases = [{"inputs": test_input}]

                # 进行性能测试
                result = self.benchmark.benchmark_code_string(
                    code, function_name, test_cases, runs=3
                )

                results.append({
                    'input_size': size,
                    'avg_time': result.avg_time,
                    'memory_usage': result.peak_memory,
                    'ops_per_sec': result.operations_per_second
                })

            except Exception as e:
                results.append({
                    'input_size': size,
                    'avg_time': float('inf'),
                    'memory_usage': 0,
                    'ops_per_sec': 0,
                    'error': str(e)
                })

        return {
            'scalability_data': results,
            'complexity_analysis': self._analyze_scalability_trend(results)
        }

    def _analyze_scalability_trend(self, results: List[Dict]) -> str:
        """分析可扩展性趋势"""
        valid_results = [r for r in results if r['avg_time'] != float('inf')]

        if len(valid_results) < 3:
            return "insufficient_data"

        # 简单的趋势分析
        times = [r['avg_time'] for r in valid_results]
        sizes = [r['input_size'] for r in valid_results]

        # 计算时间增长率
        growth_rates = []
        for i in range(1, len(times)):
            if times[i-1] > 0:
                growth_rate = times[i] / times[i-1]
                size_ratio = sizes[i] / sizes[i-1]
                normalized_growth = growth_rate / size_ratio
                growth_rates.append(normalized_growth)

        if not growth_rates:
            return "unknown"

        avg_growth = sum(growth_rates) / len(growth_rates)

        if avg_growth < 1.2:
            return "excellent_scalability"
        elif avg_growth < 2.0:
            return "good_scalability"
        elif avg_growth < 5.0:
            return "moderate_scalability"
        else:
            return "poor_scalability"


# 使用示例
if __name__ == "__main__":
    profiler = PerformanceProfiler()

    # 测试代码
    sample_code = '''
def bubble_sort(arr):
    """冒泡排序"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
'''

    # 输入生成器
    def generate_sort_input(size):
        import random
        return {"arr": [random.randint(1, 1000) for _ in range(size)]}

    # 进行可扩展性测试
    scalability_result = profiler.profile_function_scalability(
        sample_code,
        "bubble_sort",
        generate_sort_input,
        sizes=[10, 20, 50]
    )

    print("可扩展性测试结果:", scalability_result)
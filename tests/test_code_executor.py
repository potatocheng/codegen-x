# 添加项目根目录到Python路径
from contextlib import AbstractContextManager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codegen.code_executor import CodeExecutor
import unittest

class TestCodeExectuor(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = CodeExecutor("")
        return super().setUp()

    def test_run_success(self):
        # Test successful code execution
        test_code = "print('Hello, World!')"
        result = self.executor.run(test_code)
        
        self.assertTrue(result.success)
        self.assertEqual(result.stdout.strip(), "Hello, World!")
        self.assertEqual(result.stderr, "")
        self.assertIsNone(result.error)

    def test_run_exception(self):
        test_code = "10/0" # This will raise a ZeroDivisionError
        result = self.executor.run(test_code)

        self.assertFalse(result.success)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        self.assertIn("division by zero", result.error or "")

    def test_run_output_stderr(self):
        test_code = "import sys; print('Error message', file=sys.stderr)"
        result = self.executor.run(test_code)

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "")
        self.assertIn("Error message", result.stderr)
        self.assertIsNone(result.error)

    def test_run_empty_code(self):
        # Test running with empty code
        result = self.executor.run("")
        
        self.assertFalse(result.success)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        self.assertIn("No code provided for execution.", result.error or "")

if __name__ == "__main__":
    unittest.main()
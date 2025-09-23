import unittest
from unittest.mock import patch, Mock, mock_open
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.controller import Controller


class TestController(unittest.TestCase):
    def setUp(self):
        self.controller = Controller("""完成算法题：给你一个 非严格递增排列 的数组 nums ，请你 原地 删除重复出现的元素，使每个元素 只出现一次 ，返回删除后数组的新长度。元素的 相对顺序 应该保持 一致 。然后返回 nums 中唯一元素的个数。
考虑 nums 的唯一元素的数量为 k ，你需要做以下事情确保你的题解可以被通过:
更改数组 nums ，使 nums 的前 k 个元素包含唯一元素，并按照它们最初在 nums 中出现的顺序排列。nums 的其余元素与 nums 的大小不重要。
返回 k 。""")
        return super().setUp()

    # 集成测试
    def test_controller(self):
        self.controller.run()
        # 验证生成的文件存在
        project_root = Path(__file__).parent.parent
        contract_file = project_root / "code" / "contract.json"
        logic_file = project_root / "code" / "logic.py"
        code_file = project_root / "code" / "generated_code.py"

        self.assertTrue(contract_file.exists())
        self.assertTrue(logic_file.exists())
        self.assertTrue(code_file.exists())


if __name__ == "__main__":
    unittest.main()

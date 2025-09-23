import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from config.config import load_config, get_prompts, format_messages

class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_cache = load_config()
        return super().setUp()
    
    def test_load_config(self):
        # Test if the configuration is loaded correctly
        self.assertIsInstance(self.config_cache, dict)

if __name__ == "__main__":
    unittest.main()
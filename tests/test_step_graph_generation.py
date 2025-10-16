import unittest
from unittest.mock import patch
import sys, os, re, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codegen.functional_code_generator import FunctionalCodeGenerator

class QueueMockLLM:
    """Mock LLM that returns queued responses sequentially."""
    def __init__(self, responses):
        self._responses = list(responses)
        self.call_count = 0
        self.model_name = "mock"
    def call(self, messages, **kwargs):  # mimic interface returning object with .content
        from llm.llm_interface import LLMResponse
        self.call_count += 1
        if not self._responses:
            raise RuntimeError("No more mock responses queued")
        content = self._responses.pop(0)
        return LLMResponse(content=content, usage={}, model=self.model_name, finish_reason="stop", response_time=0.0)

class TestStepGraphGeneration(unittest.TestCase):
    def _valid_spec_json(self):
        return json.dumps({
            "main_function": {
                "name": "demo_func",
                "purpose": "Demo purpose",
                "signature": {
                    "parameters": [
                        {"name": "nums", "type": "List[int]", "description": "list of ints", "constraints": ""}
                    ],
                    "return_type": "int",
                    "return_description": "length"
                },
                "exceptions": [],
                "complexity": "O(n)"
            },
            "helper_functions": [],
            "types": {
                "parameters": [ {"name": "nums", "type": "List[int]"} ],
                "returns": {"name": "result", "type": "int"},
                "exceptions": []
            },
            "pre": [ {"id": "P1", "expr": "nums is not None", "message": "not none"} ],
            "post": [ {"id": "Q1", "expr": "result >= 0", "message": ">=0"} ],
            "invariants": [],
            "examples": {"positive": [], "negative": []},
            "metamorphic_relations": [],
            "forbidden_apis": [],
            "complexity_guarantee": {"big_o": "O(n)", "witness_rules": []},
            "oracle": {"type": ""},
            "design_notes": "",
            "spec_version": 2
        }, ensure_ascii=False)

    def _valid_step_graph_json(self):
        return json.dumps({
            "version": 1,
            "steps": [
                {"id": "S1", "intent": "validate input", "pre_refs": ["P1"], "post_refs": [], "invariant_refs": [], "evidence_hooks": [], "parents": [], "children": ["S2"]},
                {"id": "S2", "intent": "compute length", "pre_refs": [], "post_refs": ["Q1"], "invariant_refs": [], "evidence_hooks": [], "parents": ["S1"], "children": []}
            ],
            "edges": [["S1", "S2"]],
            "order": ["S1", "S2"]
        })

    def test_step_graph_logic_generation(self):
        responses = [
            self._valid_spec_json(),      # spec
            self._valid_step_graph_json(),# step graph
            "# implementation placeholder"  # implementation
        ]
        with patch('codegen.functional_code_generator.create_llm', return_value=QueueMockLLM(responses)):
            gen = FunctionalCodeGenerator(request="demo request")
            gen.generate_spec()
            self.assertIsNotNone(gen.spec)
            gen.generate_step_graph()
            self.assertIsNotNone(gen.step_graph)
            gen.generate_logic_from_step_graph()
            self.assertIn('# STEP_GRAPH:', gen.logic)
            # Count anchors
            anchors = re.findall(r'# \[(S\d+)\]', gen.logic)
            self.assertEqual(len(anchors), len(gen.step_graph.steps))

    def test_spec_schema_repair(self):
        invalid_spec = "{}"  # will fail schema
        valid_spec = self._valid_spec_json()
        step_graph = self._valid_step_graph_json()
        impl = "# impl"
        responses = [invalid_spec, valid_spec, step_graph, impl]
        with patch('codegen.functional_code_generator.create_llm', return_value=QueueMockLLM(responses)):
            gen = FunctionalCodeGenerator(request="demo request")
            gen.generate_all()
            self.assertIsNotNone(gen.spec)
            self.assertIsNotNone(gen.step_graph)
            self.assertTrue(gen.logic.startswith('# STEP_GRAPH:'))

if __name__ == '__main__':
    unittest.main()

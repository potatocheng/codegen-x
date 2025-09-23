import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from codegen.graph import Graph, Node
from typing import List

class TestGraph(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = Graph()
        return super().setUp()

    def test_add_node(self):
        node_id = self.graph.add_node("code...", "debug_info...")
        self.assertEqual(len(self.graph.nodes), 1)
        node_ids = self.graph.topological_sort()
        self.assertIn(node_id, node_ids)

    def test_connect_nodes_success(self):
        node1_id = self.graph.add_node("", "")
        node2_id = self.graph.add_node("", "")
        self.assertEqual(len(self.graph.nodes), 2)
        self.assertTrue(self.graph.connect_nodes(node1_id, node2_id))
        self.assertEqual(self.graph.edges[node1_id], {node2_id})
        self.assertEqual(self.graph.reverse_edges[node2_id], {node1_id})

    def test_connect_nodes_cycle(self):
        node1_id = self.graph.add_node("", "")
        node2_id = self.graph.add_node("", "")
        self.graph.connect_nodes(node1_id, node2_id)

        node3_id = self.graph.add_node("", "")
        self.graph.connect_nodes(node2_id, node3_id)
        
        with self.assertRaises(ValueError):
            self.graph.connect_nodes(node3_id, node1_id)  # This should create a cycle


    def test_topological_sort(self):
        ids = []
        node1_id = self.graph.add_node("", "")
        ids.append(node1_id)
        node2_id = self.graph.add_node("", "")
        ids.append(node2_id)
        node3_id = self.graph.add_node("", "")
        ids.append(node3_id)
        node4_id = self.graph.add_node("", "")
        ids.append(node4_id)

        self.graph.connect_nodes(node1_id, node2_id)
        self.graph.connect_nodes(node1_id, node3_id)
        self.graph.connect_nodes(node2_id, node4_id)
        self.graph.connect_nodes(node3_id, node4_id)

        sorted_nodes = self.graph.topological_sort()
        self.assertEqual(len(sorted_nodes), 4)
        self.assertTrue(all(node_id in sorted_nodes for node_id in ids))



if __name__ == "__main__":
    unittest.main()
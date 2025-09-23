from dataclasses import dataclass, field
from typing import Dict, Set, List
import uuid
import json

@dataclass
class Node:
    id: str
    code: str
    debug_info: str # 以Json格式存储的调试信息
    

@dataclass
class Graph: # DAG 
    nodes: Dict[str, Node] = field(default_factory=dict) # key: node_id, value: Node
    edges: Dict[str, Set[str]] = field(default_factory=dict) # key: node_id, value: set of connected node_ids
    reverse_edges: Dict[str, Set[str]] = field(default_factory=dict) # key: node_id, value: set of incoming node_ids

    def add_node(self, code: str, debug_info: str) -> str:
        """ Add a new node to the graph """
        new_node = Node(id=str(uuid.uuid4()), code=code, debug_info=debug_info)
        self.nodes[new_node.id] = new_node
        self.edges[new_node.id] = set()
        self.reverse_edges[new_node.id] = set()
        
        return new_node.id

    def connect_nodes(self, src_id: str, dest_id: str) -> bool:
        """ connect nodes in the graph with a given code and debug info """
        if src_id not in self.nodes or dest_id not in self.nodes:
            raise ValueError("Source or destination node does not exist in the graph.")
        
        if dest_id == src_id:
            raise ValueError("Cannot connect a node to itself.")

        if self._would_create_cycle(src_id, dest_id):
            raise ValueError("Adding this edge would create a cycle in the graph.")

        self.edges[src_id].add(dest_id)
        self.reverse_edges[dest_id].add(src_id)
        return True
    
    def _would_create_cycle(self, src_id: str, dest_id: str) -> bool:
        """ Check if adding an edge would create a cycle in the graph """
        visited = set()
        stack = [dest_id]

        while stack:
            current = stack.pop()
            if current == src_id:
                return True
            
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, []))

        return False

    def topological_sort(self) -> List[str]: 
        """ 
        Perform a topological sort on the graph for acquire a code-generation order 
        Returns:
            List[str]: A list of node IDs in topological order.
        """
        in_degree = {node_id: len(self.reverse_edges.get(node_id, [])) 
                    for node_id in self.nodes}
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        sorted_nodes = []
        
        while queue:
            current_node_id = queue.pop(0)
            sorted_nodes.append(current_node_id)

            for node_id in self.edges[current_node_id]:
                in_degree[node_id] -= 1
                if(in_degree[node_id] == 0):
                    queue.append(node_id)

        if len(sorted_nodes) != len(self.nodes):
            raise ValueError("Graph has at least one cycle, topological sort not possible.")

        return sorted_nodes
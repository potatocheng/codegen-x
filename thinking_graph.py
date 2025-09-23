from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
import uuid
from graphviz import Digraph
import json
from logger import logger

@dataclass
class ThoughtNode:
    """
    代表思考图中的一个节点。
    
    这个结构不仅存储了节点的描述，还增加了`status`来跟踪其生命周期
    (例如，已规划、已生成、已优化)，以及`content`来存储与此节点
    相关的具体产出（例如，生成的代码片段）。
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    component: str = ''
    description: str = ''
    status: str = 'planned'
    content: str = ''
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """验证节点数据的有效性"""
        if not self.component:
            raise ValueError("Component name cannot be empty")
        if self.status not in ['planned', 'generating', 'completed', 'error', 'refined']:
            raise ValueError(f"Invalid status: {self.status}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """将节点转换为字典格式"""
        return {
            'id': self.id,
            'component': self.component,
            'description': self.description,
            'status': self.status,
            'content': self.content,
            'confidence': self.confidence,
            'metadata': self.metadata or {}
        }

    def to_json(self) -> str:
        """将节点序列化为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def update_status(self, new_status: str, confidence: Optional[float] = None):
        """更新节点状态和置信度"""
        if new_status not in ['planned', 'generating', 'completed', 'error', 'refined']:
            raise ValueError(f"Invalid status: {new_status}")
        
        old_status = self.status
        self.status = new_status
        
        if confidence is not None:
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("Confidence must be between 0.0 and 1.0")
            self.confidence = confidence
        
        logger.debug(f"节点 {self.component} 状态更新: {old_status} -> {new_status}")


class ThinkingGraph:
    """
    Graph of Thinking (GoT) 的图结构实现。
    
    优化后的版本包含了更强的错误处理、性能优化和功能扩展。
    """
    
    def __init__(self) -> None:
        self.nodes: Dict[str, ThoughtNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # 使用 Set 避免重复边
        self.reverse_edges: Dict[str, Set[str]] = {}
        self._component_to_id_cache: Optional[Dict[str, str]] = None  # 缓存组件名到ID的映射
        
        logger.info("创建新的 ThinkingGraph 实例")

    def _invalidate_cache(self):
        """使缓存失效"""
        self._component_to_id_cache = None

    def _get_component_to_id_mapping(self) -> Dict[str, str]:
        """获取组件名到ID的映射（带缓存）"""
        if self._component_to_id_cache is None:
            self._component_to_id_cache = {
                node.component: node.id for node in self.nodes.values()
            }
        return self._component_to_id_cache

    def add_thought(self, component: str, description: str, **kwargs) -> str:
        """添加一个思考节点"""
        try:
            # 检查组件名是否已存在
            if any(node.component == component for node in self.nodes.values()):
                logger.warning(f"组件名 '{component}' 已存在")
                raise ValueError(f"Component '{component}' already exists")

            node = ThoughtNode(
                component=component,
                description=description,
                **kwargs
            )
            
            self.nodes[node.id] = node
            self.edges[node.id] = set()
            self.reverse_edges[node.id] = set()
            
            self._invalidate_cache()
            logger.log_graph_operation("ADD_NODE", component, node.id)
            logger.debug(f"添加节点成功: {component}")
            
            return node.id
            
        except Exception as e:
            logger.error(f"添加节点失败: {component} - {str(e)}")
            raise

    def remove_thought(self, node_id: str) -> bool:
        """移除一个思考节点及其所有连接"""
        if node_id not in self.nodes:
            logger.warning(f"尝试移除不存在的节点: {node_id}")
            return False
        
        try:
            component = self.nodes[node_id].component
            
            # 移除所有相关的边
            for child_id in self.edges[node_id]:
                self.reverse_edges[child_id].discard(node_id)
            
            for parent_id in self.reverse_edges[node_id]:
                self.edges[parent_id].discard(node_id)
            
            # 移除节点
            del self.nodes[node_id]
            del self.edges[node_id]
            del self.reverse_edges[node_id]
            
            self._invalidate_cache()
            logger.log_graph_operation("REMOVE_NODE", component, node_id)
            return True
            
        except Exception as e:
            logger.error(f"移除节点失败: {node_id} - {str(e)}")
            return False

    def connect_thoughts(self, from_id: str, to_id: str) -> bool:
        """连接两个思考节点"""
        if from_id not in self.nodes:
            logger.error(f"源节点不存在: {from_id}")
            return False
        
        if to_id not in self.nodes:
            logger.error(f"目标节点不存在: {to_id}")
            return False
        
        if from_id == to_id:
            logger.error("不能连接节点到自身")
            return False
        
        # 检查是否会创建环
        if self._would_create_cycle(from_id, to_id):
            logger.error(f"连接 {from_id} -> {to_id} 会创建环")
            return False
        
        try:
            self.edges[from_id].add(to_id)
            self.reverse_edges[to_id].add(from_id)
            
            from_component = self.nodes[from_id].component
            to_component = self.nodes[to_id].component
            logger.log_graph_operation("CONNECT_NODES")
            logger.debug(f"连接节点: {from_component} -> {to_component}")
            return True
            
        except Exception as e:
            logger.error(f"连接节点失败: {from_id} -> {to_id} - {str(e)}")
            return False

    def disconnect_thoughts(self, from_id: str, to_id: str) -> bool:
        """断开两个思考节点的连接"""
        if from_id not in self.nodes or to_id not in self.nodes:
            logger.error(f"节点不存在: {from_id} 或 {to_id}")
            return False
        
        try:
            self.edges[from_id].discard(to_id)
            self.reverse_edges[to_id].discard(from_id)
            
            from_component = self.nodes[from_id].component
            to_component = self.nodes[to_id].component
            logger.debug(f"断开连接: {from_component} -> {to_component}")
            return True
            
        except Exception as e:
            logger.error(f"断开连接失败: {from_id} -> {to_id} - {str(e)}")
            return False

    def _would_create_cycle(self, from_id: str, to_id: str) -> bool:
        """检查添加边是否会创建环"""
        # 使用DFS检查从to_id是否能到达from_id
        visited = set()
        stack = [to_id]
        
        while stack:
            current = stack.pop()
            if current == from_id:
                return True
            
            if current in visited:
                continue
            
            visited.add(current)
            stack.extend(self.edges.get(current, []))
        
        return False

    def get_node(self, node_id: str) -> Optional[ThoughtNode]:
        """通过ID获取节点"""
        return self.nodes.get(node_id)

    def get_node_by_component(self, component: str) -> Optional[ThoughtNode]:
        """通过组件名获取节点"""
        component_to_id = self._get_component_to_id_mapping()
        node_id = component_to_id.get(component)
        return self.nodes.get(node_id) if node_id else None

    def get_children(self, node_id: str) -> List[ThoughtNode]:
        """获取一个节点的所有直接子节点"""
        if node_id not in self.nodes:
            return []
        return [self.nodes[child_id] for child_id in self.edges.get(node_id, [])]

    def get_parents(self, node_id: str) -> List[ThoughtNode]:
        """获取一个节点的所有直接父节点"""
        if node_id not in self.nodes:
            return []
        return [self.nodes[parent_id] for parent_id in self.reverse_edges.get(node_id, [])]

    def get_root_nodes(self) -> List[ThoughtNode]:
        """获取图中所有的根节点"""
        return [node for node_id, node in self.nodes.items() 
                if not self.reverse_edges.get(node_id)]

    def get_leaf_nodes(self) -> List[ThoughtNode]:
        """获取图中所有的叶子节点"""
        return [node for node_id, node in self.nodes.items() 
                if not self.edges.get(node_id)]

    def get_all_ancestors(self, node_id: str) -> Dict[str, ThoughtNode]:
        """获取一个节点的所有祖先节点"""
        if node_id not in self.nodes:
            logger.warning(f"节点不存在: {node_id}")
            return {}
        
        ancestors = {}
        visited = set()
        queue = list(self.reverse_edges.get(node_id, []))
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            
            visited.add(current_id)
            ancestors[current_id] = self.nodes[current_id]
            queue.extend(self.reverse_edges.get(current_id, []))
        
        return ancestors

    def get_all_descendants(self, node_id: str) -> Dict[str, ThoughtNode]:
        """获取一个节点的所有后代节点"""
        if node_id not in self.nodes:
            logger.warning(f"节点不存在: {node_id}")
            return {}
        
        descendants = {}
        visited = set()
        queue = list(self.edges.get(node_id, []))
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            
            visited.add(current_id)
            descendants[current_id] = self.nodes[current_id]
            queue.extend(self.edges.get(current_id, []))
        
        return descendants

    def topological_sort(self) -> List[ThoughtNode]:
        """对图进行拓扑排序"""
        logger.info("开始拓扑排序")
        
        in_degree = {node_id: len(self.reverse_edges.get(node_id, [])) 
                    for node_id in self.nodes}
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        sorted_order = []

        while queue:
            current_id = queue.pop(0)
            sorted_order.append(self.nodes[current_id])

            for neighbor_id in self.edges.get(current_id, []):
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        if len(sorted_order) != len(self.nodes):
            logger.error("检测到图中存在环，无法进行拓扑排序")
            raise ValueError("Graph has at least one cycle and cannot be topologically sorted.")

        logger.info(f"拓扑排序完成，共 {len(sorted_order)} 个节点")
        return sorted_order

    def _find_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """使用BFS查找路径"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return None

        queue = [(start_id, [start_id])]
        visited = {start_id}

        while queue:
            current, path = queue.pop(0)

            if current == end_id:
                return path

            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_thinking_chain(self, node_id: str) -> List[ThoughtNode]:
        """获取到达目标节点的思考链"""
        if node_id not in self.nodes:
            logger.warning(f"节点不存在: {node_id}")
            return []

        for root in self.get_root_nodes():
            path_ids = self._find_path(root.id, node_id)
            if path_ids:
                return [self.nodes[id] for id in path_ids]

        return [self.nodes[node_id]]

    def get_statistics(self) -> Dict[str, Any]:
        """获取图的统计信息"""
        total_nodes = len(self.nodes)
        total_edges = sum(len(edges) for edges in self.edges.values())
        
        status_count = {}
        for node in self.nodes.values():
            status_count[node.status] = status_count.get(node.status, 0) + 1
        
        return {
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'root_nodes': len(self.get_root_nodes()),
            'leaf_nodes': len(self.get_leaf_nodes()),
            'status_distribution': status_count,
            'average_confidence': sum(node.confidence for node in self.nodes.values()) / total_nodes if total_nodes > 0 else 0.0
        }

    def validate_graph(self) -> Tuple[bool, List[str]]:
        """验证图的完整性"""
        errors = []
        
        # 检查边的一致性
        for from_id, to_ids in self.edges.items():
            if from_id not in self.nodes:
                errors.append(f"边的源节点不存在: {from_id}")
            
            for to_id in to_ids:
                if to_id not in self.nodes:
                    errors.append(f"边的目标节点不存在: {to_id}")
                elif from_id not in self.reverse_edges.get(to_id, set()):
                    errors.append(f"反向边不一致: {from_id} -> {to_id}")
        
        # 检查是否有环
        try:
            self.topological_sort()
        except ValueError:
            errors.append("图中存在环")
        
        # 检查组件名唯一性
        components = [node.component for node in self.nodes.values()]
        if len(components) != len(set(components)):
            errors.append("存在重复的组件名")
        
        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """将整个图转换为字典格式"""
        return {
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'edges': {from_id: list(to_ids) for from_id, to_ids in self.edges.items()},
            'statistics': self.get_statistics()
        }

    def to_json(self) -> str:
        """将图序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_graphviz(self) -> Digraph:
        """转换为Graphviz图形"""
        dot = Digraph('GoT_Code_Plan', comment='代码规划依赖图')
        dot.attr('node', shape='box', style='rounded', fontname='Inter')
        dot.attr(rankdir='TB', splines='ortho')

        status_colors = {
            'planned': '#f0f9ff',
            'generating': '#fefce8',
            'completed': '#f0fdf4',
            'error': '#fef2f2',
            'refined': '#faf5ff',
        }

        for node_id, node in self.nodes.items():
            label = f"<{node.component}<br/><font point-size='10'>({node.description})</font>>"
            color = status_colors.get(node.status, '#f8fafc')
            dot.node(node_id, label, fillcolor=color, style='filled')

        for from_id, to_ids in self.edges.items():
            for to_id in to_ids:
                dot.edge(from_id, to_id)

        return dot

    def __len__(self) -> int:
        """返回节点数量"""
        return len(self.nodes)

    def __contains__(self, node_id: str) -> bool:
        """检查节点是否存在"""
        return node_id in self.nodes

    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_statistics()
        return f"ThinkingGraph(nodes={stats['total_nodes']}, edges={stats['total_edges']})"


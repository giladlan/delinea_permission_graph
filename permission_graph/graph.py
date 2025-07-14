from typing import List

from permission_graph.edge import Edge
from permission_graph.node import Node


class Graph:
    def __init__(self):
        self.edges: List[Edge] = list()
        self._edge_keys = set()
        self.nodes: dict[str, Node] = dict()

    def add_node(self, new_node: Node):
        existing = self.nodes.get(new_node.node_id)
        if not existing:
            self.nodes[new_node.node_id] = new_node

    def add_nodes(self, new_nodes: List[Node]):
        for new_node in new_nodes:
            self.add_node(new_node)

    def add_edge(self, new_edge: Edge):
        _edge_key = (
            new_edge.from_node_id,
            new_edge.to_node_id,
            new_edge.edge_type,
            new_edge.binding_role,
            new_edge.member_type
        )
        if _edge_key not in self._edge_keys:
            self._edge_keys.add(_edge_key)
            self.edges.append(new_edge)

    def add_edges(self, new_edges: List[Edge]):
        for new_edge in new_edges:
            self.add_edge(new_edge)

    def get_node_by_id(self, node_id: str):
        return self.nodes.get(node_id.strip().lower())

    def get_user_permissions(self, user_email: str):
        pass

from collections import defaultdict
from typing import List, Dict, Tuple, Set

from permission_graph.edge import Edge, EdgeType
from permission_graph.exceptions import ResourceNotFound, InvalidResourceType
from permission_graph.graph import Graph
from permission_graph.node import Node, NodeType

DELIMITER = '/'


class PermissionGraph:
    def __init__(self):
        self.graph = Graph()

    def build_from_parsed_permissions(self, permissions: List[dict]):
        for resource in permissions:
            resource_id = self._extract_resource_id(resource)
            resource_sub_type = self._extract_resource_sub_type(resource)

            resource_node = Node(resource_id, NodeType.RESOURCE, resource_sub_type)
            self.graph.add_node(resource_node)

            raw_policy = resource.get('iam_policy')
            policy_nodes, policy_edges = self._create_policy_binding_nodes(raw_policy,
                                                                           resource_node.node_id,
                                                                           self.graph.nodes)
            self.graph.add_nodes(policy_nodes)
            self.graph.add_edges(policy_edges)

            resource['resource_node_id'] = resource_id

        for resource in permissions:
            resource_node_id = resource['resource_node_id']
            resource_ancestors = resource.get('ancestors')
            ancestor_nodes, ancestor_edged = self._create_ancestor_nodes(resource_ancestors,
                                                                         resource_node_id,
                                                                         self.graph.nodes)
            self.graph.add_nodes(ancestor_nodes)
            self.graph.add_edges(ancestor_edged)

    @staticmethod
    def _extract_resource_id(resource: dict) -> str:
        _name = resource.get('name').strip().lower().split(DELIMITER)
        resource_id = DELIMITER.join(_name[-2:])
        return resource_id

    @staticmethod
    def _extract_resource_sub_type(resource: dict) -> str:
        node_sub_type = resource.get('asset_type').split(DELIMITER)[-1].strip().lower()
        return node_sub_type

    @staticmethod
    def _create_policy_binding_nodes(resource_policy: dict, parent_node_id: str,
                                     existing_nodes: Dict[str, Node]) -> tuple[List[Node], List[Edge]]:
        _bindings = resource_policy.get('bindings', [])

        nodes = list()
        edges = list()

        for binding in _bindings:
            binding_role = binding.get('role').strip().lower()
            for member in binding.get('members'):
                member_type, member_id = member.split(':')
                member_id = member_id.strip().lower()

                member_node_id = member_id if member_id in existing_nodes else None
                if not member_node_id:
                    member_node = Node(node_id=member_id, node_type=NodeType.IDENTITY)
                    member_node_id = member_node.node_id
                    nodes.append(member_node)

                edge = Edge(member_node_id, parent_node_id, EdgeType.PERMISSION, binding_role, member_type)
                edges.append(edge)

        return nodes, edges

    @staticmethod
    def _create_ancestor_nodes(ancestors: List[str], base_node_id: str, existing_nodes: Dict[str, Node]) -> tuple[
        List[Node], List[Edge]]:
        nodes: List[Node] = list()
        edges: List[Edge] = list()

        child_node_id = base_node_id
        for ancestor_id in ancestors[1:]:  # First element is the same as base node

            ancestor_id = ancestor_id.strip().lower()

            if ancestor_id not in existing_nodes:
                ancestor_node = Node(ancestor_id, NodeType.RESOURCE)
                ancestor_node_id = ancestor_node.node_id
                nodes.append(ancestor_node)

            ancestor_edge = Edge(child_node_id, ancestor_id, EdgeType.PARENT)
            edges.append(ancestor_edge)

            child_node_id = ancestor_id

        return nodes, edges

    def get_hierarchy_for_resource(self, resource_id: str):
        node = self.graph.get_node_by_id(resource_id)
        if not node:
            raise ResourceNotFound(f'Resource with id {resource_id} not found')
        if node.node_type != NodeType.RESOURCE:
            raise InvalidResourceType(f'Resource with id {resource_id} is of invalid type')

        resource_hierarchy = list()
        visited_nodes = set()

        child_to_parent_mapping: Dict[str, List[str]] = self.get_child_to_parent_mapping(self.graph.edges,
                                                                                         EdgeType.PARENT)

        def dfs(child_id):
            for edge in self.graph.edges:
                for parent_id in child_to_parent_mapping.get(child_id, []):
                    if parent_id not in visited_nodes:
                        visited_nodes.add(parent_id)
                        resource_hierarchy.append(parent_id)
                        dfs(parent_id)

        dfs(node.node_id)
        return resource_hierarchy

    def get_permissions_for_identity(self, user_id: str):
        user_node = self.graph.get_node_by_id(user_id)
        if not user_node:
            raise ResourceNotFound(f'Resource with id {user_id} not found')
        if user_node.node_type != NodeType.IDENTITY:
            raise InvalidResourceType(f'Resource with id {user_id} is of invalid type')

        results = list()
        visited: Set[Tuple[str, str]] = set()

        parent_to_child_mapping: Dict[str, List[str]] = self.get_parent_to_child_mapping(self.graph.edges,
                                                                                         EdgeType.PARENT)

        for edge in self.graph.edges:
            if edge.from_node_id == user_node.node_id and edge.edge_type == EdgeType.PERMISSION:  # user_node.node_id instead of user_id just to be safe
                role = edge.binding_role

                resource_children = [edge.to_node_id]

                while resource_children:
                    current_node_id = resource_children.pop(0)
                    if (current_node_id, role) in visited:
                        continue

                    visited.add((current_node_id, role))

                    current_node = self.graph.get_node_by_id(current_node_id)
                    if current_node and current_node.node_type == NodeType.RESOURCE:
                        results.append((current_node.node_id, current_node.sub_type, role))

                    resource_children.extend(parent_to_child_mapping.get(current_node_id, []))

        return results

    @staticmethod
    def get_child_to_parent_mapping(edges: List[Edge], filter_for_type: EdgeType = None):
        mapping = defaultdict(list)
        for edge in edges:
            if filter_for_type is None or edge.edge_type == filter_for_type:
                mapping[edge.from_node_id].append(edge.to_node_id)

        return mapping

    @staticmethod
    def get_parent_to_child_mapping(edges: List[Edge], filter_for_type: EdgeType = None):
        mapping = defaultdict(list)
        for edge in edges:
            if filter_for_type is None or edge.edge_type == filter_for_type:
                mapping[edge.to_node_id].append(edge.from_node_id)

        return mapping

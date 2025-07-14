from enum import Enum


class NodeType(Enum):
    RESOURCE = 'resource'
    IDENTITY = 'identity'


class Node:
    def __init__(self, node_id: str, node_type: NodeType, sub_type: str = None):
        self.node_id: str = node_id
        self.node_type: NodeType = node_type
        self.sub_type: str = sub_type

    def __repr__(self):
        return f'{self.node_id} # {self.node_type} # {self.sub_type}'

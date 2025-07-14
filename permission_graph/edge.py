from enum import Enum
from uuid import uuid4

from permission_graph.node import Node


class EdgeType(Enum):
    PARENT = 'parent'
    PERMISSION = 'permission'


class Edge:
    def __init__(self, from_node_id: str, to_node_id: str, edge_type: EdgeType, binding_role: str = None, member_type:str=None):
        self.edge_id = str(uuid4())[:8]
        self.from_node_id = from_node_id # Child
        self.to_node_id = to_node_id # Parent
        self.edge_type = edge_type
        self.binding_role = binding_role.lower() if binding_role else binding_role
        self.member_type= member_type.lower() if member_type else member_type

    def __repr__(self):
        _repr =  f'{self.edge_id} # {self.edge_type}'
        _repr+= f' # {self.binding_role}' if self.binding_role else ''
        _repr+= f' # {self.member_type}' if self.member_type else ''

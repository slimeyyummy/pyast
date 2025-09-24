"""
JSON serialization for PyAST.

This module provides functionality to serialize and deserialize AST trees to/from JSON.
"""

import json
from typing import Dict, List, Any, Union
from .nodes import Node, Program, NODE_CLASSES, NodeType


class Serializer:
    """Handles serialization and deserialization of AST nodes."""

    @staticmethod
    def to_json(node: Node, indent: int = 2) -> str:
        """Convert AST node to JSON string."""
        data = Serializer._node_to_dict(node)
        return json.dumps(data, indent=indent, default=str)

    @staticmethod
    def from_json(json_str: str) -> Node:
        """Create AST node from JSON string."""
        data = json.loads(json_str)
        return Serializer._node_from_dict(data)

    @staticmethod
    def _node_to_dict(node: Node) -> Dict[str, Any]:
        """Convert node to dictionary."""
        result = node.to_dict()

        # Add specific attributes based on node type
        if hasattr(node, 'body') and isinstance(node.body, list):
            result['body'] = [Serializer._node_to_dict(child) for child in node.body if isinstance(child, Node)]
        if hasattr(node, 'value') and isinstance(node.value, Node):
            result['value'] = Serializer._node_to_dict(node.value)
        if hasattr(node, 'left') and isinstance(node.left, Node):
            result['left'] = Serializer._node_to_dict(node.left)
        if hasattr(node, 'right') and isinstance(node.right, Node):
            result['right'] = Serializer._node_to_dict(node.right)
        if hasattr(node, 'func') and isinstance(node.func, Node):
            result['func'] = Serializer._node_to_dict(node.func)
        if hasattr(node, 'test') and isinstance(node.test, Node):
            result['test'] = Serializer._node_to_dict(node.test)
        if hasattr(node, 'target') and isinstance(node.target, Node):
            result['target'] = Serializer._node_to_dict(node.target)
        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            result['iter'] = Serializer._node_to_dict(node.iter)
        if hasattr(node, 'targets') and isinstance(node.targets, list):
            result['targets'] = [Serializer._node_to_dict(target) for target in node.targets if isinstance(target, Node)]
        if hasattr(node, 'args') and isinstance(node.args, list):
            result['args'] = [Serializer._node_to_dict(arg) for arg in node.args if isinstance(arg, Node)]
        if hasattr(node, 'bases') and isinstance(node.bases, list):
            result['bases'] = [Serializer._node_to_dict(base) for base in node.bases if isinstance(base, Node)]
        if hasattr(node, 'decorator_list') and isinstance(node.decorator_list, list):
            result['decorator_list'] = [Serializer._node_to_dict(decorator) for decorator in node.decorator_list if isinstance(decorator, Node)]
        if hasattr(node, 'orelse') and isinstance(node.orelse, list):
            result['orelse'] = [Serializer._node_to_dict(child) for child in node.orelse if isinstance(child, Node)]
        if hasattr(node, 'handlers') and isinstance(node.handlers, list):
            result['handlers'] = [Serializer._node_to_dict(handler) for handler in node.handlers if isinstance(handler, Node)]
        if hasattr(node, 'finalbody') and isinstance(node.finalbody, list):
            result['finalbody'] = [Serializer._node_to_dict(child) for child in node.finalbody if isinstance(child, Node)]
        if hasattr(node, 'items') and isinstance(node.items, list):
            result['items'] = node.items  # These are already dicts
        if hasattr(node, 'keywords') and isinstance(node.keywords, list):
            result['keywords'] = node.keywords  # These are already dicts
        if hasattr(node, 'names') and isinstance(node.names, list):
            result['names'] = node.names  # These are already dicts
        if hasattr(node, 'type') and isinstance(node.type, Node):
            result['type'] = Serializer._node_to_dict(node.type)
        if hasattr(node, 'exc') and isinstance(node.exc, Node):
            result['exc'] = Serializer._node_to_dict(node.exc)
        if hasattr(node, 'cause') and isinstance(node.cause, Node):
            result['cause'] = Serializer._node_to_dict(node.cause)
        if hasattr(node, 'msg') and isinstance(node.msg, Node):
            result['msg'] = Serializer._node_to_dict(node.msg)

        return result

    @staticmethod
    def _node_from_dict(data: Dict[str, Any]) -> Node:
        """Create node from dictionary."""
        # Handle nested structures
        data_copy = data.copy()

        # Recursively convert nested node structures
        if 'body' in data_copy and isinstance(data_copy['body'], list):
            data_copy['body'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['body']]
        if 'value' in data_copy and isinstance(data_copy['value'], dict):
            data_copy['value'] = Serializer._node_from_dict(data_copy['value'])
        if 'left' in data_copy and isinstance(data_copy['left'], dict):
            data_copy['left'] = Serializer._node_from_dict(data_copy['left'])
        if 'right' in data_copy and isinstance(data_copy['right'], dict):
            data_copy['right'] = Serializer._node_from_dict(data_copy['right'])
        if 'func' in data_copy and isinstance(data_copy['func'], dict):
            data_copy['func'] = Serializer._node_from_dict(data_copy['func'])
        if 'test' in data_copy and isinstance(data_copy['test'], dict):
            data_copy['test'] = Serializer._node_from_dict(data_copy['test'])
        if 'target' in data_copy and isinstance(data_copy['target'], dict):
            data_copy['target'] = Serializer._node_from_dict(data_copy['target'])
        if 'iter' in data_copy and isinstance(data_copy['iter'], dict):
            data_copy['iter'] = Serializer._node_from_dict(data_copy['iter'])
        if 'targets' in data_copy and isinstance(data_copy['targets'], list):
            data_copy['targets'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['targets']]
        if 'args' in data_copy and isinstance(data_copy['args'], list):
            data_copy['args'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['args']]
        if 'bases' in data_copy and isinstance(data_copy['bases'], list):
            data_copy['bases'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['bases']]
        if 'decorator_list' in data_copy and isinstance(data_copy['decorator_list'], list):
            data_copy['decorator_list'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['decorator_list']]
        if 'orelse' in data_copy and isinstance(data_copy['orelse'], list):
            data_copy['orelse'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['orelse']]
        if 'handlers' in data_copy and isinstance(data_copy['handlers'], list):
            data_copy['handlers'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['handlers']]
        if 'finalbody' in data_copy and isinstance(data_copy['finalbody'], list):
            data_copy['finalbody'] = [Serializer._node_from_dict(item) if isinstance(item, dict) else item for item in data_copy['finalbody']]
        if 'type' in data_copy and isinstance(data_copy['type'], dict):
            data_copy['type'] = Serializer._node_from_dict(data_copy['type'])
        if 'exc' in data_copy and isinstance(data_copy['exc'], dict):
            data_copy['exc'] = Serializer._node_from_dict(data_copy['exc'])
        if 'cause' in data_copy and isinstance(data_copy['cause'], dict):
            data_copy['cause'] = Serializer._node_from_dict(data_copy['cause'])
        if 'msg' in data_copy and isinstance(data_copy['msg'], dict):
            data_copy['msg'] = Serializer._node_from_dict(data_copy['msg'])

        return Node.from_dict(data_copy)

    @staticmethod
    def serialize_tree(tree: Node, filename: str) -> None:
        """Serialize AST tree to JSON file."""
        with open(filename, 'w') as f:
            f.write(Serializer.to_json(tree))

    @staticmethod
    def deserialize_tree(filename: str) -> Node:
        """Deserialize AST tree from JSON file."""
        with open(filename, 'r') as f:
            return Serializer.from_json(f.read())

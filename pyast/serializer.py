"""
JSON serialization for PyAST.

This module provides functionality to serialize and deserialize AST trees to/from JSON.
"""

import json
from typing import Dict, List, Any, Union
from collections import deque
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from nodes import Node, Program, NODE_CLASSES, NodeType


class Serializer:
    """Handles serialization and deserialization of AST nodes."""

    # Mapping of node types to their attributes that contain nodes or lists of nodes
    NODE_ATTRIBUTES = {
        NodeType.PROGRAM: {
            'single_nodes': [],
            'node_lists': ['body']
        },
        NodeType.FUNCTION_DEF: {
            'single_nodes': [],
            'node_lists': ['body', 'decorator_list']
        },
        NodeType.CLASS_DEF: {
            'single_nodes': [],
            'node_lists': ['bases', 'body', 'decorator_list']
        },
        NodeType.ASSIGN: {
            'single_nodes': ['value'],
            'node_lists': ['targets']
        },
        NodeType.BIN_OP: {
            'single_nodes': ['left', 'right'],
            'node_lists': []
        },
        NodeType.NAME: {
            'single_nodes': [],
            'node_lists': []
        },
        NodeType.CONSTANT: {
            'single_nodes': [],
            'node_lists': []
        },
        NodeType.CALL: {
            'single_nodes': ['func'],
            'node_lists': ['args']
        },
        NodeType.ATTRIBUTE: {
            'single_nodes': ['value'],
            'node_lists': []
        },
        NodeType.IF: {
            'single_nodes': ['test'],
            'node_lists': ['body', 'orelse']
        },
        NodeType.FOR: {
            'single_nodes': ['target', 'iter'],
            'node_lists': ['body', 'orelse']
        },
        NodeType.WHILE: {
            'single_nodes': ['test'],
            'node_lists': ['body', 'orelse']
        },
        NodeType.RETURN: {
            'single_nodes': ['value'],
            'node_lists': []
        },
        NodeType.BREAK: {
            'single_nodes': [],
            'node_lists': []
        },
        NodeType.CONTINUE: {
            'single_nodes': [],
            'node_lists': []
        },
        NodeType.IMPORT: {
            'single_nodes': [],
            'node_lists': []
        },
        NodeType.IMPORT_FROM: {
            'single_nodes': [],
            'node_lists': []
        },
        NodeType.TRY: {
            'single_nodes': [],
            'node_lists': ['body', 'handlers', 'orelse', 'finalbody']
        },
        NodeType.EXCEPT_HANDLER: {
            'single_nodes': ['type'],
            'node_lists': ['body']
        },
        NodeType.WITH: {
            'single_nodes': [],
            'node_lists': ['body']
        },
        NodeType.RAISE: {
            'single_nodes': ['exc', 'cause'],
            'node_lists': []
        },
        NodeType.ASSERT: {
            'single_nodes': ['test', 'msg'],
            'node_lists': []
        },
        NodeType.PASS: {
            'single_nodes': [],
            'node_lists': []
        },
        NodeType.EXPR: {
            'single_nodes': ['value'],
            'node_lists': []
        },
        NodeType.COMMENT: {
            'single_nodes': [],
            'node_lists': []
        }
    }

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
        """Convert node to dictionary using iterative approach."""
        if not isinstance(node, Node):
            return node

        # Use iterative BFS approach with a queue - much faster!
        queue = deque([node])
        results = {}

        while queue:
            current_node = queue.popleft()

            # Get the base dictionary representation
            result = current_node.to_dict()

            # Get node type specific attributes
            node_type = current_node.node_type
            attrs = Serializer.NODE_ATTRIBUTES.get(node_type, {'single_nodes': [], 'node_lists': []})

            # Process single node attributes
            for attr_name in attrs['single_nodes']:
                if hasattr(current_node, attr_name):
                    attr_value = getattr(current_node, attr_name)
                    if isinstance(attr_value, Node):
                        # Add to queue for processing
                        queue.append(attr_value)
                        # Store reference - will be replaced later
                        result[attr_name] = f"__NODE_REF__{id(attr_value)}"
                    else:
                        result[attr_name] = attr_value

            # Process node list attributes
            for attr_name in attrs['node_lists']:
                if hasattr(current_node, attr_name):
                    attr_value = getattr(current_node, attr_name)
                    if isinstance(attr_value, list):
                        processed_list = []
                        for item in attr_value:
                            if isinstance(item, Node):
                                # Add to queue for processing
                                queue.append(item)
                                # Store reference - will be replaced later
                                processed_list.append(f"__NODE_REF__{id(item)}")
                            else:
                                processed_list.append(item)
                        result[attr_name] = processed_list
                    else:
                        result[attr_name] = attr_value

            # Store the result
            results[id(current_node)] = result

        # Replace all references with actual results
        for node_id, result in results.items():
            # Replace single node references
            for attr_name, attrs in Serializer.NODE_ATTRIBUTES.items():
                for single_attr in attrs['single_nodes']:
                    if single_attr in result and isinstance(result[single_attr], str) and result[single_attr].startswith("__NODE_REF__"):
                        ref_id = int(result[single_attr].replace("__NODE_REF__", ""))
                        if ref_id in results:
                            result[single_attr] = results[ref_id]

            # Replace node list references
            for attr_name, attrs in Serializer.NODE_ATTRIBUTES.items():
                for list_attr in attrs['node_lists']:
                    if list_attr in result and isinstance(result[list_attr], list):
                        for i, item in enumerate(result[list_attr]):
                            if isinstance(item, str) and item.startswith("__NODE_REF__"):
                                ref_id = int(item.replace("__NODE_REF__", ""))
                                if ref_id in results:
                                    result[list_attr][i] = results[ref_id]

        # Return the root node result
        return results[id(node)]

    @staticmethod
    def _node_from_dict(data: Dict[str, Any]) -> Node:
        """Create node from dictionary using iterative approach."""
        if not isinstance(data, dict):
            return data

        # Use iterative BFS approach with a queue - much faster!
        queue = deque([data])
        results = {}

        while queue:
            current_data = queue.popleft()

            # Create a copy to avoid modifying the original
            data_copy = current_data.copy()

            # Get node type
            node_type = NodeType(data_copy.get("type", "Program"))
            attrs = Serializer.NODE_ATTRIBUTES.get(node_type, {'single_nodes': [], 'node_lists': []})

            # Process single node attributes
            for attr_name in attrs['single_nodes']:
                if attr_name in data_copy and isinstance(data_copy[attr_name], dict):
                    # Add to queue for processing
                    queue.append(data_copy[attr_name])
                    # Store reference - will be replaced later
                    data_copy[attr_name] = f"__NODE_REF__{id(data_copy[attr_name])}"

            # Process node list attributes
            for attr_name in attrs['node_lists']:
                if attr_name in data_copy and isinstance(data_copy[attr_name], list):
                    processed_list = []
                    for item in data_copy[attr_name]:
                        if isinstance(item, dict):
                            # Add to queue for processing
                            queue.append(item)
                            # Store reference - will be replaced later
                            processed_list.append(f"__NODE_REF__{id(item)}")
                        else:
                            processed_list.append(item)
                    data_copy[attr_name] = processed_list

            # Create the node
            results[id(current_data)] = Node.from_dict(data_copy)

        # Replace all references with actual nodes
        for data_id, node in results.items():
            # Replace single node references
            for attr_name, attrs in Serializer.NODE_ATTRIBUTES.items():
                for single_attr in attrs['single_nodes']:
                    if hasattr(node, single_attr):
                        attr_value = getattr(node, single_attr)
                        if isinstance(attr_value, str) and attr_value.startswith("__NODE_REF__"):
                            ref_id = int(attr_value.replace("__NODE_REF__", ""))
                            if ref_id in results:
                                setattr(node, single_attr, results[ref_id])

            # Replace node list references
            for attr_name, attrs in Serializer.NODE_ATTRIBUTES.items():
                for list_attr in attrs['node_lists']:
                    if hasattr(node, list_attr):
                        attr_value = getattr(node, list_attr)
                        if isinstance(attr_value, list):
                            for i, item in enumerate(attr_value):
                                if isinstance(item, str) and item.startswith("__NODE_REF__"):
                                    ref_id = int(item.replace("__NODE_REF__", ""))
                                    if ref_id in results:
                                        attr_value[i] = results[ref_id]

        # Return the root node
        return results[id(data)]

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

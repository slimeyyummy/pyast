"""
Graph visualization for PyAST.

This module provides functionality to export AST trees to DOT and JSON formats
for visualization tools like Graphviz and web viewers.
"""

import json
from typing import Dict, List, Any, Optional
from .nodes import Node, NodeType


class Visualizer:
    """Handles AST visualization and export."""

    def __init__(self):
        self.node_counter = 0
        self.node_map: Dict[int, str] = {}

    def to_dot(self, tree: Node, filename: Optional[str] = None) -> str:
        """Convert AST to DOT format for Graphviz."""
        dot_lines = ['digraph AST {', '  node [shape=box];', '  edge [arrowhead=none];']

        self.node_counter = 0
        self.node_map.clear()

        self._build_dot(tree, dot_lines, None)

        dot_lines.append('}')

        dot_content = '\n'.join(dot_lines)

        if filename:
            with open(filename, 'w') as f:
                f.write(dot_content)

        return dot_content

    def _build_dot(self, node: Node, dot_lines: List[str], parent_id: Optional[str]):
        """Recursively build DOT representation."""
        node_id = self._get_node_id(node)

        # Node label
        label = self._get_node_label(node)
        dot_lines.append(f'  {node_id} [label="{label}"];')

        # Edge from parent
        if parent_id:
            dot_lines.append(f'  {parent_id} -> {node_id};')

        # Child nodes
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    self._build_dot(child, dot_lines, node_id)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            self._build_dot(node.value, dot_lines, node_id)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            self._build_dot(node.left, dot_lines, node_id)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            self._build_dot(node.right, dot_lines, node_id)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            self._build_dot(node.func, dot_lines, node_id)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            self._build_dot(node.test, dot_lines, node_id)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            self._build_dot(node.target, dot_lines, node_id)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            self._build_dot(node.iter, dot_lines, node_id)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    self._build_dot(target, dot_lines, node_id)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    self._build_dot(arg, dot_lines, node_id)

    def _get_node_id(self, node: Node) -> str:
        """Get unique ID for a node."""
        node_hash = hash((id(node), type(node).__name__))
        if node_hash not in self.node_map:
            self.node_counter += 1
            self.node_map[node_hash] = f"n{self.node_counter}"
        return self.node_map[node_hash]

    def _get_node_label(self, node: Node) -> str:
        """Get label for a node."""
        label = f"{node.node_type.value}"

        if hasattr(node, 'name') and node.name:
            label += f"\\n{node.name}"
        elif hasattr(node, 'id') and node.id:
            label += f"\\n{node.id}"
        elif hasattr(node, 'value'):
            if node.value is not None:
                val_str = str(node.value)
                if len(val_str) > 20:
                    val_str = val_str[:17] + "..."
                label += f"\\n{val_str}"
        elif hasattr(node, 'op') and node.op:
            label += f"\\n{node.op}"

        return label.replace('"', '\\"')

    def to_json_graph(self, tree: Node, filename: Optional[str] = None) -> Dict[str, Any]:
        """Convert AST to JSON graph format."""
        self.node_counter = 0
        self.node_map.clear()

        nodes = []
        edges = []

        self._build_json_graph(tree, nodes, edges, None)

        graph = {
            "nodes": nodes,
            "edges": edges
        }

        if filename:
            with open(filename, 'w') as f:
                json.dump(graph, f, indent=2)

        return graph

    def _build_json_graph(self, node: Node, nodes: List[Dict], edges: List[Dict], parent_id: Optional[str]):
        """Recursively build JSON graph representation."""
        node_id = self._get_node_id(node)

        # Add node
        node_info = {
            "id": node_id,
            "type": node.node_type.value,
            "label": self._get_node_label(node)
        }

        if hasattr(node, 'position') and node.position:
            node_info["position"] = {
                "line": node.position.line,
                "column": node.position.column
            }

        nodes.append(node_info)

        # Add edge from parent
        if parent_id:
            edges.append({
                "source": parent_id,
                "target": node_id
            })

        # Child nodes
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    self._build_json_graph(child, nodes, edges, node_id)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            self._build_json_graph(node.value, nodes, edges, node_id)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            self._build_json_graph(node.left, nodes, edges, node_id)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            self._build_json_graph(node.right, nodes, edges, node_id)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            self._build_json_graph(node.func, nodes, edges, node_id)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            self._build_json_graph(node.test, nodes, edges, node_id)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            self._build_json_graph(node.target, nodes, edges, node_id)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            self._build_json_graph(node.iter, nodes, edges, node_id)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    self._build_json_graph(target, nodes, edges, node_id)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    self._build_json_graph(arg, nodes, edges, node_id)

    def export_graphml(self, tree: Node, filename: str):
        """Export AST to GraphML format."""
        # This is a simplified GraphML export
        graphml = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="AST" edgedefault="directed">
'''

        self.node_counter = 0
        self.node_map.clear()

        nodes_xml, edges_xml = self._build_graphml(tree)

        graphml += nodes_xml
        graphml += edges_xml
        graphml += '  </graph>\n</graphml>'

        with open(filename, 'w') as f:
            f.write(graphml)

    def _build_graphml(self, tree: Node) -> tuple[str, str]:
        """Build GraphML representation."""
        nodes_xml = ""
        edges_xml = ""

        node_id = self._get_node_id(tree)
        label = self._get_node_label(tree).replace('"', '&quot;')

        nodes_xml += f'    <node id="{node_id}">\n'
        nodes_xml += f'      <data key="label">{label}</data>\n'
        nodes_xml += f'      <data key="type">{tree.node_type.value}</data>\n'
        nodes_xml += '    </node>\n'

        # Add edges and recurse
        if hasattr(tree, 'body') and isinstance(tree.body, list):
            for child in tree.body:
                if isinstance(child, Node):
                    child_id = self._get_node_id(child)
                    edges_xml += f'    <edge source="{node_id}" target="{child_id}"/>\n'
                    child_nodes, child_edges = self._build_graphml(child)
                    nodes_xml += child_nodes
                    edges_xml += child_edges

        if hasattr(tree, 'value') and isinstance(tree.value, Node):
            child_id = self._get_node_id(tree.value)
            edges_xml += f'    <edge source="{node_id}" target="{child_id}"/>\n'
            child_nodes, child_edges = self._build_graphml(tree.value)
            nodes_xml += child_nodes
            edges_xml += child_edges

        return nodes_xml, edges_xml

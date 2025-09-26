"""
Graph visualization for PyAST.

This module provides comprehensive AST visualization with interactive web-based graphs,
syntax highlighting, symbol table integration, and advanced analysis features.
"""

import json
import os
import webbrowser
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict

# Add current directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(__file__))

from nodes import Node, NodeType, Position
from symbols import SymbolTable, Symbol


class Visualizer:
    """Enhanced AST visualization with interactive features."""

    def __init__(self):
        self.node_counter = 0
        self.node_map: Dict[int, str] = {}
        self.control_flow_edges: List[Dict] = []
        self.graph_metrics: Dict[str, Any] = {}

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
        """Recursively build DOT representation with enhanced styling."""
        node_id = self._get_node_id(node)

        # Enhanced node styling based on type
        shape, color, style = self._get_node_style(node)

        # Node label with enhanced information
        label = self._get_enhanced_node_label(node)
        dot_lines.append(f'  {node_id} [label="{label}" shape={shape} color="{color}" style="{style}"];')

        # Edge from parent
        if parent_id:
            dot_lines.append(f'  {parent_id} -> {node_id};')

        # Child nodes with enhanced traversal
        self._build_child_connections(node, dot_lines, node_id)

    def _get_node_style(self, node: Node) -> Tuple[str, str, str]:
        """Get styling information based on node type."""
        node_type = node.node_type.value

        # Define styles for different node types
        styles = {
            'FunctionDef': ('box', 'blue', 'filled'),
            'ClassDef': ('diamond', 'purple', 'filled'),
            'Assign': ('box', 'green', 'filled'),
            'BinOp': ('ellipse', 'orange', 'filled'),
            'Name': ('circle', 'red', 'filled'),
            'Constant': ('plaintext', 'black', 'filled'),
            'Call': ('box', 'cyan', 'filled'),
            'If': ('diamond', 'yellow', 'filled'),
            'For': ('box', 'magenta', 'filled'),
            'While': ('box', 'pink', 'filled'),
            'Return': ('triangle', 'red', 'filled'),
            'Break': ('invtriangle', 'darkred', 'filled'),
            'Continue': ('invtriangle', 'darkorange', 'filled'),
            'Import': ('parallelogram', 'brown', 'filled'),
            'Try': ('box', 'darkgreen', 'filled'),
        }

        return styles.get(node_type, ('box', 'black', 'filled'))

    def _get_enhanced_node_label(self, node: Node) -> str:
        """Get enhanced label with metadata."""
        label = f"{node.node_type.value}"

        # Add position information if available
        if hasattr(node, 'position') and node.position:
            label += f"\\nLine {node.position.line}"

        # Add specific information based on node type
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

    def _build_child_connections(self, node: Node, dot_lines: List[str], node_id: str):
        """Build connections to child nodes with enhanced traversal."""
        # Define all possible child attributes
        child_attrs = [
            ('body', list), ('value', Node), ('left', Node), ('right', Node),
            ('func', Node), ('test', Node), ('target', Node), ('iter', Node),
            ('orelse', list), ('handlers', list), ('finalbody', list),
            ('args', list), ('bases', list), ('decorator_list', list),
            ('exc', Node), ('cause', Node), ('msg', Node), ('type', Node),
            ('generators', list), ('elt', Node), ('key', Node)
        ]

        for attr_name, expected_type in child_attrs:
            if hasattr(node, attr_name):
                value = getattr(node, attr_name)
                if isinstance(value, expected_type):
                    if expected_type == list:
                        for child in value:
                            if isinstance(child, Node):
                                self._build_dot(child, dot_lines, node_id)
                    else:
                        self._build_dot(value, dot_lines, node_id)

    def _get_node_id(self, node: Node) -> str:
        """Get unique ID for a node."""
        node_hash = hash((id(node), type(node).__name__))
        if node_hash not in self.node_map:
            self.node_counter += 1
            self.node_map[node_hash] = f"n{self.node_counter}"
        return self.node_map[node_hash]

    def to_interactive_html(self, tree: Node, symbol_table: Optional[SymbolTable] = None,
                           filename: Optional[str] = None) -> str:
        """Create interactive HTML visualization with D3.js."""
        self.node_counter = 0
        self.node_map.clear()
        self.control_flow_edges.clear()

        # Calculate graph metrics FIRST
        self.graph_metrics = self._calculate_metrics(tree)

        # Build graph data
        graph_data = self._build_interactive_graph(tree, symbol_table)

        # Generate HTML
        html_content = self._generate_html(graph_data, symbol_table)

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            # Optionally open in browser
            if filename.endswith('.html'):
                webbrowser.open(f'file://{os.path.abspath(filename)}')

        return html_content

    def _build_interactive_graph(self, tree: Node, symbol_table: Optional[SymbolTable]) -> Dict[str, Any]:
        """Build interactive graph data structure."""
        nodes = []
        edges = []
        self._build_interactive_nodes(tree, nodes, edges, None, symbol_table, 0)
        return {"nodes": nodes, "edges": edges, "metrics": self.graph_metrics}

    def _build_interactive_nodes(self, node: Node, nodes: List[Dict], edges: List[Dict],
                                parent_id: Optional[str], symbol_table: Optional[SymbolTable], depth: int):
        """Build interactive node representation."""
        node_id = self._get_node_id(node)

        # Enhanced node data
        node_data = {
            "id": node_id,
            "type": node.node_type.value,
            "label": self._get_enhanced_node_label(node),
            "depth": depth,
            "style": self._get_node_style(node),
            "metadata": self._get_node_metadata(node, symbol_table),
            "position": None
        }

        # Add position information
        if hasattr(node, 'position') and node.position:
            node_data["position"] = {
                "line": node.position.line,
                "column": node.position.column
            }

        nodes.append(node_data)

        # Add edge from parent
        if parent_id:
            edges.append({
                "source": parent_id,
                "target": node_id,
                "type": "structural"
            })

        # Build child connections
        self._build_interactive_child_connections(node, nodes, edges, node_id, symbol_table, depth)

    def _build_interactive_child_connections(self, node: Node, nodes: List[Dict], edges: List[Dict],
                                           node_id: str, symbol_table: Optional[SymbolTable], depth: int):
        """Build connections to child nodes for interactive visualization."""
        # Define all possible child attributes
        child_attrs = [
            ('body', list), ('value', Node), ('left', Node), ('right', Node),
            ('func', Node), ('test', Node), ('target', Node), ('iter', Node),
            ('orelse', list), ('handlers', list), ('finalbody', list),
            ('args', list), ('bases', list), ('decorator_list', list),
            ('exc', Node), ('cause', Node), ('msg', Node), ('type', Node),
            ('generators', list), ('elt', Node), ('key', Node)
        ]

        for attr_name, expected_type in child_attrs:
            if hasattr(node, attr_name):
                value = getattr(node, attr_name)
                if isinstance(value, expected_type):
                    if expected_type == list:
                        for child in value:
                            if isinstance(child, Node):
                                self._build_interactive_nodes(child, nodes, edges, node_id, symbol_table, depth)
                    else:
                        self._build_interactive_nodes(value, nodes, edges, node_id, symbol_table, depth)

    def _get_node_metadata(self, node: Node, symbol_table: Optional[SymbolTable]) -> Dict[str, Any]:
        """Get comprehensive metadata for a node."""
        metadata = {
            "node_type": node.node_type.value,
            "attributes": {}
        }

        # Add position info
        if hasattr(node, 'position') and node.position:
            metadata["position"] = {
                "line": node.position.line,
                "column": node.position.column
            }

        # Add symbol information if available
        if symbol_table:
            # Try to find symbol information for this node
            if hasattr(node, 'name') and node.name:
                symbol = symbol_table.current_scope.get_symbol(node.name)
                if symbol:
                    metadata["symbol"] = {
                        "type": symbol.node_type,
                        "is_used": symbol.is_used(),
                        "is_assigned": symbol.is_assigned(),
                        "type_info": str(symbol.type_info) if symbol.type_info else None
                    }

        # Add specific attributes
        for attr in ['name', 'id', 'value', 'op', 'args', 'body', 'orelse']:
            if hasattr(node, attr):
                value = getattr(node, attr)
                if value is not None and not callable(value):
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        metadata["attributes"][attr] = value
                    elif isinstance(value, list):
                        metadata["attributes"][attr] = f"list[{len(value)}]"

        return metadata

    def _calculate_metrics(self, tree: Node) -> Dict[str, Any]:
        """Calculate graph metrics."""
        metrics = {
            "total_nodes": 0,
            "max_depth": 0,
            "node_types": defaultdict(int),
            "branching_factors": []
        }

        def traverse(node: Node, depth: int):
            metrics["total_nodes"] += 1
            metrics["max_depth"] = max(metrics["max_depth"], depth)
            metrics["node_types"][node.node_type.value] += 1

            child_count = 0

            # Count children using simple traversal
            if hasattr(node, 'body') and isinstance(node.body, list):
                child_count += len([c for c in node.body if isinstance(c, Node)])
            if hasattr(node, 'value') and isinstance(node.value, Node):
                child_count += 1
            if hasattr(node, 'left') and isinstance(node.left, Node):
                child_count += 1
            if hasattr(node, 'right') and isinstance(node.right, Node):
                child_count += 1
            if hasattr(node, 'func') and isinstance(node.func, Node):
                child_count += 1
            if hasattr(node, 'test') and isinstance(node.test, Node):
                child_count += 1
            if hasattr(node, 'target') and isinstance(node.target, Node):
                child_count += 1
            if hasattr(node, 'iter') and isinstance(node.iter, Node):
                child_count += 1

            if child_count > 1:
                metrics["branching_factors"].append(child_count)

            # Recurse on children
            if hasattr(node, 'body') and isinstance(node.body, list):
                for child in node.body:
                    if isinstance(child, Node):
                        traverse(child, depth + 1)

            for attr in ['value', 'left', 'right', 'func', 'test', 'target', 'iter']:
                if hasattr(node, attr):
                    value = getattr(node, attr)
                    if isinstance(value, Node):
                        traverse(value, depth + 1)

        traverse(tree, 0)

        # Calculate averages
        avg_branching = sum(metrics["branching_factors"]) / len(metrics["branching_factors"]) if metrics["branching_factors"] else 0

        return {
            **metrics,
            "avg_branching_factor": avg_branching,
            "complexity_score": metrics["total_nodes"] * metrics["max_depth"] * avg_branching
        }

    def _generate_html(self, graph_data: Dict[str, Any], symbol_table: Optional[SymbolTable]) -> str:
        """Generate enhanced interactive HTML with improved D3.js."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyAST Interactive Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            overflow: hidden;
        }

        #container {
            width: 100vw;
            height: 100vh;
            position: relative;
            display: flex;
        }

        #sidebar {
            width: 300px;
            background: #2c3e50;
            color: white;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }

        #main-content {
            flex: 1;
            position: relative;
        }

        #graph-container {
            width: 100%;
            height: 100%;
            background: white;
        }

        #controls {
            background: #34495e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        #controls h4 {
            margin-bottom: 10px;
            color: #ecf0f1;
        }

        .control-group {
            margin-bottom: 10px;
        }

        .control-group label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            color: #bdc3c7;
        }

        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 5px;
            margin-bottom: 5px;
            font-size: 12px;
            transition: background 0.3s;
        }

        button:hover {
            background: #2980b9;
        }

        button.danger {
            background: #e74c3c;
        }

        button.danger:hover {
            background: #c0392b;
        }

        select, input {
            width: 100%;
            padding: 6px;
            border: 1px solid #7f8c8d;
            border-radius: 4px;
            background: white;
            color: #2c3e50;
        }

        #metrics {
            background: #34495e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        #metrics h4 {
            margin-bottom: 10px;
            color: #ecf0f1;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
        }

        .metric-label {
            color: #bdc3c7;
        }

        .metric-value {
            color: #f39c12;
            font-weight: bold;
        }

        #node-info {
            background: #34495e;
            padding: 15px;
            border-radius: 8px;
            min-height: 200px;
        }

        #node-info h4 {
            margin-bottom: 10px;
            color: #ecf0f1;
        }

        #node-details {
            background: #ecf0f1;
            color: #2c3e50;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 11px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }

        .node {
            cursor: pointer;
            transition: all 0.3s;
        }

        .node:hover {
            transform-origin: center;
        }

        .node.function { fill: #3498db; stroke: #2980b9; }
        .node.class { fill: #9b59b6; stroke: #8e44ad; }
        .node.variable { fill: #2ecc71; stroke: #27ae60; }
        .node.expression { fill: #f39c12; stroke: #e67e22; }
        .node.statement { fill: #e74c3c; stroke: #c0392b; }
        .node.literal { fill: #95a5a6; stroke: #7f8c8d; }

        .edge {
            stroke: #7f8c8d;
            stroke-width: 2px;
            fill: none;
            transition: stroke 0.3s;
        }

        .edge.control-flow {
            stroke: #e74c3c;
            stroke-width: 3px;
            stroke-dasharray: 8,4;
        }

        .edge.highlighted {
            stroke: #f39c12;
            stroke-width: 4px;
        }

        .node.highlighted {
            stroke: #f39c12;
            stroke-width: 4px;
        }

        .node.selected {
            stroke: #e74c3c;
            stroke-width: 6px;
        }

        .node.unused {
            stroke: #e74c3c;
            stroke-width: 3px;
            stroke-dasharray: 5,5;
        }

        .node.undefined {
            stroke: #f39c12;
            stroke-width: 3px;
            stroke-dasharray: 3,3;
        }

        #legend {
            background: #34495e;
            padding: 15px;
            border-radius: 8px;
        }

        #legend h4 {
            margin-bottom: 10px;
            color: #ecf0f1;
        }

        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            font-size: 11px;
        }

        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
            border: 2px solid #ecf0f1;
        }

        .legend-label {
            color: #bdc3c7;
        }

        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 18px;
            color: #7f8c8d;
        }

        .tooltip {
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 300px;
        }

        .search-highlight {
            fill: #f39c12 !important;
            stroke: #e67e22 !important;
        }

        /* Text styling for better readability */
        text {
            fill: white !important;
            stroke: #333 !important;
            stroke-width: 0.5px !important;
            paint-order: stroke fill !important;
        }

        /* Ensure no yellow fill on text */
        .node text {
            fill: white !important;
            stroke: #333 !important;
            stroke-width: 0.5px !important;
        }
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <div id="controls">
                <h4>🎛️ Controls</h4>

                <div class="control-group">
                    <button onclick="collapseAll()">Collapse All</button>
                    <button onclick="expandAll()">Expand All</button>
                    <button onclick="resetView()">Reset View</button>
                </div>

                <div class="control-group">
                    <label for="nodeTypeFilter">Filter by Type:</label>
                    <select id="nodeTypeFilter" onchange="filterByType(this.value)">
                        <option value="">All Types</option>
                        <option value="FunctionDef">Functions</option>
                        <option value="ClassDef">Classes</option>
                        <option value="Assign">Assignments</option>
                        <option value="Name">Variables</option>
                        <option value="BinOp">Expressions</option>
                        <option value="Constant">Constants</option>
                        <option value="Call">Function Calls</option>
                    </select>
                </div>

                <div class="control-group">
                    <label for="searchInput">Search Nodes:</label>
                    <input type="text" id="searchInput" placeholder="Search..." onkeyup="searchNodes(this.value)">
                </div>

                <div class="control-group">
                    <button onclick="highlightUnusedVariables()">Highlight Unused</button>
                    <button onclick="highlightUndefinedVariables()">Highlight Undefined</button>
                    <button onclick="clearHighlights()">Clear Highlights</button>
                </div>

                <div class="control-group">
                    <button onclick="exportSVG()">Export SVG</button>
                    <button onclick="exportPNG()">Export PNG</button>
                </div>
            </div>

            <div id="metrics">
                <h4>📊 Graph Metrics</h4>
                <div class="metric">
                    <span class="metric-label">Total Nodes:</span>
                    <span class="metric-value" id="totalNodes">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Max Depth:</span>
                    <span class="metric-value" id="maxDepth">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Branching:</span>
                    <span class="metric-value" id="avgBranching">0.00</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Complexity Score:</span>
                    <span class="metric-value" id="complexity">0</span>
                </div>
            </div>

            <div id="node-info">
                <h4>🔍 Node Details</h4>
                <div id="node-details">Click on a node to see details...</div>
            </div>

            <div id="legend">
                <h4>🎨 Legend</h4>
                <div class="legend-item">
                    <div class="legend-color" style="background: #3498db;"></div>
                    <span class="legend-label">Functions</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #9b59b6;"></div>
                    <span class="legend-label">Classes</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #2ecc71;"></div>
                    <span class="legend-label">Variables</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #f39c12;"></div>
                    <span class="legend-label">Expressions</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #e74c3c;"></div>
                    <span class="legend-label">Statements</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #95a5a6;"></div>
                    <span class="legend-label">Constants</span>
                </div>
            </div>
        </div>

        <div id="main-content">
            <div id="graph-container">
                <div id="loading">Loading visualization...</div>
                <svg id="graph"></svg>
            </div>
        </div>
    </div>

    <div id="tooltip" class="tooltip" style="display: none;"></div>

    <script type="application/json" id="graphData">
""" + json.dumps(graph_data, indent=2) + """
    </script>

    <script>
        // Global variables
        let simulation;
        let tooltip;
        let selectedNode = null;
        let highlightedNodes = new Set();

        // Simple and robust initialization
        document.addEventListener('DOMContentLoaded', function() {
            try {
                // Hide loading immediately
                document.getElementById('loading').style.display = 'none';

                // Get graph data
                const graphDataElement = document.getElementById('graphData');
                if (!graphDataElement) {
                    throw new Error('Graph data element not found');
                }

                const graphData = JSON.parse(graphDataElement.textContent);
                if (!graphData || !graphData.nodes || !graphData.edges) {
                    throw new Error('Invalid graph data structure');
                }

                // Initialize visualization immediately
                initializeVisualization(graphData);

            } catch (error) {
                console.error('Initialization error:', error);
                document.getElementById('loading').innerHTML =
                    '<div style="color: red; text-align: center;">Error: ' + error.message + '</div>';
                document.getElementById('loading').style.display = 'block';
            }
        });

        function initializeVisualization(graphData) {
            console.log('Initializing visualization with', graphData.nodes.length, 'nodes');

            // Get DOM elements
            const svg = d3.select("#graph");
            const width = window.innerWidth - 320;
            const height = window.innerHeight;

            svg.attr("width", width).attr("height", height);

            // Create tooltip
            tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);

            // Create zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", (event) => {
                    g.attr("transform", event.transform);
                });

            svg.call(zoom);
            const g = svg.append("g");

            // Update metrics
            updateMetrics(graphData);

            // Create edges first
            const edges = g.selectAll(".edge")
                .data(graphData.edges)
                .enter().append("line")
                .attr("class", "edge")
                .style("stroke", "#7f8c8d")
                .style("stroke-width", "2");

            // Create nodes
            const nodes = g.selectAll(".node")
                .data(graphData.nodes)
                .enter().append("g")
                .attr("class", d => {
                    // Map node types to CSS classes for proper coloring
                    const typeMap = {
                        'FunctionDef': 'function',
                        'ClassDef': 'class',
                        'Assign': 'variable',
                        'Name': 'variable',
                        'Constant': 'literal',
                        'BinOp': 'expression',
                        'Compare': 'expression',
                        'Call': 'expression',
                        'If': 'statement',
                        'For': 'statement',
                        'While': 'statement',
                        'Try': 'statement',
                        'Import': 'statement',
                        'ImportFrom': 'statement',
                        'Return': 'statement',
                        'Expr': 'statement',
                        'Program': 'statement'
                    };
                    const cssClass = typeMap[d.type] || d.type.toLowerCase();
                    return `node ${cssClass}`;
                })
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended))
                .on("click", nodeClicked)
                .on("mouseover", nodeMouseOver)
                .on("mouseout", nodeMouseOut);

            // Add circles
            nodes.append("circle")
                .attr("r", 25)
                .attr("cx", 0)
                .attr("cy", 0);

            // Add labels
            nodes.append("text")
                .text(d => d.label)
                .attr("text-anchor", "middle")
                .attr("dy", "0.35em")
                .style("font-size", "12px")
                .style("fill", "white")
                .style("stroke", "#333")
                .style("stroke-width", "0.5px")
                .style("font-weight", "bold")
                .style("paint-order", "stroke fill");

            // Force simulation
            simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .on("tick", ticked);

            function ticked() {
                nodes.attr("transform", d => `translate(${d.x},${d.y})`);
                edges.attr("x1", d => d.source.x)
                     .attr("y1", d => d.source.y)
                     .attr("x2", d => d.target.x)
                     .attr("y2", d => d.target.y);
            }

            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }

            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }

            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }

            function nodeClicked(event, d) {
                updateNodeDetails(d);
            }

            function nodeMouseOver(event, d) {
                d3.select(event.currentTarget).style("stroke", "#f39c12").style("stroke-width", "4");
            }

            function nodeMouseOut(event, d) {
                d3.select(event.currentTarget).style("stroke", "#333").style("stroke-width", "2");
            }

            function updateNodeDetails(node) {
                const detailsDiv = document.getElementById("node-details");
                detailsDiv.innerHTML = `<strong>${node.type}</strong><br>${node.label}`;
            }

            function updateMetrics(graphData) {
                const totalNodes = graphData.metrics?.total_nodes || 0;
                const maxDepth = graphData.metrics?.max_depth || 0;
                const avgBranching = graphData.metrics?.avg_branching_factor || 0;
                const complexity = graphData.metrics?.complexity_score || 0;

                document.getElementById("totalNodes").textContent = totalNodes;
                document.getElementById("maxDepth").textContent = maxDepth;
                document.getElementById("avgBranching").textContent = avgBranching.toFixed(2);
                document.getElementById("complexity").textContent = Math.round(complexity);
            }

            // Working controls
            window.collapseAll = function() {
                nodes.transition().duration(300).style("opacity", 0.3);
                edges.transition().duration(300).style("opacity", 0.1);
            };

            window.expandAll = function() {
                nodes.transition().duration(300).style("opacity", 1);
                edges.transition().duration(300).style("opacity", 0.6);
            };

            window.resetView = function() {
                svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
                simulation.alpha(1).restart();
            };

            window.filterByType = function(type) {
                if (type === "") {
                    nodes.style("opacity", 1);
                    edges.style("opacity", 0.6);
                } else {
                    nodes.style("opacity", d => d.type === type ? 1 : 0.1);
                    edges.style("opacity", d => {
                        return (d.source.type === type || d.target.type === type) ? 0.6 : 0.1;
                    });
                }
            };

            window.searchNodes = function(query) {
                if (query.trim() === "") {
                    nodes.style("opacity", 1);
                } else {
                    const regex = new RegExp(query, 'i');
                    nodes.style("opacity", d => regex.test(d.label) || regex.test(d.type) ? 1 : 0.1);
                }
            };

            window.highlightUnusedVariables = function() {
                nodes.classed("unused", false);
                nodes.each(function(d) {
                    if (d.metadata?.symbol?.is_used === false) {
                        d3.select(this).classed("unused", true);
                    }
                });
            };

            window.highlightUndefinedVariables = function() {
                nodes.classed("undefined", false);
                nodes.each(function(d) {
                    if (d.metadata?.symbol?.is_assigned === false) {
                        d3.select(this).classed("undefined", true);
                    }
                });
            };

            window.clearHighlights = function() {
                d3.selectAll(".node").classed("unused undefined", false);
                d3.selectAll(".node, .edge").style("opacity", 1);
            };

            console.log('✅ Visualization initialized successfully!');
        }

        // Handle keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            switch(e.key) {
                case 'Escape':
                    clearHighlights();
                    break;
                case 'r':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        resetView();
                    }
                    break;
                case 'f':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        document.getElementById('searchInput').focus();
                    }
                    break;
            }
        });
    </script>
</body>
</html>
        """

        return html_template

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

        with open(filename, 'w', encoding='utf-8') as f:
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

    def visualize_with_symbol_table(self, tree: Node, symbol_table: SymbolTable,
                                   filename: Optional[str] = None) -> str:
        """Create enhanced visualization with symbol table integration."""
        return self.to_interactive_html(tree, symbol_table, filename)

    def compare_asts(self, tree1: Node, tree2: Node, filename: str):
        """Compare two ASTs and highlight differences."""
        # This is a placeholder for diff functionality
        diff_html = f"""
        <html>
        <head><title>AST Comparison</title></head>
        <body>
        <h1>AST Comparison</h1>
        <p>Comparing two ASTs - detailed diff visualization would go here.</p>
        <p>AST 1 nodes: {self._count_nodes(tree1)}</p>
        <p>AST 2 nodes: {self._count_nodes(tree2)}</p>
        </body>
        </html>
        """

        with open(filename, 'w') as f:
            f.write(diff_html)

    def _count_nodes(self, tree: Node) -> int:
        """Count total nodes in AST."""
        count = 1  # Count current node

        # Count children
        if hasattr(tree, 'body') and isinstance(tree.body, list):
            for child in tree.body:
                if isinstance(child, Node):
                    count += self._count_nodes(child)

        for attr in ['value', 'left', 'right', 'func', 'test', 'target', 'iter']:
            if hasattr(tree, attr):
                value = getattr(tree, attr)
                if isinstance(value, Node):
                    count += self._count_nodes(value)

        return count

    def get_graph_metrics(self, tree: Node) -> Dict[str, Any]:
        """Get comprehensive graph metrics."""
        return self._calculate_metrics(tree)

    def filter_nodes_by_type(self, tree: Node, node_type: str) -> List[Node]:
        """Filter nodes by type."""
        filtered = []

        def collect_nodes(node: Node):
            if node.node_type.value == node_type:
                filtered.append(node)

            # Recurse on children
            if hasattr(node, 'body') and isinstance(node.body, list):
                for child in node.body:
                    if isinstance(child, Node):
                        collect_nodes(child)

            for attr in ['value', 'left', 'right', 'func', 'test', 'target', 'iter']:
                if hasattr(node, attr):
                    value = getattr(node, attr)
                    if isinstance(value, Node):
                        collect_nodes(value)

        collect_nodes(tree)
        return filtered

    def collapse_node_subtree(self, tree: Node, node_id: str) -> Dict[str, Any]:
        """Collapse a subtree for better visualization."""
        # This would create a collapsed representation
        return {
            "id": node_id,
            "type": "collapsed",
            "label": f"{tree.node_type.value} (+{self._count_nodes(tree) - 1} nodes)",
            "collapsed": True,
            "original_nodes": self._count_nodes(tree)
        }

    def export_to_json(self, tree: Node, symbol_table: Optional[SymbolTable] = None,
                      filename: Optional[str] = None) -> Dict[str, Any]:
        """Export comprehensive AST data to JSON."""
        self.node_counter = 0
        self.node_map.clear()

        data = {
            "graph": self._build_interactive_graph(tree, symbol_table),
            "metrics": self._calculate_metrics(tree),
            "metadata": {
                "export_time": "2024-01-01T00:00:00Z",  # Would use actual time
                "node_types": list(set(node.node_type.value for node in self._get_all_nodes(tree))),
                "symbol_analysis": symbol_table is not None
            }
        }

        if filename:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

        return data

    def _get_all_nodes(self, tree: Node) -> List[Node]:
        """Get all nodes in the AST."""
        nodes = [tree]

        if hasattr(tree, 'body') and isinstance(tree.body, list):
            for child in tree.body:
                if isinstance(child, Node):
                    nodes.extend(self._get_all_nodes(child))

        for attr in ['value', 'left', 'right', 'func', 'test', 'target', 'iter']:
            if hasattr(tree, attr):
                value = getattr(tree, attr)
                if isinstance(value, Node):
                    nodes.extend(self._get_all_nodes(value))

        return nodes

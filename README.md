# PyAST

**A comprehensive Python AST implementation with advanced features for code analysis, transformation, and visualization.**

PyAST provides a simple, extensible AST (Abstract Syntax Tree) implementation for Python code analysis and transformation. It includes features like round-trip parsing, pattern matching, transformation pipelines, symbol table management, and interactive web-based visualization.

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Components](#-core-components)
- [Detailed Usage](#-detailed-usage)
- [Advanced Features](#-advanced-features)
- [Examples](#-examples)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [License](#-license)

## 🚀 Installation

### Option 1: Install from Source

```bash
git https://github.com/slimeyyummy/pyast-extended
pip install -e .
```

### Requirements

- Python 3.7+
- Required packages: `ast`, `json`, `typing`, `dataclasses`

## 🎯 Quick Start

Here's a simple example to get you started:

```python
from pyast import Parser, Visualization

# Parse Python code
parser = Parser()
code = """
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
"""
tree = parser.parse(code)

# Create interactive visualization
visualizer = Visualization()
html_content = visualizer.to_interactive_html(tree, filename="my_ast.html")
```

Open `my_ast.html` in your browser to see the interactive AST visualization!

## 🏗️ Core Components

### Parser
Parses Python source code into AST trees.

```python
from pyast import Parser

parser = Parser()
tree = parser.parse("x = 1 + 2")
print(f"Parsed {len(tree.body)} statements")
```

### Nodes
Core AST node classes representing different Python constructs.

```python
from pyast import Nodes, NodeType

# Create a function definition node
func_node = Nodes.FunctionDef(
    name="my_function",
    args=["param1", "param2"],
    body=[
        Nodes.Assign(
            targets=[Nodes.Name(id="result")],
            value=Nodes.BinOp(
                left=Nodes.Name(id="param1"),
                op="+",
                right=Nodes.Name(id="param2")
            )
        ),
        Nodes.Return(value=Nodes.Name(id="result"))
    ]
)
```

### Matcher
Pattern matching system for finding specific code patterns.

```python
from pyast import Matcher

matcher = Matcher()
tree = parser.parse("print('hello')")

# Find all function calls
calls = matcher.find_calls(tree, "print")

# Find all assignments
assignments = matcher.find_assignments(tree)

# Custom pattern matching
pattern = matcher.query_by_string(tree, "call print")
```

### Symbols
Symbol table management with type inference.

```python
from pyast import Symbols

symbol_table = Symbols()
symbol_table.analyze(tree)

# Get unused variables
unused = symbol_table.get_unused_variables()

# Get symbols by type
functions = symbol_table.get_symbols_by_type("function")
```

### Transformer
Code transformation and optimization pipeline.

```python
from pyast import Transformer

transformer = Transformer()
optimized_tree = transformer.optimize(tree)

# Apply specific transformations
transformer.add_pass(ConstantFoldingPass())
transformed_tree = transformer.transform(tree)
```

### Visualization
Interactive web-based AST visualization.

```python
from pyast import Visualization

visualizer = Visualization()
html = visualizer.to_interactive_html(tree, filename="visualization.html")

# With symbol table integration
html = visualizer.to_interactive_html(tree, symbol_table, filename="enhanced_viz.html")
```

### Serializer
JSON serialization and deserialization.

```python
from pyast import Serializer

# Convert AST to JSON
json_str = Serializer.to_json(tree)

# Load AST from JSON
loaded_tree = Serializer.from_json(json_str)

# Save to file
Serializer.serialize_tree(tree, "ast.json")
loaded_tree = Serializer.deserialize_tree("ast.json")
```

## 📚 Detailed Usage

### Working with AST Nodes

```python
from pyast import Parser, Nodes, NodeType

# Parse code
parser = Parser()
tree = parser.parse("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
""")

# Access node properties
print(f"Root type: {tree.node_type.value}")
print(f"Number of statements: {len(tree.body)}")

# Find function definitions
for node in tree.body:
    if isinstance(node, Nodes.FunctionDef):
        print(f"Found function: {node.name}")
        print(f"Parameters: {node.args}")
        print(f"Number of body statements: {len(node.body)}")
```

### Pattern Matching Tutorial

```python
from pyast import Parser, Matcher

# Parse some code
parser = Parser()
code = """
def calculate_area(width, height):
    return width * height

def calculate_volume(length, width, height):
    area = calculate_area(length, width)
    return area * height

# Usage
a = calculate_area(10, 20)
v = calculate_volume(10, 20, 30)
"""
tree = parser.parse(code)

# Create matcher
matcher = Matcher()

# Find all function definitions
functions = matcher.find_functions(tree)
print(f"Found {len(functions)} functions")

# Find calls to calculate_area
area_calls = matcher.find_calls(tree, "calculate_area")
print(f"Found {len(area_calls)} calls to calculate_area")

# Find assignments
assignments = matcher.find_assignments(tree)
print(f"Found {len(assignments)} assignments")

# Use query language
results = matcher.query_by_string(tree, "call calculate_area")
print(f"Query results: {len(results)} matches")
```

### Symbol Analysis

```python
from pyast import Parser, Symbols

# Parse code with variables
code = """
def greet(name):
    message = f"Hello, {name}!"
    return message

def process_data(data):
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result

# Usage
user_name = "Alice"
greeting = greet(user_name)
numbers = [1, 2, 3, 4, 5]
processed = process_data(numbers)
"""
tree = parser.parse(code)

# Analyze symbols
symbol_table = Symbols()
symbol_table.analyze(tree)

# Print symbol table
symbol_table.print_table()

# Get unused variables
unused = symbol_table.get_unused_variables()
print(f"Unused variables: {[var.name for var in unused]}")

# Get undefined variables
undefined = symbol_table.get_undefined_variables()
print(f"Potentially undefined: {undefined}")
```

### Code Transformation

```python
from pyast import Parser, Transformer

# Parse code with optimization opportunities
code = """
def calculate(x, y):
    temp = x + 1  # This is dead code
    result = y * 2
    return result

def unused_function():
    return "This function is never called"

# Only this is used
final_result = calculate(5, 10)
"""
tree = parser.parse(code)

print("Before transformation:")
print(f"- Total nodes: {len(tree.body)}")

# Apply dead code elimination
transformer = Transformer()
transformer.add_pass(DeadCodeEliminationPass())
transformer.add_pass(UnusedVariableRemovalPass())

optimized_tree = transformer.transform(tree)

print("After transformation:")
print(f"- Total nodes: {len(optimized_tree.body)}")
```

### Interactive Visualization

```python
from pyast import Parser, Symbols, Visualization

# Parse complex code
code = """
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, x, y):
        return x + y

    def multiply(self, x, y):
        return x * y

def main():
    calc = Calculator()
    a = calc.add(5, 3)
    b = calc.multiply(a, 2)
    return b

# Usage
result = main()
"""
tree = parser.parse(code)

# Create symbol table
symbol_table = Symbols()
symbol_table.analyze(tree)

# Create enhanced visualization
visualizer = Visualization()

# Generate HTML with symbol information
html_content = visualizer.to_interactive_html(
    tree,
    symbol_table,
    filename="enhanced_visualization.html"
)

print(f"Generated {len(html_content)} character visualization")

# The HTML file includes:
# - Interactive graph with node details
# - Symbol table information
# - Code metrics and complexity scores
# - Filtering and search capabilities
```

## 🔧 Advanced Features

### Custom Node Types

```python
from pyast import Nodes, NodeType, Plugins

# Create custom node type
class CustomNode(Nodes.Node):
    def __init__(self, custom_field: str = ""):
        super().__init__(NodeType.PROGRAM)
        self.custom_field = custom_field

# Register with plugin system
Plugins.register_node_type("CustomNode", CustomNode)
```

### Custom Transformation Passes

```python
from pyast import TransformPass, Nodes

class CustomOptimizationPass(TransformPass):
    def __init__(self):
        super().__init__("custom_optimization")

    def transform(self, node: Nodes.Node) -> Nodes.Node:
        # Implement custom transformation logic
        if isinstance(node, Nodes.BinOp):
            # Custom binary operation optimization
            if node.op == "*" and self._is_zero(node.right):
                return Nodes.Constant(value=0)

        return node

    def _is_zero(self, node: Nodes.Node) -> bool:
        return isinstance(node, Nodes.Constant) and node.value == 0
```

### Plugin System

```python
from pyast import Plugins

# List available custom nodes
custom_nodes = Plugins.list_custom_nodes()
print(f"Available custom nodes: {custom_nodes}")

# List available passes
custom_passes = Plugins.list_custom_passes()
print(f"Available custom passes: {custom_passes}")

# Register hooks
def my_hook(node):
    print(f"Processing node: {node.node_type.value}")

Plugins.register_hook("before_transform", my_hook)
```

## 💡 Examples

### Example 1: Code Complexity Analysis

```python
from pyast import Parser, Symbols, Visualization

code = """
def complex_function(data):
    if not data:
        return None

    result = []
    for item in data:
        if item > 0:
            processed = item * 2
            if processed > 10:
                result.append(processed)
            else:
                result.append(0)
        else:
            result.append(-1)

    return result
"""

parser = Parser()
tree = parser.parse(code)

# Analyze complexity
symbol_table = Symbols()
symbol_table.analyze(tree)

visualizer = Visualization()
metrics = visualizer._calculate_metrics(tree)

print("Code Complexity Analysis:")
print(f"- Total nodes: {metrics['total_nodes']}")
print(f"- Maximum depth: {metrics['max_depth']}")
print(f"- Average branching factor: {metrics['avg_branching_factor']:.2f}")
print(f"- Complexity score: {metrics['complexity_score']}")
```

### Example 2: Function Call Analysis

```python
from pyast import Parser, Matcher

code = """
import math
from utils import helper

def calculate_stats(data):
    total = sum(data)
    average = total / len(data)
    variance = sum((x - average) ** 2 for x in data) / len(data)
    std_dev = math.sqrt(variance)
    return average, std_dev

def main():
    data = [1, 2, 3, 4, 5]
    avg, std = calculate_stats(data)
    result = helper.process(avg, std)
    return result
"""

parser = Parser()
tree = parser.parse(code)

matcher = Matcher()

# Find all function definitions
functions = matcher.find_functions(tree)
print(f"Found {len(functions)} function definitions")

# Find all function calls
all_calls = matcher.find_calls(tree)
print(f"Found {len(all_calls)} function calls")

# Find specific function calls
math_calls = matcher.find_calls(tree, "sqrt")
import_calls = matcher.find_calls(tree, "sum")
```

### Example 3: Dead Code Elimination

```python
from pyast import Parser, Transformer

code = """
def example_function(x, y):
    temp = x + 1  # This is dead code
    result = y * 2
    return result

def unused_function():
    return "This function is never called"

# Only this is used
final_result = example_function(5, 10)
"""

parser = Parser()
tree = parser.parse(code)

print("Before transformation:")
print(f"- Total nodes: {len(tree.body)}")

# Apply dead code elimination
transformer = Transformer()
transformer.add_pass(DeadCodeEliminationPass())
transformer.add_pass(UnusedVariableRemovalPass())

optimized_tree = transformer.transform(tree)

print("After transformation:")
print(f"- Total nodes: {len(optimized_tree.body)}")
```

## 📚 API Reference

### Parser

- `Parser.parse(code: str) -> Node`: Parse Python code string into AST

### Matcher

- `Matcher.find_functions(tree: Node) -> List[FunctionDef]`: Find all function definitions
- `Matcher.find_calls(tree: Node, func_name: str = None) -> List[Call]`: Find function calls
- `Matcher.find_assignments(tree: Node, var_name: str = None) -> List[Assign]`: Find assignments
- `Matcher.query_by_string(tree: Node, query: str) -> List[Node]`: Query using string patterns

### Symbols

- `SymbolTable.analyze(tree: Node)`: Analyze AST and build symbol table
- `SymbolTable.get_unused_variables() -> List[Symbol]`: Get unused variables
- `SymbolTable.get_undefined_variables() -> List[str]`: Get potentially undefined variables
- `SymbolTable.print_table()`: Print symbol table for debugging

### Transformer

- `Transformer.optimize(tree: Node) -> Node`: Apply common optimizations
- `Transformer.add_pass(pass_instance: TransformPass)`: Add transformation pass
- `Transformer.transform(tree: Node) -> Node`: Apply all registered passes

### Visualization

- `Visualization.to_interactive_html(tree: Node, symbol_table: SymbolTable = None, filename: str = None) -> str`: Generate interactive HTML

### Serializer

- `Serializer.to_json(node: Node) -> str`: Convert AST to JSON string
- `Serializer.from_json(json_str: str) -> Node`: Parse AST from JSON string
- `Serializer.serialize_tree(tree: Node, filename: str)`: Save AST to file
- `Serializer.deserialize_tree(filename: str) -> Node`: Load AST from file

## 🛠️ Troubleshooting

**Issue: Empty visualization**
```
Generated HTML shows no nodes
```
**Solution:**
- Check that your code parses correctly
- Ensure you're using valid Python syntax
- Try with a simpler code example first

**Issue: Pattern matching not working**
```
No matches found for pattern
```
**Solution:**
- Verify the AST structure using visualization
- Check that node types match expected patterns
- Use `print_tree()` to debug AST structure

### Debugging Tips

```python
# Debug AST structure
def print_tree(node, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{node.node_type.value}")
    if hasattr(node, 'body') and isinstance(node.body, list):
        for child in node.body:
            if isinstance(child, Node):
                print_tree(child, indent + 1)

# Use with your tree
print_tree(tree)
```

## ❓ FAQ

**Q: What is an AST?**
A: AST (Abstract Syntax Tree) is a tree representation of the abstract syntactic structure of source code. Each node represents a construct in the code.

**Q: How does PyAST differ from Python's built-in ast module?**
A: PyAST provides additional features like interactive visualization, pattern matching, symbol analysis, and transformation pipelines that aren't available in the standard library.

**Q: Can I extend PyAST with custom node types?**
A: Yes! Use the plugin system to register custom node types and transformation passes.

**Q: Is the visualization interactive?**
A: Yes! The generated HTML includes zoom, pan, filtering, search, and node inspection capabilities.

**Q: How do I analyze code complexity?**
A: Use the metrics calculation feature which provides node count, depth, branching factors, and complexity scores.

**Q: Can I transform and regenerate Python code?**
A: Yes! The transformation pipeline can modify ASTs and the serialization system can convert back to Python code.

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all public functions
- Add docstrings to all classes and methods
- Keep functions small and focused

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


*PyAST v1.2.0 - Comprehensive Python AST Analysis and Transformation*

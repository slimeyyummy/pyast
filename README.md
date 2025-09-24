# PyAST

> A powerful Python AST implementation with advanced features for code analysis and transformation

##  Features

-  **Advanced Parsing** - Robust Python code parsing with error tolerance
-  **Transformation Pipeline** - Extensible system for AST transformations
-  **Pattern Matching** - Powerful query system for AST pattern matching
-  **Serialization** - JSON serialization/deserialization support
-  **Symbol Analysis** - Complete symbol table management
-  **Visualization** - Export AST to DOT, JSON, and GraphML formats
-  **Plugin System** - Extensible architecture for custom passes and nodes
-  **Performance** - Optimized for large codebases

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)
- [Credits](#credits)
- [License](#license)

##  Installation

### From PyPI (Recommended)
```bash
pip install pyast
```

### From Source
```bash
git clone https://github.com/slimeyyummy/pyast
cd pyast
pip install -e .
```

### Development Setup
```bash
git clone https://github.com/slimeyyummy/pyast
cd pyast
pip install -r requirements-dev.txt
```

##  Quick Start

```python
from pyast import Parser, Transformer, Matcher, ConstantFoldingPass

# Parse Python code
parser = Parser()
tree = parser.parse('x = 1 + 2; y = x * 3')

# Apply transformations
transformer = Transformer()
transformer.add_pass(ConstantFoldingPass())
optimized_tree = transformer.transform(tree)

# Pattern matching
matcher = Matcher()
assignments = matcher.find_matches(tree, 'assign x')
```

##  Core Concepts

### AST (Abstract Syntax Tree)
PyAST converts Python source code into a tree structure where each node represents a syntactic construct (functions, variables, expressions, etc.). This tree can be analyzed and modified programmatically.

### Transformation Pipeline
Apply a series of transformations to the AST to optimize, refactor, or analyze code. Each transformation pass can modify the tree structure.

### Pattern Matching
Use query patterns to find specific code patterns in the AST. This is useful for code analysis, refactoring, and static analysis tools.

##  Usage Examples

### Basic AST Operations
```python
from pyast import Parser, print_ast

# Parse and display AST
parser = Parser()
tree = parser.parse('x = 1 + 2 * 3')
print_ast(tree)
```

**Output:**
```
Program
  Assign
    BinOp(+)
      Constant(1)
      BinOp(*)
        Constant(2)
        Constant(3)
    Name(x)
```

### Advanced Pattern Matching
```python
from pyast import Parser, Matcher

# Parse Python code
parser = Parser()
tree = parser.parse('x = 1 + 2; y = x * 3; z = fibonacci(y)')

matcher = Matcher()

# Find all function calls
calls = matcher.find_matches(tree, 'call *')

# Find assignments to specific variables
assignments = matcher.find_matches(tree, 'assign x')

# Find calls to specific functions
fib_calls = matcher.find_matches(tree, 'call fibonacci')

# Complex patterns with regex
import_calls = matcher.find_matches(tree, 'call /import.*/')
```

### AST Transformations
```python
from pyast import Parser, Transformer, ConstantFoldingPass, UnusedVariableRemovalPass

# Parse Python code
parser = Parser()
tree = parser.parse('x = 1 + 2; y = x * 3; z = y + 1')

# Create transformer and apply passes
transformer = Transformer()
transformer.add_pass(ConstantFoldingPass())
transformer.add_pass(UnusedVariableRemovalPass())

# Transform the AST
result = transformer.transform(tree)
print(f'Original: {len(tree.body)} statements')
print(f'Optimized: {len(result.body)} statements')
```

### Complex Code Analysis
```python
from pyast import Parser, Matcher, SymbolTable

# Parse complex code
parser = Parser()
tree = parser.parse('''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

result = factorial(5)
''')

# Analyze symbols
symbol_table = SymbolTable()
symbol_table.analyze(tree)
print(f'Found {len(symbol_table.symbols)} symbols')

# Find all function definitions and calls
matcher = Matcher()
functions = matcher.find_functions(tree)
calls = matcher.find_matches(tree, 'call *')

print(f'Functions: {len(functions)}')
print(f'Function calls: {len(calls)}')
```

### Error Handling
```python
from pyast import Parser

parser = Parser()

# Parse code with syntax errors (error-tolerant)
tree = parser.parse('x = 1 + ; y = 2')  # Invalid syntax

if parser.has_errors():
    print("Parsing errors found:")
    for error in parser.get_errors():
        print(f"  - {error}")
else:
    print("Code parsed successfully")
```

##  Advanced Features

### Custom Transformation Passes
```python
from pyast import TransformPass, Node

class CustomOptimizationPass(TransformPass):
    def __init__(self):
        super().__init__("custom_optimization")

    def transform(self, node: Node) -> Node:
        # Add your custom transformation logic here
        return node

# Use the custom pass
parser = Parser()
tree = parser.parse('x = 1 + 2')
transformer = Transformer()
transformer.add_pass(CustomOptimizationPass())
result = transformer.transform(tree)
```

### Query Language Patterns
PyAST supports a rich query language for pattern matching:

| Pattern | Description | Example |
|---------|-------------|---------|
| `call *` | All function calls | `matcher.find_matches(tree, "call *")` |
| `assign x` | Assignments to variable x | `matcher.find_matches(tree, "assign x")` |
| `call /fib.*/` | Calls matching regex | `matcher.find_matches(tree, "call /fib.*/")` |
| `name /test_/` | Names matching regex | `matcher.find_matches(tree, "name /test_/")` |

### AST Visualization
```python
from pyast import Parser, Visualizer

parser = Parser()
tree = parser.parse('def hello(): return "world"')

visualizer = Visualizer()

# Export to DOT format (Graphviz)
dot_code = visualizer.to_dot(tree, "ast.dot")

# Export to JSON
json_data = visualizer.to_json_graph(tree, "ast.json")

# Export to GraphML
visualizer.export_graphml(tree, "ast.graphml")
```

### Plugin System
```python
from pyast import PluginManager

plugin_manager = PluginManager()

# Register custom node types
plugin_manager.register_node_type("CustomNode", CustomNodeClass)

# Register custom transformation passes
plugin_manager.register_pass("custom_pass", CustomPassClass)

# Register hooks for specific events
def my_hook(node):
    print(f"Processing node: {node.node_type}")

plugin_manager.register_hook("pre_transform", my_hook)
```

## 🔧 API Reference

### Core Classes

#### Parser
Main parser class for converting Python code to AST representation.

```python
parser = Parser(source_code: str = "", filename: str = "<string>")
tree = parser.parse(source_code: Optional[str] = None) -> Program
```

**Key Methods:**
- `parse(source_code)` - Parse source code into AST
- `get_errors()` - Get list of parsing errors
- `has_errors()` - Check if parsing had errors
- `clear_errors()` - Clear error list

#### Transformer
Transformation engine that applies passes in sequence.

```python
transformer = Transformer()
transformer.add_pass(pass_instance: TransformPass)
result = transformer.transform(tree: Node) -> Node
```

**Key Methods:**
- `add_pass(pass)` - Add a transformation pass
- `transform(tree)` - Apply all passes to the tree

#### Matcher
Pattern matching engine for AST queries.

```python
matcher = Matcher()
matches = matcher.find_matches(tree: Node, pattern: Union[str, Pattern]) -> List[Node]
functions = matcher.find_functions(tree: Node) -> List[FunctionDef]
```

**Key Methods:**
- `find_matches(tree, pattern)` - Find nodes matching pattern
- `find_functions(tree)` - Find all function definitions
- `find_calls(tree, func_name)` - Find calls to specific function
- `find_assignments(tree, var_name)` - Find assignments to variable

### AST Node Types

| Node Type | Description | Key Attributes |
|-----------|-------------|----------------|
| `Program` | Root program node | `body: List[Node]` |
| `FunctionDef` | Function definition | `name: str`, `args: List[str]`, `body: List[Node]` |
| `ClassDef` | Class definition | `name: str`, `bases: List[Node]`, `body: List[Node]` |
| `Assign` | Assignment statement | `targets: List[Node]`, `value: Node` |
| `BinOp` | Binary operation | `left: Node`, `op: str`, `right: Node` |
| `Call` | Function call | `func: Node`, `args: List[Node]` |
| `Name` | Variable/attribute name | `id: str`, `ctx: str` |
| `Constant` | Constant value | `value: Any`, `kind: str` |

### Transform Passes

| Pass | Description | Use Case |
|------|-------------|----------|
| `ConstantFoldingPass` | Evaluates constant expressions | `1 + 2` → `3` |
| `DeadCodeEliminationPass` | Removes unreachable code | Eliminates dead branches |
| `ExpressionSimplificationPass` | Simplifies expressions | `x + 0` → `x` |
| `UnusedVariableRemovalPass` | Removes unused variables | Cleans up dead code |
| `VariableRenamingPass` | Renames variables | Refactoring, obfuscation |
| `FunctionInliningPass` | Inlines simple functions | Performance optimization |

### Pattern Classes

| Pattern | Description | Example |
|---------|-------------|---------|
| `CallPattern` | Match function calls | `CallPattern(func_name="print")` |
| `AssignPattern` | Match assignments | `AssignPattern(target_name="x")` |
| `NamePattern` | Match variable names | `NamePattern(name="my_var")` |
| `WildcardPattern` | Match any node | `WildcardPattern()` |
| `AndPattern` | Logical AND of patterns | `AndPattern(pat1, pat2)` |
| `OrPattern` | Logical OR of patterns | `OrPattern(pat1, pat2)` |

##  Credits

### Core Contributors
- **slimeyy** - Original implementation and architecture

## shout out to ffa and jeff W mans

##  License

MIT License

Copyright (c) 2024 PyAST

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

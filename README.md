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

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [API Reference](#API-Reference)
- [Contributing](#contributing)
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
import pyast
from pyast import Parser, Transformer, Matcher

# Parse Python code into AST
parser = Parser()
tree = parser.parse('''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
''')

# Apply transformations
transformer = Transformer()
transformer.add_pass(pyast.ConstantFoldingPass())
transformer.add_pass(pyast.DeadCodeEliminationPass())
optimized_tree = transformer.transform(tree)

# Pattern matching
matcher = Matcher()
functions = matcher.find_functions(tree)
calls = matcher.find_calls(tree, "fibonacci")
```

##  Usage Examples

### Basic AST Operations
```python
from pyast import Parser, print_ast

# Parse and display AST
parser = Parser()
tree = parser.parse('x = 1 + 2 * 3')
print_ast(tree)
```

### Advanced Pattern Matching
```python
from pyast import Parser, Matcher

# Parse Python code
parser = Parser()
tree = parser.parse('x = 1 + 2; y = x * 3; z = fibonacci(y)')

matcher = Matcher()

# Find all function calls
calls = matcher.find_matches(tree, "call *")

# Find assignments to specific variables
assignments = matcher.find_matches(tree, "assign x")

# Find calls to specific functions
fib_calls = matcher.find_matches(tree, "call fibonacci")

# Complex patterns with regex
import_calls = matcher.find_matches(tree, "call /import.*/")
```

### AST Transformations
```python
from pyast import Transformer, VariableRenamingPass

# Rename variables
rename_pass = VariableRenamingPass("old_var", "new_var")
transformer = Transformer()
transformer.add_pass(rename_pass)

# Apply multiple transformations
transformer.add_pass(pyast.ConstantFoldingPass())
transformer.add_pass(pyast.UnusedVariableRemovalPass())

result = transformer.transform(tree)
```

### Visualization
```python
from pyast import Visualizer

visualizer = Visualizer()
dot_code = visualizer.to_dot(tree, "ast_graph.dot")
json_graph = visualizer.to_json_graph(tree, "ast_graph.json")
visualizer.export_graphml(tree, "ast_graph.graphml")
```

## 🔧 API Reference

### Core Classes

#### Parser
Main parser class for converting Python code to AST representation.

```python
parser = Parser(source_code: str = "", filename: str = "<string>")
tree = parser.parse(source_code: Optional[str] = None) -> Program
```

#### Transformer
Transformation engine that applies passes in sequence.

```python
transformer = Transformer()
transformer.add_pass(pass_instance: TransformPass)
result = transformer.transform(tree: Node) -> Node
```

#### Matcher
Pattern matching engine for AST queries.

```python
matcher = Matcher()
matches = matcher.find_matches(tree: Node, pattern: Union[str, Pattern]) -> List[Node]
functions = matcher.find_functions(tree: Node) -> List[FunctionDef]
```

### AST Node Types

| Node Type | Description | Attributes |
|-----------|-------------|------------|
| `Program` | Root program node | `body: List[Node]` |
| `FunctionDef` | Function definition | `name: str`, `args: List[str]`, `body: List[Node]` |
| `ClassDef` | Class definition | `name: str`, `bases: List[Node]`, `body: List[Node]` |
| `Assign` | Assignment statement | `targets: List[Node]`, `value: Node` |
| `BinOp` | Binary operation | `left: Node`, `op: str`, `right: Node` |
| `Call` | Function call | `func: Node`, `args: List[Node]` |
| `Name` | Variable/attribute name | `id: str`, `ctx: str` |
| `Constant` | Constant value | `value: Any`, `kind: str` |

### Transform Passes

| Pass | Description |
|------|-------------|
| `ConstantFoldingPass` | Evaluates constant expressions |
| `DeadCodeEliminationPass` | Removes unreachable code |
| `ExpressionSimplificationPass` | Simplifies expressions |
| `UnusedVariableRemovalPass` | Removes unused variables |
| `VariableRenamingPass` | Renames variables |
| `FunctionInliningPass` | Inlines simple functions |

### Query Language

PyAST supports a powerful query language for pattern matching:

```python
# Find all function calls
matcher.find_matches(tree, "call *")

# Find assignments to specific variables
matcher.find_matches(tree, "assign x")

# Find calls to specific functions
matcher.find_matches(tree, "call fibonacci")

# Complex patterns
matcher.find_matches(tree, "call print")
```

## 👥 Credits


### Core Contributors
- **slimeyy** - Original implementation and architecture

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


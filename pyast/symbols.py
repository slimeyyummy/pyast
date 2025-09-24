"""
Symbol table management for PyAST.

This module provides functionality to track variable definitions, scopes, and references.
"""

from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
from .nodes import Node, Name, FunctionDef, ClassDef, Assign


class Symbol:
    """Represents a symbol (variable, function, class) in the symbol table."""

    def __init__(self, name: str, node_type: str = "variable"):
        self.name = name
        self.node_type = node_type  # "variable", "function", "class", "parameter"
        self.definitions: List[Node] = []
        self.references: List[Node] = []
        self.scope_level: int = 0

    def add_definition(self, node: Node):
        """Add a definition site."""
        self.definitions.append(node)

    def add_reference(self, node: Node):
        """Add a reference site."""
        self.references.append(node)

    def is_used(self) -> bool:
        """Check if symbol is referenced."""
        return len(self.references) > 0

    def is_assigned(self) -> bool:
        """Check if symbol is assigned to."""
        return len(self.definitions) > 0


class Scope:
    """Represents a scope in the program."""

    def __init__(self, name: str, level: int, parent: Optional['Scope'] = None):
        self.name = name
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []

    def add_symbol(self, name: str, symbol: Symbol):
        """Add a symbol to this scope."""
        symbol.scope_level = self.level
        self.symbols[name] = symbol

    def get_symbol(self, name: str) -> Optional[Symbol]:
        """Get a symbol by name, searching up the scope chain."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.get_symbol(name)
        return None

    def add_child(self, child: 'Scope'):
        """Add a child scope."""
        self.children.append(child)


class SymbolTable:
    """Main symbol table manager."""

    def __init__(self):
        self.root_scope = Scope("global", 0)
        self.current_scope = self.root_scope
        self.scopes: List[Scope] = [self.root_scope]

    def enter_scope(self, name: str):
        """Enter a new scope."""
        new_scope = Scope(name, len(self.scopes), self.current_scope)
        self.current_scope.add_child(new_scope)
        self.current_scope = new_scope
        self.scopes.append(new_scope)

    def exit_scope(self):
        """Exit the current scope."""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
        else:
            raise ValueError("Cannot exit root scope")

    def define_symbol(self, name: str, node: Node, symbol_type: str = "variable"):
        """Define a symbol in the current scope."""
        symbol = Symbol(name, symbol_type)
        symbol.add_definition(node)
        self.current_scope.add_symbol(name, symbol)
        return symbol

    def reference_symbol(self, name: str, node: Node):
        """Reference a symbol (mark as used)."""
        symbol = self.current_scope.get_symbol(name)
        if symbol:
            symbol.add_reference(node)
        else:
            # Create a new symbol if it doesn't exist (forward reference)
            symbol = Symbol(name)
            symbol.add_reference(node)
            self.current_scope.add_symbol(name, symbol)
        return symbol

    def analyze(self, tree: Node):
        """Analyze the AST tree to build symbol table."""
        self._analyze_node(tree)

    def _analyze_node(self, node: Node):
        """Recursively analyze a node."""
        if isinstance(node, FunctionDef):
            # Define function
            self.define_symbol(node.name, node, "function")

            # Enter function scope
            self.enter_scope(f"function_{node.name}")

            # Define parameters
            for arg in node.args:
                self.define_symbol(arg, node, "parameter")

            # Analyze body
            for child in node.body:
                self._analyze_node(child)

            # Exit function scope
            self.exit_scope()

        elif isinstance(node, ClassDef):
            # Define class
            self.define_symbol(node.name, node, "class")

            # Enter class scope
            self.enter_scope(f"class_{node.name}")

            # Analyze body
            for child in node.body:
                self._analyze_node(child)

            # Exit class scope
            self.exit_scope()

        elif isinstance(node, Assign):
            # Handle assignments
            for target in node.targets:
                if isinstance(target, Name):
                    symbol = self.current_scope.get_symbol(target.id)
                    if symbol:
                        symbol.add_definition(node)
                    else:
                        self.define_symbol(target.id, node)

            # Analyze value
            if node.value:
                self._analyze_node(node.value)

        elif isinstance(node, Name):
            if node.ctx == "load":
                self.reference_symbol(node.id, node)
            elif node.ctx == "store":
                symbol = self.current_scope.get_symbol(node.id)
                if symbol:
                    symbol.add_definition(node)
                else:
                    self.define_symbol(node.id, node)

        # Recursively analyze child nodes
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    self._analyze_node(child)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            self._analyze_node(node.value)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            self._analyze_node(node.left)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            self._analyze_node(node.right)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            self._analyze_node(node.func)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            self._analyze_node(node.test)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            self._analyze_node(node.target)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            self._analyze_node(node.iter)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    self._analyze_node(target)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    self._analyze_node(arg)

        if hasattr(node, 'orelse') and isinstance(node.orelse, list):
            for child in node.orelse:
                if isinstance(child, Node):
                    self._analyze_node(child)

        if hasattr(node, 'handlers') and isinstance(node.handlers, list):
            for handler in node.handlers:
                if isinstance(handler, Node):
                    self._analyze_node(handler)

        if hasattr(node, 'finalbody') and isinstance(node.finalbody, list):
            for child in node.finalbody:
                if isinstance(child, Node):
                    self._analyze_node(child)

    def get_unused_variables(self) -> List[Symbol]:
        """Get list of unused variables."""
        unused = []
        for scope in self.scopes:
            for symbol in scope.symbols.values():
                if symbol.node_type == "variable" and not symbol.is_used():
                    unused.append(symbol)
        return unused

    def get_undefined_variables(self) -> List[str]:
        """Get list of potentially undefined variables."""
        undefined = []
        for scope in self.scopes:
            for symbol in scope.symbols.values():
                if not symbol.is_assigned() and symbol.node_type == "variable":
                    undefined.append(symbol.name)
        return undefined

    def print_table(self):
        """Print the symbol table for debugging."""
        print("Symbol Table:")
        for scope in self.scopes:
            indent = "  " * scope.level
            print(f"{indent}Scope: {scope.name}")
            for name, symbol in scope.symbols.items():
                defs = len(symbol.definitions)
                refs = len(symbol.references)
                print(f"{indent}  {name} ({symbol.node_type}): {defs} defs, {refs} refs")

"""
Symbol table management for PyAST.

This module provides functionality to track variable definitions, scopes, references,
types, and integrates with the parser for enhanced static analysis.
"""

from typing import Dict, List, Set, Optional, Any, Union
from collections import defaultdict
from functools import lru_cache
import ast

# Add current directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from nodes import (
    Node, Name, FunctionDef, ClassDef, Assign, BinOp, Call, Attribute,
    If, For, While, Return, Break, Continue, Import, ImportFrom, Try,
    ExceptHandler, With, Raise, Assert, Pass, Expr, Lambda, ListComp,
    DictComp, SetComp, GeneratorExp, Global, Nonlocal, Position, Constant
)


class TypeInfo:
    """Represents type information for symbols."""

    def __init__(self, type_name: str = "Any", confidence: float = 1.0):
        self.type_name = type_name
        self.confidence = confidence
        self.attributes: Dict[str, 'TypeInfo'] = {}
        self.methods: Dict[str, 'TypeInfo'] = {}

    def __str__(self):
        return f"{self.type_name}({self.confidence:.2f})"


class Symbol:
    """Represents a symbol (variable, function, class) in the symbol table."""

    def __init__(self, name: str, node_type: str = "variable"):
        self.name = name
        self.node_type = node_type  # "variable", "function", "class", "parameter", "lambda"
        self.definitions: List[Node] = []
        self.references: List[Node] = []
        self.scope_level: int = 0
        self.type_info: Optional[TypeInfo] = None
        self.is_global = False
        self.is_nonlocal = False
        self.is_builtin = False

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

    def set_type(self, type_info: TypeInfo):
        """Set type information for this symbol."""
        self.type_info = type_info

    def get_type(self) -> Optional[TypeInfo]:
        """Get type information."""
        return self.type_info


class Scope:
    """Represents a scope in the program."""

    def __init__(self, name: str, level: int, parent: Optional['Scope'] = None):
        self.name = name
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []
        self.globals: Set[str] = set()
        self.nonlocals: Set[str] = set()

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

    def mark_global(self, name: str):
        """Mark a symbol as global."""
        self.globals.add(name)

    def mark_nonlocal(self, name: str):
        """Mark a symbol as nonlocal."""
        self.nonlocals.add(name)

    def is_global(self, name: str) -> bool:
        """Check if a symbol is marked as global."""
        return name in self.globals

    def is_nonlocal(self, name: str) -> bool:
        """Check if a symbol is marked as nonlocal."""
        return name in self.nonlocals


class SymbolTable:
    """Main symbol table manager with advanced features."""

    def __init__(self):
        self.root_scope = Scope("global", 0)
        self.current_scope = self.root_scope
        self.scopes: List[Scope] = [self.root_scope]
        self.memo_cache: Dict[int, Any] = {}  # For memoization
        self._type_cache: Dict[str, TypeInfo] = {}  # For type inference

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
        # Check if it's marked as global or nonlocal
        if self.current_scope.is_global(name):
            # Find the symbol in global scope
            scope = self.current_scope
            while scope.parent:
                scope = scope.parent
            symbol = Symbol(name, symbol_type)
            symbol.add_definition(node)
            symbol.is_global = True
            scope.add_symbol(name, symbol)
            return symbol
        elif self.current_scope.is_nonlocal(name):
            # Find the symbol in nearest enclosing scope
            scope = self.current_scope.parent
            while scope and scope.parent:
                if name in scope.symbols:
                    symbol = scope.symbols[name]
                    symbol.add_definition(node)
                    symbol.is_nonlocal = True
                    return symbol
                scope = scope.parent
            # If not found, create in current scope
            symbol = Symbol(name, symbol_type)
            symbol.add_definition(node)
            symbol.is_nonlocal = True
            self.current_scope.add_symbol(name, symbol)
            return symbol

        # Normal symbol definition
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

    @lru_cache(maxsize=1024)
    def _memoized_analyze(self, node_id: int, node_type: str) -> Any:
        """Memoized version of node analysis."""
        # This will be called by _analyze_node_with_memo
        pass

    def analyze(self, tree: Node):
        """Analyze the AST tree to build symbol table."""
        self._analyze_node(tree)
        self._infer_types()

    def _analyze_node(self, node: Node):
        """Recursively analyze a node with memoization."""
        node_id = id(node)

        # Check memoization cache
        if node_id in self.memo_cache:
            return self.memo_cache[node_id]

        result = self._analyze_node_internal(node)
        self.memo_cache[node_id] = result
        return result

    def _analyze_node_internal(self, node: Node):
        """Internal node analysis without memoization."""
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

        elif isinstance(node, Global):
            # Handle global declarations
            for name in node.names:
                self.current_scope.mark_global(name)

        elif isinstance(node, Nonlocal):
            # Handle nonlocal declarations
            for name in node.names:
                self.current_scope.mark_nonlocal(name)

        elif isinstance(node, Lambda):
            # Handle lambda functions
            self.enter_scope("lambda")
            # Define parameters
            for arg in node.args:
                self.define_symbol(arg, node, "parameter")
            # Analyze body
            self._analyze_node(node.body)
            self.exit_scope()

        elif isinstance(node, (ListComp, DictComp, SetComp, GeneratorExp)):
            # Handle comprehensions
            self.enter_scope("comprehension")
            # Analyze generators and body
            for generator in node.generators:
                if hasattr(generator, 'target'):
                    self._analyze_node(generator.target)
                if hasattr(generator, 'iter'):
                    self._analyze_node(generator.iter)
                if hasattr(generator, 'ifs'):
                    for if_cond in generator.ifs:
                        self._analyze_node(if_cond)
            # Analyze the comprehension expression
            if hasattr(node, 'elt'):
                self._analyze_node(node.elt)  # For ListComp, SetComp
            elif hasattr(node, 'key') and hasattr(node, 'value'):
                self._analyze_node(node.key)  # For DictComp
                self._analyze_node(node.value)
            self.exit_scope()

        # Handle other node types with helper method
        self._analyze_child_nodes(node)

    def _analyze_child_nodes(self, node: Node):
        """Analyze child nodes using a mapping approach."""
        # Define child node attributes to analyze
        child_attrs = [
            ('body', list), ('value', Node), ('left', Node), ('right', Node),
            ('func', Node), ('test', Node), ('target', Node), ('iter', Node),
            ('orelse', list), ('handlers', list), ('finalbody', list),
            ('args', list), ('bases', list), ('decorator_list', list),
            ('exc', Node), ('cause', Node), ('msg', Node), ('type', Node)
        ]

        for attr_name, expected_type in child_attrs:
            if hasattr(node, attr_name):
                value = getattr(node, attr_name)
                if isinstance(value, expected_type):
                    if expected_type == list:
                        for child in value:
                            if isinstance(child, Node):
                                self._analyze_node(child)
                    else:
                        self._analyze_node(value)

    def _infer_types(self):
        """Infer types for symbols based on their usage."""
        for scope in self.scopes:
            for symbol in scope.symbols.values():
                if not symbol.type_info:
                    self._infer_symbol_type(symbol)

    def _infer_symbol_type(self, symbol: Symbol):
        """Infer type for a single symbol."""
        # Basic type inference based on definitions and usage
        if symbol.node_type == "function":
            symbol.set_type(TypeInfo("function"))
        elif symbol.node_type == "class":
            symbol.set_type(TypeInfo("class"))
        elif symbol.node_type == "parameter":
            symbol.set_type(TypeInfo("Any", 0.5))  # Low confidence for parameters
        else:
            # Try to infer from usage patterns
            if symbol.definitions:
                # Look at the type of values assigned to this variable
                assigned_types = []
                for def_node in symbol.definitions:
                    inferred_type = self._infer_node_type(def_node)
                    if inferred_type:
                        assigned_types.append(inferred_type)

                if assigned_types:
                    # Use the most common type
                    type_counts = defaultdict(int)
                    for t in assigned_types:
                        type_counts[t.type_name] += 1

                    most_common = max(type_counts.items(), key=lambda x: x[1])
                    confidence = most_common[1] / len(assigned_types)
                    symbol.set_type(TypeInfo(most_common[0], confidence))

    def _infer_node_type(self, node: Node) -> Optional[TypeInfo]:
        """Infer type of a node."""
        if isinstance(node, Name):
            symbol = self.current_scope.get_symbol(node.id)
            if symbol and symbol.type_info:
                return symbol.type_info

        elif isinstance(node, Constant):
            if isinstance(node.value, str):
                return TypeInfo("str")
            elif isinstance(node.value, int):
                return TypeInfo("int")
            elif isinstance(node.value, float):
                return TypeInfo("float")
            elif isinstance(node.value, bool):
                return TypeInfo("bool")
            elif node.value is None:
                return TypeInfo("NoneType")

        elif isinstance(node, BinOp):
            # Infer result type from operation
            left_type = self._infer_node_type(node.left)
            right_type = self._infer_node_type(node.right)

            if left_type and right_type:
                if left_type.type_name == right_type.type_name:
                    return left_type
                elif left_type.type_name in ("int", "float") and right_type.type_name in ("int", "float"):
                    return TypeInfo("float" if "float" in (left_type.type_name, right_type.type_name) else "int")

        elif isinstance(node, Call):
            # Function call - return type is harder to infer without more context
            return TypeInfo("Any", 0.3)

        return TypeInfo("Any", 0.1)  # Default fallback

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

    def get_symbols_by_type(self, node_type: str) -> List[Symbol]:
        """Get all symbols of a specific type."""
        symbols = []
        for scope in self.scopes:
            for symbol in scope.symbols.values():
                if symbol.node_type == node_type:
                    symbols.append(symbol)
        return symbols

    def print_table(self):
        """Print the symbol table for debugging."""
        print("Symbol Table:")
        for scope in self.scopes:
            indent = "  " * scope.level
            print(f"{indent}Scope: {scope.name}")
            for name, symbol in scope.symbols.items():
                defs = len(symbol.definitions)
                refs = len(symbol.references)
                type_info = f" [{symbol.type_info}]" if symbol.type_info else ""
                flags = []
                if symbol.is_global:
                    flags.append("global")
                if symbol.is_nonlocal:
                    flags.append("nonlocal")
                if symbol.is_builtin:
                    flags.append("builtin")
                flag_str = f" ({', '.join(flags)})" if flags else ""
                print(f"{indent}  {name} ({symbol.node_type}){type_info}{flag_str}: {defs} defs, {refs} refs")

    def clear_cache(self):
        """Clear memoization cache."""
        self.memo_cache.clear()
        self._memoized_analyze.cache_clear()

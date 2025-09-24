"""
PyAST: A Python AST implementation with advanced features.

This package provides a simple, extensible AST implementation for Python code
analysis and transformation with features like round-trip parsing, pattern
matching, transformation pipelines, and more.
"""

from .nodes import *
from .parser import Parser
from .transformer import Transformer, TransformPass, ConstantFoldingPass, DeadCodeEliminationPass, ExpressionSimplificationPass, UnusedVariableRemovalPass, VariableRenamingPass, FunctionInliningPass
from .matcher import Matcher, Pattern, NodePattern, NamePattern, CallPattern, AssignPattern, WildcardPattern, RegexPattern, AndPattern, OrPattern, NotPattern, QueryLanguage
from .serializer import Serializer
from .symbols import SymbolTable
from .visualization import Visualizer
from .plugins import PluginManager
from .errors import *
from .utils import *
from .main import main

__version__ = "0.1.0"
__all__ = [
    # Nodes
    "Node", "Program", "FunctionDef", "ClassDef", "Assign", "BinOp", "Name",
    "Constant", "Call", "Attribute", "If", "For", "While", "Return", "Break",
    "Continue", "Import", "ImportFrom", "Try", "ExceptHandler", "With", "Raise",
    "Assert", "Pass", "Expr", "Comment",

    # Core classes
    "Parser", "Transformer", "Matcher", "Serializer", "SymbolTable",
    "Visualizer", "PluginManager",

    # Transform passes
    "TransformPass", "ConstantFoldingPass", "DeadCodeEliminationPass",
    "ExpressionSimplificationPass", "UnusedVariableRemovalPass",
    "VariableRenamingPass", "FunctionInliningPass",

    # Pattern matching
    "Pattern", "NodePattern", "NamePattern", "CallPattern", "AssignPattern",
    "WildcardPattern", "RegexPattern", "AndPattern", "OrPattern", "NotPattern",
    "QueryLanguage",

    # Error classes
    "PyASTError", "ParseError", "TransformError", "MatchError", "SymbolError",
    "SerializeError", "VisualizationError", "PluginError", "ValidationError",

    # Utility functions
    "print_ast", "find_all_names", "find_all_constants", "replace_node",
    "clone_node", "get_tree_size", "main"
]

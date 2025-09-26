"""
PyAST: A Python AST implementation with advanced features.

This package provides a simple, extensible AST implementation for Python code
analysis and transformation with features like round-trip parsing, pattern
matching, transformation pipelines, and more.
"""

# Core AST components
from .nodes import (
    Node, NodeType, Position,
    Program, FunctionDef, ClassDef, Assign, BinOp, Name, Constant,
    Call, Attribute, If, For, While, Return, Break, Continue,
    Import, ImportFrom, Try, ExceptHandler, With, Raise, Assert,
    Pass, Expr, Lambda, ListComp, DictComp, SetComp, GeneratorExp,
    Global, Nonlocal, Comment
)

# Pattern matching
from .matcher import (
    Matcher, Pattern, NodePattern, NamePattern, CallPattern,
    AssignPattern, WildcardPattern, RegexPattern, AndPattern, OrPattern, NotPattern,
    QueryLanguage
)

# Plugin system
from .plugins import (
    PluginManager,
    CustomNode, ExampleTransformPass
)

# Serialization
from .serializer import Serializer

# Symbol table management
from .symbols import (
    SymbolTable, Symbol, Scope, TypeInfo
)

# Transformation pipeline
from .transformer import (
    Transformer, TransformPass,
    ConstantFoldingPass, DeadCodeEliminationPass, UnusedVariableRemovalPass,
    ExpressionSimplificationPass, VariableRenamingPass, FunctionInliningPass
)

# Visualization
from .visualization import Visualizer

# Parser
from .parser import Parser

# Create convenient aliases for the main components
class Nodes:
    """Main node classes and types."""
    # Import all node classes
    Node = Node
    NodeType = NodeType
    Position = Position
    Program = Program
    FunctionDef = FunctionDef
    ClassDef = ClassDef
    Assign = Assign
    BinOp = BinOp
    Name = Name
    Constant = Constant
    Call = Call
    Attribute = Attribute
    If = If
    For = For
    While = While
    Return = Return
    Break = Break
    Continue = Continue
    Import = Import
    ImportFrom = ImportFrom
    Try = Try
    ExceptHandler = ExceptHandler
    With = With
    Raise = Raise
    Assert = Assert
    Pass = Pass
    Expr = Expr
    Lambda = Lambda
    ListComp = ListComp
    DictComp = DictComp
    SetComp = SetComp
    GeneratorExp = GeneratorExp
    Global = Global
    Nonlocal = Nonlocal
    Comment = Comment

class Matcher:
    """Pattern matching system."""
    # Import main matcher classes
    Matcher = Matcher
    Pattern = Pattern
    NodePattern = NodePattern
    NamePattern = NamePattern
    CallPattern = CallPattern
    AssignPattern = AssignPattern
    WildcardPattern = WildcardPattern
    RegexPattern = RegexPattern
    AndPattern = AndPattern
    OrPattern = OrPattern
    NotPattern = NotPattern
    QueryLanguage = QueryLanguage

class Plugins:
    """Plugin management system."""
    PluginManager = PluginManager
    CustomNode = CustomNode
    ExampleTransformPass = ExampleTransformPass

class Symbols:
    """Symbol table management."""
    SymbolTable = SymbolTable
    Symbol = Symbol
    Scope = Scope
    TypeInfo = TypeInfo

class Transformer:
    """Transformation pipeline."""
    Transformer = Transformer
    TransformPass = TransformPass
    ConstantFoldingPass = ConstantFoldingPass
    DeadCodeEliminationPass = DeadCodeEliminationPass
    UnusedVariableRemovalPass = UnusedVariableRemovalPass
    ExpressionSimplificationPass = ExpressionSimplificationPass
    VariableRenamingPass = VariableRenamingPass
    FunctionInliningPass = FunctionInliningPass

# Keep simple aliases for backward compatibility
Visualization = Visualizer
Serializer = Serializer
Parser = Parser

__version__ = "0.1.0"
__all__ = [
    # Core AST
    "Node", "NodeType", "Position",
    "Program", "FunctionDef", "ClassDef", "Assign", "BinOp", "Name", "Constant",
    "Call", "Attribute", "If", "For", "While", "Return", "Break", "Continue",
    "Import", "ImportFrom", "Try", "ExceptHandler", "With", "Raise", "Assert",
    "Pass", "Expr", "Lambda", "ListComp", "DictComp", "SetComp", "GeneratorExp",
    "Global", "Nonlocal", "Comment",

    # Pattern matching
    "Matcher", "Pattern", "NodePattern", "NamePattern", "CallPattern",
    "AssignPattern", "WildcardPattern", "RegexPattern", "AndPattern", "OrPattern", "NotPattern",
    "QueryLanguage",

    # Plugin system
    "PluginManager", "Plugins",
    "CustomNode", "ExampleTransformPass",

    # Serialization
    "Serializer",

    # Symbol table
    "SymbolTable", "Symbol", "Scope", "TypeInfo", "Symbols",

    # Transformation
    "Transformer", "TransformPass",
    "ConstantFoldingPass", "DeadCodeEliminationPass", "UnusedVariableRemovalPass",
    "ExpressionSimplificationPass", "VariableRenamingPass", "FunctionInliningPass",

    # Visualization
    "Visualizer", "Visualization",

    # Parser
    "Parser",

    # Main aliases
    "Nodes", "Plugins", "Symbols", "Visualization"
]

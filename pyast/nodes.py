"""
AST Node definitions for PyAST.

This module defines the basic AST node classes with a simple, uniform structure.
"""

import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Enumeration of all possible AST node types."""
    PROGRAM = "Program"
    FUNCTION_DEF = "FunctionDef"
    CLASS_DEF = "ClassDef"
    ASSIGN = "Assign"
    BIN_OP = "BinOp"
    NAME = "Name"
    CONSTANT = "Constant"
    CALL = "Call"
    ATTRIBUTE = "Attribute"
    IF = "If"
    FOR = "For"
    WHILE = "While"
    RETURN = "Return"
    BREAK = "Break"
    CONTINUE = "Continue"
    IMPORT = "Import"
    IMPORT_FROM = "ImportFrom"
    TRY = "Try"
    EXCEPT_HANDLER = "ExceptHandler"
    WITH = "With"
    RAISE = "Raise"
    ASSERT = "Assert"
    PASS = "Pass"
    EXPR = "Expr"
    COMMENT = "Comment"


@dataclass
class Position:
    """Represents a position in source code."""
    line: int
    column: int
    offset: int

    def to_dict(self) -> Dict[str, int]:
        return {"line": self.line, "column": self.column, "offset": self.offset}


@dataclass
class Node:
    """Base class for all AST nodes."""
    node_type: NodeType
    position: Optional[Position] = None
    leading_comments: List[str] = field(default_factory=list)
    trailing_comments: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        result = {
            "type": self.node_type.value,
            "leading_comments": self.leading_comments,
            "trailing_comments": self.trailing_comments,
            "extra": self.extra
        }
        if self.position:
            result["position"] = self.position.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Create node from dictionary representation."""
        node_type = NodeType(data["type"])
        position = None
        if "position" in data:
            pos_data = data["position"]
            position = Position(
                line=pos_data["line"],
                column=pos_data["column"],
                offset=pos_data["offset"]
            )

        node_class = NODE_CLASSES.get(node_type)
        if not node_class:
            # Create generic node for unknown types
            node = Node(node_type, position)
            node.leading_comments = data.get("leading_comments", [])
            node.trailing_comments = data.get("trailing_comments", [])
            node.extra = data.get("extra", {})
            return node

        # Create specific node type
        node_data = {k: v for k, v in data.items() if k not in ["type", "leading_comments", "trailing_comments", "extra", "position"]}
        node = node_class(**node_data)
        node.position = position
        node.leading_comments = data.get("leading_comments", [])
        node.trailing_comments = data.get("trailing_comments", [])
        node.extra = data.get("extra", {})
        return node


@dataclass
class Program(Node):
    """Root node representing a complete Python program."""
    body: List[Node] = field(default_factory=list)

    def __init__(self, body=None, node_type=NodeType.PROGRAM):
        if body is None:
            body = []
        super().__init__(node_type=node_type)
        self.body = body


@dataclass
class FunctionDef(Node):
    """Function definition node."""
    name: str = ""
    args: List[str] = field(default_factory=list)
    body: List[Node] = field(default_factory=list)
    decorator_list: List[Node] = field(default_factory=list)

    def __init__(self, name="", args=None, body=None, decorator_list=None, node_type=NodeType.FUNCTION_DEF):
        if args is None:
            args = []
        if body is None:
            body = []
        if decorator_list is None:
            decorator_list = []
        super().__init__(node_type=node_type)
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list


@dataclass
class ClassDef(Node):
    """Class definition node."""
    name: str = ""
    bases: List[Node] = field(default_factory=list)
    body: List[Node] = field(default_factory=list)
    decorator_list: List[Node] = field(default_factory=list)

    def __init__(self, name="", bases=None, body=None, decorator_list=None, node_type=NodeType.CLASS_DEF):
        if bases is None:
            bases = []
        if body is None:
            body = []
        if decorator_list is None:
            decorator_list = []
        super().__init__(node_type=node_type)
        self.name = name
        self.bases = bases
        self.body = body
        self.decorator_list = decorator_list


@dataclass
class Assign(Node):
    """Assignment node."""
    targets: List[Node] = field(default_factory=list)
    value: Optional[Node] = None

    def __init__(self, targets=None, value=None, node_type=NodeType.ASSIGN):
        if targets is None:
            targets = []
        super().__init__(node_type=node_type)
        self.targets = targets
        self.value = value


@dataclass
class BinOp(Node):
    """Binary operation node."""
    left: Optional[Node] = None
    op: str = ""
    right: Optional[Node] = None

    def __init__(self, left=None, op="", right=None, node_type=NodeType.BIN_OP):
        super().__init__(node_type=node_type)
        self.left = left
        self.op = op
        self.right = right


@dataclass
class Name(Node):
    """Name/identifier node."""
    id: str = ""
    ctx: str = "load"  # 'load', 'store', 'del'

    def __init__(self, id="", ctx="load", node_type=NodeType.NAME):
        super().__init__(node_type=node_type)
        self.id = id
        self.ctx = ctx


@dataclass
class Constant(Node):
    """Constant value node."""
    value: Any = None
    kind: Optional[str] = None  # 'str', 'int', 'float', 'None', etc.

    def __init__(self, value=None, kind=None, node_type=NodeType.CONSTANT):
        super().__init__(node_type=node_type)
        self.value = value
        self.kind = kind


@dataclass
class Call(Node):
    """Function call node."""
    func: Optional[Node] = None
    args: List[Node] = field(default_factory=list)
    keywords: List[Dict[str, Node]] = field(default_factory=list)

    def __init__(self, func=None, args=None, keywords=None, node_type=NodeType.CALL):
        if args is None:
            args = []
        if keywords is None:
            keywords = []
        super().__init__(node_type=node_type)
        self.func = func
        self.args = args
        self.keywords = keywords


@dataclass
class Attribute(Node):
    """Attribute access node."""
    value: Optional[Node] = None
    attr: str = ""
    ctx: str = "load"

    def __init__(self, value=None, attr="", ctx="load", node_type=NodeType.ATTRIBUTE):
        super().__init__(node_type=node_type)
        self.value = value
        self.attr = attr
        self.ctx = ctx


@dataclass
class If(Node):
    """If statement node."""
    test: Optional[Node] = None
    body: List[Node] = field(default_factory=list)
    orelse: List[Node] = field(default_factory=list)

    def __init__(self, test=None, body=None, orelse=None, node_type=NodeType.IF):
        if body is None:
            body = []
        if orelse is None:
            orelse = []
        super().__init__(node_type=node_type)
        self.test = test
        self.body = body
        self.orelse = orelse


@dataclass
class For(Node):
    """For loop node."""
    target: Optional[Node] = None
    iter: Optional[Node] = None
    body: List[Node] = field(default_factory=list)
    orelse: List[Node] = field(default_factory=list)

    def __init__(self, target=None, iter=None, body=None, orelse=None, node_type=NodeType.FOR):
        if body is None:
            body = []
        if orelse is None:
            orelse = []
        super().__init__(node_type=node_type)
        self.target = target
        self.iter = iter
        self.body = body
        self.orelse = orelse


@dataclass
class While(Node):
    """While loop node."""
    test: Optional[Node] = None
    body: List[Node] = field(default_factory=list)
    orelse: List[Node] = field(default_factory=list)

    def __init__(self, test=None, body=None, orelse=None, node_type=NodeType.WHILE):
        if body is None:
            body = []
        if orelse is None:
            orelse = []
        super().__init__(node_type=node_type)
        self.test = test
        self.body = body
        self.orelse = orelse


@dataclass
class Return(Node):
    """Return statement node."""
    value: Optional[Node] = None

    def __init__(self, value=None, node_type=NodeType.RETURN):
        super().__init__(node_type=node_type)
        self.value = value


@dataclass
class Break(Node):
    """Break statement node."""

    def __init__(self, node_type=NodeType.BREAK):
        super().__init__(node_type=node_type)


@dataclass
class Continue(Node):
    """Continue statement node."""

    def __init__(self, node_type=NodeType.CONTINUE):
        super().__init__(node_type=node_type)


@dataclass
class Import(Node):
    """Import statement node."""
    names: List[Dict[str, str]] = field(default_factory=list)  # List of {'name': str, 'asname': str}

    def __init__(self, names=None, node_type=NodeType.IMPORT):
        if names is None:
            names = []
        super().__init__(node_type=node_type)
        self.names = names


@dataclass
class ImportFrom(Node):
    """Import from statement node."""
    module: str = ""
    names: List[Dict[str, str]] = field(default_factory=list)
    level: int = 0

    def __init__(self, module="", names=None, level=0, node_type=NodeType.IMPORT_FROM):
        if names is None:
            names = []
        super().__init__(node_type=node_type)
        self.module = module
        self.names = names
        self.level = level


@dataclass
class Try(Node):
    """Try-except node."""
    body: List[Node] = field(default_factory=list)
    handlers: List[Node] = field(default_factory=list)
    orelse: List[Node] = field(default_factory=list)
    finalbody: List[Node] = field(default_factory=list)

    def __init__(self, body=None, handlers=None, orelse=None, finalbody=None, node_type=NodeType.TRY):
        if body is None:
            body = []
        if handlers is None:
            handlers = []
        if orelse is None:
            orelse = []
        if finalbody is None:
            finalbody = []
        super().__init__(node_type=node_type)
        self.body = body
        self.handlers = handlers
        self.orelse = orelse
        self.finalbody = finalbody


@dataclass
class ExceptHandler(Node):
    """Exception handler node."""
    type: Optional[Node] = None
    name: str = ""
    body: List[Node] = field(default_factory=list)

    def __init__(self, type=None, name="", body=None, node_type=NodeType.EXCEPT_HANDLER):
        if body is None:
            body = []
        super().__init__(node_type=node_type)
        self.type = type
        self.name = name
        self.body = body


@dataclass
class With(Node):
    """With statement node."""
    items: List[Dict[str, Node]] = field(default_factory=list)  # List of {'context_expr': Node, 'optional_vars': Node}
    body: List[Node] = field(default_factory=list)

    def __init__(self, items=None, body=None, node_type=NodeType.WITH):
        if items is None:
            items = []
        if body is None:
            body = []
        super().__init__(node_type=node_type)
        self.items = items
        self.body = body


@dataclass
class Raise(Node):
    """Raise statement node."""
    exc: Optional[Node] = None
    cause: Optional[Node] = None

    def __init__(self, exc=None, cause=None, node_type=NodeType.RAISE):
        super().__init__(node_type=node_type)
        self.exc = exc
        self.cause = cause


@dataclass
class Assert(Node):
    """Assert statement node."""
    test: Optional[Node] = None
    msg: Optional[Node] = None

    def __init__(self, test=None, msg=None, node_type=NodeType.ASSERT):
        super().__init__(node_type=node_type)
        self.test = test
        self.msg = msg


@dataclass
class Pass(Node):
    """Pass statement node."""

    def __init__(self, node_type=NodeType.PASS):
        super().__init__(node_type=node_type)


@dataclass
class Expr(Node):
    """Expression statement node."""
    value: Optional[Node] = None

    def __init__(self, value=None, node_type=NodeType.EXPR):
        super().__init__(node_type=node_type)
        self.value = value


@dataclass
class Comment(Node):
    """Comment node."""
    value: str = ""

    def __init__(self, value="", node_type=NodeType.COMMENT):
        super().__init__(node_type=node_type)
        self.value = value


# Mapping for creating nodes from type
NODE_CLASSES = {
    NodeType.PROGRAM: Program,
    NodeType.FUNCTION_DEF: FunctionDef,
    NodeType.CLASS_DEF: ClassDef,
    NodeType.ASSIGN: Assign,
    NodeType.BIN_OP: BinOp,
    NodeType.NAME: Name,
    NodeType.CONSTANT: Constant,
    NodeType.CALL: Call,
    NodeType.ATTRIBUTE: Attribute,
    NodeType.IF: If,
    NodeType.FOR: For,
    NodeType.WHILE: While,
    NodeType.RETURN: Return,
    NodeType.BREAK: Break,
    NodeType.CONTINUE: Continue,
    NodeType.IMPORT: Import,
    NodeType.IMPORT_FROM: ImportFrom,
    NodeType.TRY: Try,
    NodeType.EXCEPT_HANDLER: ExceptHandler,
    NodeType.WITH: With,
    NodeType.RAISE: Raise,
    NodeType.ASSERT: Assert,
    NodeType.PASS: Pass,
    NodeType.EXPR: Expr,
    NodeType.COMMENT: Comment,
}

"""
Parser implementation for PyAST.

This module provides a parser that can parse Python code into our AST representation,
with error tolerance and formatting preservation.
"""

import ast
import re
from typing import List, Optional, Dict, Any, Tuple
from .nodes import (
    NodeType,
    Node,
    Program,
    FunctionDef,
    ClassDef,
    Assign,
    BinOp,
    Name,
    Constant,
    Call,
    Attribute,
    If,
    For,
    While,
    Return,
    Break,
    Continue,
    Import,
    ImportFrom,
    Try,
    ExceptHandler,
    With,
    Raise,
    Assert,
    Pass,
    Expr,
)
from .errors import ParseError, parse_error_at_position


class Parser:
    """Main parser class for converting Python code to AST."""

    def __init__(self, source_code: str = "", filename: str = "<string>"):
        self.source_code = source_code
        self.filename = filename
        self.lines = source_code.split('\n') if source_code else []
        self.errors: List[ParseError] = []

    def parse(self, source_code: Optional[str] = None) -> Program:
        """Parse source code into AST."""
        if source_code is not None:
            self.source_code = source_code
            self.lines = source_code.split('\n')

        self.errors = []  # Reset errors
        try:
            # Use Python's ast module as a starting point
            tree = ast.parse(self.source_code, filename=self.filename)
            return self._convert_ast(tree)
        except SyntaxError as e:
            # Handle syntax errors gracefully
            error = parse_error_at_position(
                str(e), e.lineno, e.offset,
                filename=self.filename
            )
            self.errors.append(error)
            # Try to parse what we can
            return self._parse_error_tolerant()
        except Exception as e:
            error = ParseError(f"Unexpected parsing error: {str(e)}")
            self.errors.append(error)
            return self._parse_error_tolerant()

    def _convert_ast(self, node: ast.AST) -> Node:
        """Convert Python AST node to our AST node."""
        method_name = f"_convert_{type(node).__name__}"
        method = getattr(self, method_name, self._convert_generic)
        return method(node)

    def _convert_Module(self, node: ast.Module) -> Program:
        body = [self._convert_ast(child) for child in node.body]
        return Program(body=body)

    def _convert_FunctionDef(self, node: ast.FunctionDef) -> FunctionDef:
        args = [arg.arg for arg in node.args.args]
        body = [self._convert_ast(child) for child in node.body]
        decorators = [self._convert_ast(decorator) for decorator in node.decorator_list]

        return FunctionDef(
            name=node.name,
            args=args,
            body=body,
            decorator_list=decorators
        )

    def _convert_ClassDef(self, node: ast.ClassDef) -> ClassDef:
        bases = [self._convert_ast(base) for base in node.bases]
        body = [self._convert_ast(child) for child in node.body]
        decorators = [self._convert_ast(decorator) for decorator in node.decorator_list]

        return ClassDef(
            name=node.name,
            bases=bases,
            body=body,
            decorator_list=decorators
        )

    def _convert_Assign(self, node: ast.Assign) -> Assign:
        targets = [self._convert_ast(target) for target in node.targets]
        value = self._convert_ast(node.value) if node.value else None

        return Assign(targets=targets, value=value)

    def _convert_BinOp(self, node: ast.BinOp) -> BinOp:
        left = self._convert_ast(node.left)
        right = self._convert_ast(node.right)
        op = self._get_binop_symbol(node.op)

        return BinOp(left=left, op=op, right=right)

    def _get_binop_symbol(self, op: ast.AST) -> str:
        """Get string representation of binary operator."""
        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "//",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.LShift: "<<",
            ast.RShift: ">>",
            ast.BitOr: "|",
            ast.BitXor: "^",
            ast.BitAnd: "&",
            ast.MatMult: "@"
        }
        return op_map.get(type(op), str(op))

    def _convert_Name(self, node: ast.Name) -> Name:
        return Name(id=node.id, ctx=self._get_ctx(node.ctx))

    def _convert_Constant(self, node: ast.Constant) -> Constant:
        return Constant(value=node.value, kind=type(node.value).__name__)

    def _convert_Call(self, node: ast.Call) -> Call:
        func = self._convert_ast(node.func)
        args = [self._convert_ast(arg) for arg in node.args]
        keywords = [{"arg": kw.arg, "value": self._convert_ast(kw.value)} for kw in node.keywords]

        return Call(func=func, args=args, keywords=keywords)

    def _convert_Attribute(self, node: ast.Attribute) -> Attribute:
        value = self._convert_ast(node.value)
        return Attribute(value=value, attr=node.attr, ctx=self._get_ctx(node.ctx))

    def _convert_If(self, node: ast.If) -> If:
        test = self._convert_ast(node.test)
        body = [self._convert_ast(child) for child in node.body]
        orelse = [self._convert_ast(child) for child in node.orelse]

        return If(test=test, body=body, orelse=orelse)

    def _convert_For(self, node: ast.For) -> For:
        target = self._convert_ast(node.target)
        iter_expr = self._convert_ast(node.iter)
        body = [self._convert_ast(child) for child in node.body]
        orelse = [self._convert_ast(child) for child in node.orelse]

        return For(target=target, iter=iter_expr, body=body, orelse=orelse)

    def _convert_While(self, node: ast.While) -> While:
        test = self._convert_ast(node.test)
        body = [self._convert_ast(child) for child in node.body]
        orelse = [self._convert_ast(child) for child in node.orelse]

        return While(test=test, body=body, orelse=orelse)

    def _convert_Return(self, node: ast.Return) -> Return:
        value = self._convert_ast(node.value) if node.value else None
        return Return(value=value)

    def _convert_Break(self, node: ast.Break) -> Break:
        return Break()

    def _convert_Continue(self, node: ast.Continue) -> Continue:
        return Continue()

    def _convert_Import(self, node: ast.Import) -> Import:
        names = [{"name": alias.name, "asname": alias.asname} for alias in node.names]
        return Import(names=names)

    def _convert_ImportFrom(self, node: ast.ImportFrom) -> ImportFrom:
        names = [{"name": alias.name, "asname": alias.asname} for alias in node.names]
        return ImportFrom(module=node.module or "", names=names, level=node.level)

    def _convert_Try(self, node: ast.Try) -> Try:
        body = [self._convert_ast(child) for child in node.body]
        handlers = [self._convert_ast(handler) for handler in node.handlers]
        orelse = [self._convert_ast(child) for child in node.orelse]
        finalbody = [self._convert_ast(child) for child in node.finalbody]

        return Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)

    def _convert_ExceptHandler(self, node: ast.ExceptHandler) -> ExceptHandler:
        type_expr = self._convert_ast(node.type) if node.type else None
        body = [self._convert_ast(child) for child in node.body]

        return ExceptHandler(type=type_expr, name=node.name or "", body=body)

    def _convert_With(self, node: ast.With) -> With:
        items = [{"context_expr": self._convert_ast(item.context_expr),
                 "optional_vars": self._convert_ast(item.optional_vars) if item.optional_vars else None}
                for item in node.items]
        body = [self._convert_ast(child) for child in node.body]

        return With(items=items, body=body)

    def _convert_Raise(self, node: ast.Raise) -> Raise:
        exc = self._convert_ast(node.exc) if node.exc else None
        cause = self._convert_ast(node.cause) if node.cause else None

        return Raise(exc=exc, cause=cause)

    def _convert_Assert(self, node: ast.Assert) -> Assert:
        test = self._convert_ast(node.test)
        msg = self._convert_ast(node.msg) if node.msg else None

        return Assert(test=test, msg=msg)

    def _convert_Pass(self, node: ast.Pass) -> Pass:
        return Pass()

    def _convert_Expr(self, node: ast.Expr) -> Expr:
        value = self._convert_ast(node.value)
        return Expr(value=value)

    def _convert_generic(self, node: ast.AST) -> Node:
        """Fallback for unhandled node types."""
        return Node(node_type=NodeType.PROGRAM)  # Placeholder

    def _get_ctx(self, ctx: ast.AST) -> str:
        """Convert AST context to string."""
        ctx_map = {
            ast.Load: "load",
            ast.Store: "store",
            ast.Del: "del"
        }
        return ctx_map.get(type(ctx), "load")

    def _parse_error_tolerant(self) -> Program:
        """Attempt to parse code despite syntax errors using error recovery."""
        lines = self.source_code.split('\n')
        body = []

        # Simple error recovery: try to parse line by line
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # Try to parse as a simple statement
                stmt_tree = ast.parse(line, filename=self.filename, mode='single')
                if stmt_tree:
                    converted = self._convert_ast(stmt_tree)
                    if converted:
                        body.append(converted)
            except SyntaxError:
                # Create a generic expression node for unparseable lines
                from .nodes import Expr, Constant
                body.append(Expr(value=Constant(value=line)))
            except Exception:
                # Create a generic expression node for any other errors
                from .nodes import Expr, Constant
                body.append(Expr(value=Constant(value=line)))

        return Program(body=body)

    def parse_expression(self, expr: str) -> Optional[Node]:
        """Parse a single expression."""
        try:
            tree = ast.parse(expr, mode='eval')
            return self._convert_ast(tree.body)
        except SyntaxError as e:
            error = parse_error_at_position(str(e), e.lineno, e.offset)
            self.errors.append(error)
            return None
        except Exception as e:
            error = ParseError(f"Failed to parse expression: {str(e)}")
            self.errors.append(error)
            return None

    def get_errors(self) -> List[ParseError]:
        """Get list of parsing errors."""
        return self.errors.copy()

    def has_errors(self) -> bool:
        """Check if there were parsing errors."""
        return len(self.errors) > 0

    def clear_errors(self):
        """Clear all parsing errors."""
        self.errors.clear()

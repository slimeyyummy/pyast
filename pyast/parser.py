"""
Parser implementation for PyAST.

This module provides a parser that can parse Python code into our AST representation,
with error tolerance and formatting preservation.
"""

import ast
import re
import sys
import os
from typing import List, Optional, Dict, Any, Tuple, Union
from collections import defaultdict
from functools import lru_cache

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from nodes import (
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
    Position,
)
from errors import ParseError, parse_error_at_position


class Parser:
    """Main parser class for converting Python code to AST."""

    def __init__(self, source_code: str = "", filename: str = "<string>"):
        self.source_code = source_code
        self.filename = filename
        self.lines = source_code.split('\n') if source_code else []
        self.errors: List[ParseError] = []
        self.memo_cache: Dict[str, Node] = {}  # For memoization
        self._comment_cache: Dict[int, List[str]] = defaultdict(list)  # For comment tracking

    def parse(self, source_code: Optional[str] = None) -> Program:
        """Parse source code into AST."""
        if source_code is not None:
            self.source_code = source_code
            self.lines = source_code.split('\n')

        self.errors = []  # Reset errors
        self.memo_cache.clear()  # Clear memo cache
        self._comment_cache.clear()  # Clear comment cache

        try:
            # Use Python's ast module with type_comments for better comment preservation
            tree = ast.parse(
                self.source_code,
                filename=self.filename,
                type_comments=True
            )
            result = self._convert_ast(tree)
            self._extract_comments(tree)  # Extract comments
            return result
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

    def _create_position(self, node: ast.AST) -> Optional[Position]:
        """Create position information from AST node."""
        if hasattr(node, 'lineno') and hasattr(node, 'col_offset'):
            line = getattr(node, 'lineno', 1)
            col = getattr(node, 'col_offset', 0)
            offset = getattr(node, 'end_lineno', line)
            end_col = getattr(node, 'end_col_offset', col)

            return Position(
                line=line,
                column=col,
                offset=offset
            )
        return None

    def _convert_children(self, node: ast.AST, attributes: List[str]) -> Dict[str, Any]:
        """Helper method to convert child nodes based on attribute names."""
        result = {}
        for attr in attributes:
            if hasattr(node, attr):
                value = getattr(node, attr)
                if isinstance(value, list):
                    result[attr] = [self._convert_ast(child) for child in value]
                elif value is not None:
                    result[attr] = self._convert_ast(value)
                else:
                    result[attr] = value
        return result

    def _convert_ast(self, node: ast.AST) -> Node:
        """Convert Python AST node to our AST node."""
        method_name = f"_convert_{type(node).__name__}"
        method = getattr(self, method_name, self._convert_generic)
        result = method(node)

        # Add position information
        position = self._create_position(node)
        if position and hasattr(result, 'position'):
            result.position = position

        return result

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

    # New AST node types (Python 3.10+)
    def _convert_Match(self, node: ast.Match) -> Node:
        """Convert Match node (Python 3.10+ structural pattern matching)."""
        subject = self._convert_ast(node.subject)
        cases = [self._convert_ast(case) for case in node.cases]

        # Create a generic node since Match isn't in our NodeType enum yet
        generic_node = Node(node_type=NodeType.PROGRAM)  # Placeholder
        generic_node.extra = {
            "match_subject": subject,
            "match_cases": cases,
            "ast_type": "Match"
        }
        return generic_node

    def _convert_MatchCase(self, node: ast.match_case) -> Node:
        """Convert MatchCase node (Python 3.10+ structural pattern matching)."""
        pattern = self._convert_ast(node.pattern)
        guard = self._convert_ast(node.guard) if node.guard else None
        body = [self._convert_ast(stmt) for stmt in node.body]

        # Create a generic node since MatchCase isn't in our NodeType enum yet
        generic_node = Node(node_type=NodeType.PROGRAM)  # Placeholder
        generic_node.extra = {
            "case_pattern": pattern,
            "case_guard": guard,
            "case_body": body,
            "ast_type": "MatchCase"
        }
        return generic_node

    def _convert_generic(self, node: ast.AST) -> Node:
        """Fallback for unhandled node types with better diagnostics."""
        # Create a generic node with the actual AST node type name
        generic_node = Node(node_type=NodeType.PROGRAM)  # Using Program as fallback
        generic_node.extra = {
            "ast_type": type(node).__name__,
            "original_node": str(node),
            "unhandled": True
        }

        # Try to extract common attributes
        if hasattr(node, '_fields'):
            for field in node._fields:
                if hasattr(node, field):
                    value = getattr(node, field)
                    if isinstance(value, list):
                        generic_node.extra[field] = [self._convert_ast(item) if isinstance(item, ast.AST) else item for item in value]
                    elif isinstance(value, ast.AST):
                        generic_node.extra[field] = self._convert_ast(value)
                    else:
                        generic_node.extra[field] = value

        return generic_node

    def _get_ctx(self, ctx: ast.AST) -> str:
        """Convert AST context to string."""
        ctx_map = {
            ast.Load: "load",
            ast.Store: "store",
            ast.Del: "del"
        }
        return ctx_map.get(type(ctx), "load")

    def _extract_comments(self, tree: ast.AST):
        """Extract comments from AST and associate with nodes."""
        # Basic comment extraction - can be enhanced with asttokens
        for node in ast.walk(tree):
            if hasattr(node, 'lineno'):
                # Look for comments around this line
                line_num = getattr(node, 'lineno', 1)
                if line_num in self._comment_cache:
                    if hasattr(node, 'leading_comments'):
                        # This would be set by a proper comment extraction library
                        pass

    def _parse_error_tolerant(self) -> Program:
        """Attempt to parse code despite syntax errors using improved error recovery."""
        # Try to parse in blocks instead of individual lines
        blocks = self._split_into_blocks()
        body = []

        for block in blocks:
            try:
                # Try to parse as a statement block
                block_tree = ast.parse(block, filename=self.filename)
                if block_tree:
                    converted = self._convert_ast(block_tree)
                    if converted:
                        body.append(converted)
            except SyntaxError:
                # Try to parse as expression
                try:
                    expr_tree = ast.parse(block, filename=self.filename, mode='eval')
                    body.append(Expr(value=self._convert_ast(expr_tree.body[0])))
                except SyntaxError:
                    # Create a generic expression node for unparseable blocks
                    from nodes import Expr, Constant
                    body.append(Expr(value=Constant(value=block.strip())))
            except Exception:
                # Create a generic expression node for any other errors
                from nodes import Expr, Constant
                body.append(Expr(value=Constant(value=block.strip())))

        return Program(body=body)

    def _split_into_blocks(self) -> List[str]:
        lines = self.source_code.split('\n')
        blocks = []
        current_block = []

        for line in lines:
            current_block.append(line)

            # Simple heuristic: split on empty lines or major statement boundaries
            if (not line.strip() or
                line.strip().startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try ', 'with '))):
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []

        # Add remaining block
        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks

    def parse_expression(self, expr: str) -> Optional[Node]:
        """Parse a single expression with memoization."""
        # Check cache first
        if expr in self.memo_cache:
            return self.memo_cache[expr]

        try:
            tree = ast.parse(expr, mode='eval')
            result = self._convert_ast(tree.body)
            # Cache the result
            self.memo_cache[expr] = result
            return result
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

    def analyze_symbols(self) -> 'SymbolTable':
        """Analyze symbols in the parsed AST and return symbol table."""
        from symbols import SymbolTable

        symbol_table = SymbolTable()
        symbol_table.analyze(self._convert_ast(ast.parse(self.source_code, filename=self.filename)))
        return symbol_table

    def parse_with_symbols(self) -> Tuple[Program, 'SymbolTable']:
        """Parse source code and return both AST and symbol table."""
        from symbols import SymbolTable

        # Parse the AST
        ast_tree = self.parse()

        # Create and populate symbol table
        symbol_table = SymbolTable()
        symbol_table.analyze(ast_tree)

        return ast_tree, symbol_table

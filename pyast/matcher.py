"""
Pattern matching system for PyAST.

This module provides functionality to match patterns in AST trees.
"""

import re
from typing import List, Dict, Any, Optional, Callable, Union, Pattern as RegexPattern
from .nodes import Node, NodeType, Name, Call, Assign, FunctionDef
from .errors import MatchError, pattern_match_failed_error


class Pattern:
    """Base class for AST patterns."""

    def match(self, node: Node) -> bool:
        """Check if pattern matches the given node."""
        raise NotImplementedError

    def capture(self, node: Node) -> Dict[str, Any]:
        """Capture variables from matching node."""
        return {}


class NodePattern(Pattern):
    """Pattern for matching specific node types."""

    def __init__(self, node_type: NodeType, **constraints):
        self.node_type = node_type
        self.constraints = constraints

    def match(self, node: Node) -> bool:
        if node.node_type != self.node_type:
            return False

        for attr, expected_value in self.constraints.items():
            if hasattr(node, attr):
                actual_value = getattr(node, attr)
                if callable(expected_value):
                    if not expected_value(actual_value):
                        return False
                elif actual_value != expected_value:
                    return False
        return True


class NamePattern(Pattern):
    """Pattern for matching name nodes."""

    def __init__(self, name: Optional[str] = None, regex: Optional[str] = None):
        self.name = name
        self.regex = re.compile(regex) if regex else None

    def match(self, node: Node) -> bool:
        if not isinstance(node, Name):
            return False
        if self.name is not None and node.id != self.name:
            return False
        if self.regex and not self.regex.match(node.id):
            return False
        return True


class CallPattern(Pattern):
    """Pattern for matching function calls."""

    def __init__(self, func_name: Optional[str] = None, func_regex: Optional[str] = None,
                 args_count: Optional[int] = None, min_args: Optional[int] = None,
                 max_args: Optional[int] = None):
        self.func_name = func_name
        self.func_regex = re.compile(func_regex) if func_regex else None
        self.args_count = args_count
        self.min_args = min_args
        self.max_args = max_args

    def match(self, node: Node) -> bool:
        if not isinstance(node, Call):
            return False

        if self.func_name is not None:
            if not isinstance(node.func, Name):
                return False
            if node.func.id != self.func_name:
                return False

        if self.func_regex:
            if not isinstance(node.func, Name):
                return False
            if not self.func_regex.match(node.func.id):
                return False

        if self.args_count is not None:
            if len(node.args) != self.args_count:
                return False

        if self.min_args is not None and len(node.args) < self.min_args:
            return False

        if self.max_args is not None and len(node.args) > self.max_args:
            return False

        return True


class AssignPattern(Pattern):
    """Pattern for matching assignments."""

    def __init__(self, target_name: Optional[str] = None, target_regex: Optional[str] = None,
                 value_type: Optional[NodeType] = None):
        self.target_name = target_name
        self.target_regex = re.compile(target_regex) if target_regex else None
        self.value_type = value_type

    def match(self, node: Node) -> bool:
        if not isinstance(node, Assign):
            return False

        if self.target_name is not None or self.target_regex:
            if not node.targets:
                return False
            target = node.targets[0]
            if not isinstance(target, Name):
                return False
            if self.target_name and target.id != self.target_name:
                return False
            if self.target_regex and not self.target_regex.match(target.id):
                return False

        if self.value_type and node.value and node.value.node_type != self.value_type:
            return False

        return True


class WildcardPattern(Pattern):
    """Pattern that matches any node."""

    def __init__(self, name: str = "_"):
        self.capture_name = name

    def match(self, node: Node) -> bool:
        return True

    def capture(self, node: Node) -> Dict[str, Any]:
        return {self.capture_name: node}


class RegexPattern(Pattern):
    """Pattern for regex-based matching on node attributes."""

    def __init__(self, attribute: str, regex: str):
        self.attribute = attribute
        self.regex = re.compile(regex)

    def match(self, node: Node) -> bool:
        if not hasattr(node, self.attribute):
            return False
        value = getattr(node, self.attribute)
        if isinstance(value, str):
            return bool(self.regex.match(value))
        return False


class AndPattern(Pattern):
    """Pattern that matches if all sub-patterns match."""

    def __init__(self, *patterns: Pattern):
        self.patterns = patterns

    def match(self, node: Node) -> bool:
        return all(pattern.match(node) for pattern in self.patterns)

    def capture(self, node: Node) -> Dict[str, Any]:
        captures = {}
        for pattern in self.patterns:
            captures.update(pattern.capture(node))
        return captures


class OrPattern(Pattern):
    """Pattern that matches if any sub-pattern matches."""

    def __init__(self, *patterns: Pattern):
        self.patterns = patterns

    def match(self, node: Node) -> bool:
        return any(pattern.match(node) for pattern in self.patterns)

    def capture(self, node: Node) -> Dict[str, Any]:
        # Return captures from the first matching pattern
        for pattern in self.patterns:
            if pattern.match(node):
                return pattern.capture(node)
        return {}


class NotPattern(Pattern):
    """Pattern that matches if the sub-pattern does not match."""

    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    def match(self, node: Node) -> bool:
        return not self.pattern.match(node)


class QueryLanguage:
    """Query language for pattern matching."""

    def __init__(self):
        self.variables = {}

    def parse_query(self, query: str) -> Pattern:
        """Parse a query string into a pattern."""
        query = query.strip()

        # Simple query parsing - can be extended
        if query.startswith("call "):
            func_name = query[5:].strip()
            if func_name.startswith("/") and func_name.endswith("/"):
                return CallPattern(func_regex=func_name[1:-1])
            else:
                return CallPattern(func_name=func_name)

        elif query.startswith("assign "):
            var_name = query[7:].strip()
            if var_name.startswith("/") and var_name.endswith("/"):
                return AssignPattern(target_regex=var_name[1:-1])
            else:
                return AssignPattern(target_name=var_name)

        elif query.startswith("name "):
            name = query[5:].strip()
            if name.startswith("/") and name.endswith("/"):
                return NamePattern(regex=name[1:-1])
            else:
                return NamePattern(name=name)

        elif query == "*":
            return WildcardPattern()

        else:
            raise MatchError(f"Invalid query pattern: {query}")

    def compile_query(self, query: str) -> Pattern:
        """Compile a query string into a pattern."""
        return self.parse_query(query)


class Matcher:
    """Main pattern matching engine."""

    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.query_lang = QueryLanguage()

    def register_pattern(self, name: str, pattern: Pattern):
        """Register a named pattern."""
        self.patterns[name] = pattern

    def find_matches(self, tree: Node, pattern: Union[str, Pattern]) -> List[Node]:
        """Find all nodes matching the given pattern."""
        if isinstance(pattern, str):
            if pattern not in self.patterns:
                try:
                    pattern = self.query_lang.compile_query(pattern)
                except MatchError as e:
                    raise MatchError(f"Pattern '{pattern}' not registered and invalid query: {str(e)}")
            else:
                pattern = self.patterns[pattern]

        matches = []
        self._traverse_and_match(tree, pattern, matches)
        return matches

    def _traverse_and_match(self, node: Node, pattern: Pattern, matches: List[Node]):
        """Traverse tree and collect matches."""
        try:
            if pattern.match(node):
                matches.append(node)
        except Exception as e:
            raise MatchError(f"Error during pattern matching: {str(e)}")

        # Recursively check child nodes
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    self._traverse_and_match(child, pattern, matches)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            self._traverse_and_match(node.value, pattern, matches)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            self._traverse_and_match(node.left, pattern, matches)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            self._traverse_and_match(node.right, pattern, matches)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            self._traverse_and_match(node.func, pattern, matches)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            self._traverse_and_match(node.test, pattern, matches)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            self._traverse_and_match(node.target, pattern, matches)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            self._traverse_and_match(node.iter, pattern, matches)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    self._traverse_and_match(target, pattern, matches)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    self._traverse_and_match(arg, pattern, matches)

        if hasattr(node, 'orelse') and isinstance(node.orelse, list):
            for child in node.orelse:
                if isinstance(child, Node):
                    self._traverse_and_match(child, pattern, matches)

        if hasattr(node, 'handlers') and isinstance(node.handlers, list):
            for handler in node.handlers:
                if isinstance(handler, Node):
                    self._traverse_and_match(handler, pattern, matches)

        if hasattr(node, 'finalbody') and isinstance(node.finalbody, list):
            for child in node.finalbody:
                if isinstance(child, Node):
                    self._traverse_and_match(child, pattern, matches)

    def _traverse_and_query(self, node: Node, query_func: Callable[[Node], bool], matches: List[Node]):
        """Traverse tree and collect nodes matching query function."""
        try:
            if query_func(node):
                matches.append(node)
        except Exception as e:
            raise MatchError(f"Error during query execution: {str(e)}")

        # Recursively check child nodes
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    self._traverse_and_query(child, query_func, matches)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            self._traverse_and_query(node.value, query_func, matches)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            self._traverse_and_query(node.left, query_func, matches)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            self._traverse_and_query(node.right, query_func, matches)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            self._traverse_and_query(node.func, query_func, matches)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            self._traverse_and_query(node.test, query_func, matches)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            self._traverse_and_query(node.target, query_func, matches)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            self._traverse_and_query(node.iter, query_func, matches)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    self._traverse_and_query(target, query_func, matches)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    self._traverse_and_query(arg, query_func, matches)

        if hasattr(node, 'orelse') and isinstance(node.orelse, list):
            for child in node.orelse:
                if isinstance(child, Node):
                    self._traverse_and_query(child, query_func, matches)

        if hasattr(node, 'handlers') and isinstance(node.handlers, list):
            for handler in node.handlers:
                if isinstance(handler, Node):
                    self._traverse_and_query(handler, query_func, matches)

        if hasattr(node, 'finalbody') and isinstance(node.finalbody, list):
            for child in node.finalbody:
                if isinstance(child, Node):
                    self._traverse_and_query(child, query_func, matches)

    def query(self, tree: Node, query_func: Callable[[Node], bool]) -> List[Node]:
        """Query tree using a custom function."""
        matches = []
        self._traverse_and_query(tree, query_func, matches)
        return matches

    def find_functions(self, tree: Node) -> List[FunctionDef]:
        """Find all function definitions."""
        return self.query(tree, lambda node: isinstance(node, FunctionDef))

    def find_calls(self, tree: Node, func_name: Optional[str] = None) -> List[Call]:
        """Find all function calls, optionally filtered by name."""
        if func_name:
            pattern = CallPattern(func_name=func_name)
            return self.find_matches(tree, pattern)
        else:
            return self.query(tree, lambda node: isinstance(node, Call))

    def find_assignments(self, tree: Node, var_name: Optional[str] = None) -> List[Assign]:
        """Find all assignments, optionally filtered by variable name."""
        if var_name:
            pattern = AssignPattern(target_name=var_name)
            return self.find_matches(tree, pattern)
        else:
            return self.query(tree, lambda node: isinstance(node, Assign))

    def find_names(self, tree: Node, name: Optional[str] = None) -> List[Name]:
        """Find all name references, optionally filtered by name."""
        if name:
            pattern = NamePattern(name=name)
            return self.find_matches(tree, pattern)
        else:
            return self.query(tree, lambda node: isinstance(node, Name))

    def query_by_string(self, tree: Node, query: str) -> List[Node]:
        """Query tree using a string query."""
        pattern = self.query_lang.compile_query(query)
        return self.find_matches(tree, pattern)

    def count_matches(self, tree: Node, pattern: Union[str, Pattern]) -> int:
        """Count number of matches for a pattern."""
        matches = self.find_matches(tree, pattern)
        return len(matches)

    def has_match(self, tree: Node, pattern: Union[str, Pattern]) -> bool:
        """Check if tree has any matches for a pattern."""
        return self.count_matches(tree, pattern) > 0

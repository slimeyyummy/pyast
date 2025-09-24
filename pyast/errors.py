"""
Error classes for PyAST.

This module defines structured exception classes for consistent error handling
across the PyAST package.
"""

from typing import Optional, Dict, Any, List


class PyASTError(Exception):
    """Base exception class for all PyAST errors."""

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or "PYAST_ERROR"
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ParseError(PyASTError):
    """Exception raised when parsing fails."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 offset: Optional[int] = None, filename: Optional[str] = None):
        details = {}
        if line is not None:
            details["line"] = line
        if column is not None:
            details["column"] = column
        if offset is not None:
            details["offset"] = offset
        if filename:
            details["filename"] = filename

        super().__init__(message, "PARSE_ERROR", details)


class TransformError(PyASTError):
    """Exception raised when transformation fails."""

    def __init__(self, message: str, pass_name: Optional[str] = None, node_type: Optional[str] = None):
        details = {}
        if pass_name:
            details["pass_name"] = pass_name
        if node_type:
            details["node_type"] = node_type

        super().__init__(message, "TRANSFORM_ERROR", details)


class MatchError(PyASTError):
    """Exception raised when pattern matching fails."""

    def __init__(self, message: str, pattern: Optional[str] = None, node_type: Optional[str] = None):
        details = {}
        if pattern:
            details["pattern"] = pattern
        if node_type:
            details["node_type"] = node_type

        super().__init__(message, "MATCH_ERROR", details)


class SymbolError(PyASTError):
    """Exception raised when symbol table operations fail."""

    def __init__(self, message: str, symbol_name: Optional[str] = None, scope: Optional[str] = None):
        details = {}
        if symbol_name:
            details["symbol_name"] = symbol_name
        if scope:
            details["scope"] = scope

        super().__init__(message, "SYMBOL_ERROR", details)


class SerializeError(PyASTError):
    """Exception raised when serialization/deserialization fails."""

    def __init__(self, message: str, format_type: Optional[str] = None, node_type: Optional[str] = None):
        details = {}
        if format_type:
            details["format_type"] = format_type
        if node_type:
            details["node_type"] = node_type

        super().__init__(message, "SERIALIZE_ERROR", details)


class VisualizationError(PyASTError):
    """Exception raised when visualization fails."""

    def __init__(self, message: str, format_type: Optional[str] = None):
        details = {}
        if format_type:
            details["format_type"] = format_type

        super().__init__(message, "VISUALIZATION_ERROR", details)


class PluginError(PyASTError):
    """Exception raised when plugin operations fail."""

    def __init__(self, message: str, plugin_name: Optional[str] = None, plugin_type: Optional[str] = None):
        details = {}
        if plugin_name:
            details["plugin_name"] = plugin_name
        if plugin_type:
            details["plugin_type"] = plugin_type

        super().__init__(message, "PLUGIN_ERROR", details)


class ValidationError(PyASTError):
    """Exception raised when AST validation fails."""

    def __init__(self, message: str, node_type: Optional[str] = None, constraint: Optional[str] = None):
        details = {}
        if node_type:
            details["node_type"] = node_type
        if constraint:
            details["constraint"] = constraint

        super().__init__(message, "VALIDATION_ERROR", details)


# Error factories for common error scenarios
def parse_error_at_position(message: str, line: int, column: int, filename: str = "<string>") -> ParseError:
    """Create a parse error with position information."""
    return ParseError(message, line=line, column=column, filename=filename)


def symbol_not_found_error(symbol_name: str, scope: str = "global") -> SymbolError:
    """Create a symbol not found error."""
    return SymbolError(f"Symbol '{symbol_name}' not found in scope '{scope}'", symbol_name, scope)


def transformation_failed_error(pass_name: str, node_type: str) -> TransformError:
    """Create a transformation failed error."""
    return TransformError(f"Transformation failed in pass '{pass_name}' for node type '{node_type}'",
                         pass_name, node_type)


def pattern_match_failed_error(pattern: str, node_type: str) -> MatchError:
    """Create a pattern match failed error."""
    return MatchError(f"Pattern '{pattern}' failed to match node of type '{node_type}'", pattern, node_type)


def serialization_failed_error(format_type: str, node_type: str) -> SerializeError:
    """Create a serialization failed error."""
    return SerializeError(f"Serialization failed for format '{format_type}' and node type '{node_type}'",
                         format_type, node_type)

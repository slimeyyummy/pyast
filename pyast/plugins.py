"""
Plugin system for PyAST.

This module provides a plugin system for registering custom passes and node types.
"""

from typing import Dict, List, Type, Any, Callable
from .nodes import Node, NodeType
from .transformer import TransformPass


class PluginManager:
    """Manages plugins for PyAST."""

    def __init__(self):
        self.custom_nodes: Dict[str, Type[Node]] = {}
        self.custom_passes: Dict[str, Type[TransformPass]] = {}
        self.hooks: Dict[str, List[Callable]] = {}

    def register_node_type(self, node_type: str, node_class: Type[Node]):
        """Register a custom node type."""
        self.custom_nodes[node_type] = node_class

    def register_pass(self, name: str, pass_class: Type[TransformPass]):
        """Register a custom transformation pass."""
        self.custom_passes[name] = pass_class

    def register_hook(self, hook_name: str, hook_func: Callable):
        """Register a hook function."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(hook_func)

    def get_node_class(self, node_type: str) -> Type[Node]:
        """Get node class by type."""
        if node_type in self.custom_nodes:
            return self.custom_nodes[node_type]
        # Fall back to built-in nodes
        from .nodes import NODE_CLASSES
        return NODE_CLASSES.get(NodeType(node_type), Node)

    def create_pass(self, name: str, **kwargs) -> TransformPass:
        """Create a transformation pass by name."""
        if name in self.custom_passes:
            return self.custom_passes[name](**kwargs)
        else:
            raise ValueError(f"Pass '{name}' not found")

    def call_hooks(self, hook_name: str, *args, **kwargs):
        """Call all registered hooks for a given name."""
        if hook_name in self.hooks:
            for hook in self.hooks[hook_name]:
                hook(*args, **kwargs)

    def list_custom_nodes(self) -> List[str]:
        """List all registered custom node types."""
        return list(self.custom_nodes.keys())

    def list_custom_passes(self) -> List[str]:
        """List all registered custom passes."""
        return list(self.custom_passes.keys())

    def list_hooks(self) -> List[str]:
        """List all registered hook names."""
        return list(self.hooks.keys())


# Global plugin manager instance
plugin_manager = PluginManager()


def register_node_type(node_type: str, node_class: Type[Node]):
    """Register a custom node type globally."""
    plugin_manager.register_node_type(node_type, node_class)


def register_pass(name: str, pass_class: Type[TransformPass]):
    """Register a custom transformation pass globally."""
    plugin_manager.register_pass(name, pass_class)


def register_hook(hook_name: str, hook_func: Callable):
    """Register a hook function globally."""
    plugin_manager.register_hook(hook_name, hook_func)


# Example custom node and pass for demonstration
class CustomNode(Node):
    """Example custom node type."""

    def __init__(self, custom_field: str = ""):
        super().__init__(NodeType.PROGRAM)  # Using PROGRAM as base type
        self.custom_field = custom_field


class ExampleTransformPass(TransformPass):
    """Example custom transformation pass."""

    def __init__(self, suffix: str = "_transformed"):
        super().__init__("example_transform")
        self.suffix = suffix

    def transform(self, node: Node) -> Node:
        if hasattr(node, 'name'):
            node.name += self.suffix
        return node


# Register example plugins
plugin_manager.register_node_type("CustomNode", CustomNode)
plugin_manager.register_pass("example", ExampleTransformPass)

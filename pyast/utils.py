"""
Utility functions for PyAST.

This module provides various utility functions for working with AST trees.
"""

from typing import List, Optional, Any
from .nodes import Node, Name, Constant, Call, Assign


def print_ast(tree: Node, indent: int = 0):
    """Pretty print an AST tree."""
    indent_str = "  " * indent
    print(f"{indent_str}{tree.node_type.value}", end="")

    if hasattr(tree, 'name') and tree.name:
        print(f"({tree.name})", end="")
    elif hasattr(tree, 'id') and tree.id:
        print(f"({tree.id})", end="")
    elif hasattr(tree, 'value') and tree.value is not None:
        print(f"({repr(tree.value)})", end="")
    elif hasattr(tree, 'op') and tree.op:
        print(f"({tree.op})", end="")

    print()

    if hasattr(tree, 'body') and isinstance(tree.body, list):
        for child in tree.body:
            if isinstance(child, Node):
                print_ast(child, indent + 1)

    if hasattr(tree, 'value') and isinstance(tree.value, Node):
        print_ast(tree.value, indent + 1)

    if hasattr(tree, 'left') and isinstance(tree.left, Node):
        print_ast(tree.left, indent + 1)

    if hasattr(tree, 'right') and isinstance(tree.right, Node):
        print_ast(tree.right, indent + 1)

    if hasattr(tree, 'func') and isinstance(tree.func, Node):
        print_ast(tree.func, indent + 1)

    if hasattr(tree, 'test') and isinstance(tree.test, Node):
        print_ast(tree.test, indent + 1)

    if hasattr(tree, 'target') and isinstance(tree.target, Node):
        print_ast(tree.target, indent + 1)

    if hasattr(tree, 'iter') and isinstance(tree.iter, Node):
        print_ast(tree.iter, indent + 1)

    if hasattr(tree, 'targets') and isinstance(tree.targets, list):
        for target in tree.targets:
            if isinstance(target, Node):
                print_ast(target, indent + 1)

    if hasattr(tree, 'args') and isinstance(tree.args, list):
        for arg in tree.args:
            if isinstance(arg, Node):
                print_ast(arg, indent + 1)


def find_all_names(tree: Node) -> List[Name]:
    """Find all Name nodes in the tree."""
    names = []

    def traverse(node: Node):
        if isinstance(node, Name):
            names.append(node)

        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    traverse(child)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            traverse(node.value)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            traverse(node.left)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            traverse(node.right)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            traverse(node.func)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            traverse(node.test)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            traverse(node.target)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            traverse(node.iter)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    traverse(target)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    traverse(arg)

    traverse(tree)
    return names


def find_all_constants(tree: Node) -> List[Constant]:
    """Find all Constant nodes in the tree."""
    constants = []

    def traverse(node: Node):
        if isinstance(node, Constant):
            constants.append(node)

        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    traverse(child)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            traverse(node.value)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            traverse(node.left)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            traverse(node.right)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            traverse(node.func)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            traverse(node.test)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            traverse(node.target)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            traverse(node.iter)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    traverse(target)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    traverse(arg)

    traverse(tree)
    return constants


def replace_node(tree: Node, old_node: Node, new_node: Node) -> Node:
    """Replace a node in the tree with another node."""
    if tree is old_node:
        return new_node

    if hasattr(tree, 'body') and isinstance(tree.body, list):
        tree.body = [
            replace_node(child, old_node, new_node) if isinstance(child, Node) else child
            for child in tree.body
        ]

    if hasattr(tree, 'value') and isinstance(tree.value, Node):
        tree.value = replace_node(tree.value, old_node, new_node)

    if hasattr(tree, 'left') and isinstance(tree.left, Node):
        tree.left = replace_node(tree.left, old_node, new_node)

    if hasattr(tree, 'right') and isinstance(tree.right, Node):
        tree.right = replace_node(tree.right, old_node, new_node)

    if hasattr(tree, 'func') and isinstance(tree.func, Node):
        tree.func = replace_node(tree.func, old_node, new_node)

    if hasattr(tree, 'test') and isinstance(tree.test, Node):
        tree.test = replace_node(tree.test, old_node, new_node)

    if hasattr(tree, 'target') and isinstance(tree.target, Node):
        tree.target = replace_node(tree.target, old_node, new_node)

    if hasattr(tree, 'iter') and isinstance(tree.iter, Node):
        tree.iter = replace_node(tree.iter, old_node, new_node)

    if hasattr(tree, 'targets') and isinstance(tree.targets, list):
        tree.targets = [
            replace_node(target, old_node, new_node) if isinstance(target, Node) else target
            for target in tree.targets
        ]

    if hasattr(tree, 'args') and isinstance(tree.args, list):
        tree.args = [
            replace_node(arg, old_node, new_node) if isinstance(arg, Node) else arg
            for arg in tree.args
        ]

    return tree


def clone_node(node: Node) -> Node:
    """Create a deep copy of a node."""
    # This is a simplified clone - in a real implementation,
    # you'd want a proper deep copy
    import copy
    return copy.deepcopy(node)


def get_tree_size(tree: Node) -> int:
    """Get the total number of nodes in the tree."""
    count = 1

    if hasattr(tree, 'body') and isinstance(tree.body, list):
        for child in tree.body:
            if isinstance(child, Node):
                count += get_tree_size(child)

    if hasattr(tree, 'value') and isinstance(tree.value, Node):
        count += get_tree_size(tree.value)

    if hasattr(tree, 'left') and isinstance(tree.left, Node):
        count += get_tree_size(tree.left)

    if hasattr(tree, 'right') and isinstance(tree.right, Node):
        count += get_tree_size(tree.right)

    if hasattr(tree, 'func') and isinstance(tree.func, Node):
        count += get_tree_size(tree.func)

    if hasattr(tree, 'test') and isinstance(tree.test, Node):
        count += get_tree_size(tree.test)

    if hasattr(tree, 'target') and isinstance(tree.target, Node):
        count += get_tree_size(tree.target)

    if hasattr(tree, 'iter') and isinstance(tree.iter, Node):
        count += get_tree_size(tree.iter)

    if hasattr(tree, 'targets') and isinstance(tree.targets, list):
        for target in tree.targets:
            if isinstance(target, Node):
                count += get_tree_size(target)

    if hasattr(tree, 'args') and isinstance(tree.args, list):
        for arg in tree.args:
            if isinstance(arg, Node):
                count += get_tree_size(arg)

    return count


# Export all utility functions
__all__ = [
    "print_ast", "find_all_names", "find_all_constants", "replace_node",
    "clone_node", "get_tree_size"
]

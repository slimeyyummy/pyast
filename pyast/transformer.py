"""
Transformation pipeline for PyAST.

This module provides a system for applying transformations to AST trees.
"""

from typing import List, Callable, Any, Dict, Optional
from .nodes import Node, Program, Name, Constant, BinOp, Assign, FunctionDef, Call, Return
from .errors import TransformError, transformation_failed_error


class TransformPass:
    """Base class for transformation passes."""

    def __init__(self, name: str):
        self.name = name

    def transform(self, node: Node) -> Node:
        """Transform the given node. Override in subclasses."""
        return node

    def should_transform(self, node: Node) -> bool:
        """Check if this pass should transform the given node."""
        return True


class ConstantFoldingPass(TransformPass):
    """Pass that performs constant folding."""

    def __init__(self):
        super().__init__("constant_folding")

    def transform(self, node: Node) -> Node:
        if hasattr(node, 'left') and hasattr(node, 'right') and hasattr(node, 'op'):
            # Try to evaluate binary operations
            if hasattr(node.left, 'value') and hasattr(node.right, 'value'):
                try:
                    left_val = node.left.value
                    right_val = node.right.value
                    op = node.op

                    if op == '+':
                        result = left_val + right_val
                    elif op == '-':
                        result = left_val - right_val
                    elif op == '*':
                        result = left_val * right_val
                    elif op == '/':
                        if right_val == 0:
                            raise TransformError("Division by zero in constant folding")
                        result = left_val / right_val
                    elif op == '//':
                        if right_val == 0:
                            raise TransformError("Division by zero in constant folding")
                        result = left_val // right_val
                    elif op == '%':
                        if right_val == 0:
                            raise TransformError("Modulo by zero in constant folding")
                        result = left_val % right_val
                    elif op == '**':
                        result = left_val ** right_val
                    else:
                        return node

                    # Replace with constant node
                    from .nodes import Constant
                    return Constant(value=result)
                except (ZeroDivisionError, OverflowError, ValueError) as e:
                    raise TransformError(f"Constant folding failed: {str(e)}")
                except Exception:
                    pass
        return node


class DeadCodeEliminationPass(TransformPass):
    """Pass that eliminates unreachable code."""

    def __init__(self):
        super().__init__("dead_code_elimination")
        self.reachable = True

    def transform(self, node: Node) -> Node:
        if isinstance(node, Program):
            self.reachable = True
            node.body = [self.transform(child) for child in node.body if self.should_transform(child)]
            return node

        # Mark unreachable code after return/break/continue
        if self._is_terminating_statement(node):
            self.reachable = False

        if not self.reachable:
            # Replace unreachable code with pass
            from .nodes import Pass
            return Pass()

        return node

    def _is_terminating_statement(self, node: Node) -> bool:
        from .nodes import Return, Break, Continue, Raise
        return isinstance(node, (Return, Break, Continue, Raise))


class UnusedVariableRemovalPass(TransformPass):
    """Pass that removes unused variables."""

    def __init__(self):
        super().__init__("unused_variable_removal")
        self.used_variables: set = set()

    def transform(self, node: Node) -> Node:
        if isinstance(node, Program):
            # First pass: collect used variables
            self._collect_used_variables(node)

            # Second pass: remove unused assignments
            return self._remove_unused_assignments(node)

        return node

    def _collect_used_variables(self, node: Node):
        """Collect all used variable names."""
        if isinstance(node, Name) and node.ctx == "load":
            self.used_variables.add(node.id)

        # Recursively check child nodes
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                if isinstance(child, Node):
                    self._collect_used_variables(child)

        if hasattr(node, 'value') and isinstance(node.value, Node):
            self._collect_used_variables(node.value)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            self._collect_used_variables(node.left)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            self._collect_used_variables(node.right)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            self._collect_used_variables(node.func)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            self._collect_used_variables(node.test)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            self._collect_used_variables(node.target)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            self._collect_used_variables(node.iter)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            for target in node.targets:
                if isinstance(target, Node):
                    self._collect_used_variables(target)

        if hasattr(node, 'args') and isinstance(node.args, list):
            for arg in node.args:
                if isinstance(arg, Node):
                    self._collect_used_variables(arg)

    def _remove_unused_assignments(self, node: Node) -> Node:
        """Remove assignments to unused variables."""
        if isinstance(node, Program):
            node.body = [self._remove_unused_assignments(child) for child in node.body]
            return node

        if isinstance(node, Assign):
            # Check if any target is unused
            targets_to_remove = []
            for i, target in enumerate(node.targets):
                if isinstance(target, Name) and target.id not in self.used_variables:
                    targets_to_remove.append(i)

            # Remove unused targets from right to left to maintain indices
            for i in reversed(targets_to_remove):
                del node.targets[i]

            # If no targets left, replace with just the value expression
            if not node.targets:
                return node.value if node.value else node

        # Recursively transform children
        if hasattr(node, 'body') and isinstance(node.body, list):
            node.body = [self._remove_unused_assignments(child) for child in node.body if isinstance(child, Node)]

        if hasattr(node, 'value') and isinstance(node.value, Node):
            node.value = self._remove_unused_assignments(node.value)

        if hasattr(node, 'left') and isinstance(node.left, Node):
            node.left = self._remove_unused_assignments(node.left)

        if hasattr(node, 'right') and isinstance(node.right, Node):
            node.right = self._remove_unused_assignments(node.right)

        if hasattr(node, 'func') and isinstance(node.func, Node):
            node.func = self._remove_unused_assignments(node.func)

        if hasattr(node, 'test') and isinstance(node.test, Node):
            node.test = self._remove_unused_assignments(node.test)

        if hasattr(node, 'target') and isinstance(node.target, Node):
            node.target = self._remove_unused_assignments(node.target)

        if hasattr(node, 'iter') and isinstance(node.iter, Node):
            node.iter = self._remove_unused_assignments(node.iter)

        if hasattr(node, 'targets') and isinstance(node.targets, list):
            node.targets = [self._remove_unused_assignments(target) for target in node.targets if isinstance(target, Node)]

        if hasattr(node, 'args') and isinstance(node.args, list):
            node.args = [self._remove_unused_assignments(arg) for arg in node.args if isinstance(arg, Node)]

        return node


class ExpressionSimplificationPass(TransformPass):
    """Pass that simplifies expressions."""

    def __init__(self):
        super().__init__("expression_simplification")

    def transform(self, node: Node) -> Node:
        # Simplify x + 0 = x, x * 1 = x, etc.
        if isinstance(node, BinOp):
            if node.op == '+' and self._is_zero(node.right):
                return node.left
            elif node.op == '+' and self._is_zero(node.left):
                return node.right
            elif node.op == '*' and self._is_one(node.right):
                return node.left
            elif node.op == '*' and self._is_one(node.left):
                return node.right
            elif node.op == '-' and self._is_zero(node.right):
                return node.left

        return node

    def _is_zero(self, node: Node) -> bool:
        return isinstance(node, Constant) and node.value == 0

    def _is_one(self, node: Node) -> bool:
        return isinstance(node, Constant) and node.value == 1


class VariableRenamingPass(TransformPass):
    """Pass that renames variables."""

    def __init__(self, old_name: str, new_name: str):
        super().__init__(f"rename_{old_name}_to_{new_name}")
        self.old_name = old_name
        self.new_name = new_name

    def transform(self, node: Node) -> Node:
        if hasattr(node, 'id') and node.id == self.old_name:
            node.id = self.new_name
        return node


class FunctionInliningPass(TransformPass):
    """Pass that inlines simple functions."""

    def __init__(self):
        super().__init__("function_inlining")
        self.function_defs: Dict[str, Node] = {}

    def transform(self, node: Node) -> Node:
        if isinstance(node, Program):
            # Collect function definitions
            self.function_defs = {}
            for child in node.body:
                if isinstance(child, FunctionDef):
                    self.function_defs[child.name] = child

            # Transform body
            node.body = [self.transform(child) for child in node.body]
            return node

        elif isinstance(node, Call):
            if isinstance(node.func, Name) and node.func.id in self.function_defs:
                func_def = self.function_defs[node.func.id]
                if self._is_simple_function(func_def):
                    # Inline the function
                    return self._inline_function(func_def, node.args)

        return node

    def _is_simple_function(self, func_def: FunctionDef) -> bool:
        """Check if function is simple enough to inline."""
        return len(func_def.body) == 1 and isinstance(func_def.body[0], Return)

    def _inline_function(self, func_def: FunctionDef, args: List[Node]) -> Node:
        """Inline a simple function."""
        return_statement = func_def.body[0]
        if isinstance(return_statement, Return) and return_statement.value:
            # Simple substitution for now - TODO: implement proper argument substitution
            return return_statement.value


class Transformer:
    """Main transformation engine that applies passes in sequence."""

    def __init__(self):
        self.passes: List[TransformPass] = []

    def add_pass(self, pass_instance: TransformPass):
        """Add a transformation pass."""
        self.passes.append(pass_instance)

    def transform(self, tree: Node) -> Node:
        """Apply all transformation passes to the tree."""
        result = tree
        for pass_instance in self.passes:
            try:
                result = self._apply_pass(result, pass_instance)
            except Exception as e:
                raise TransformError(f"Transformation failed in pass '{pass_instance.name}': {str(e)}")
        return result

    def _apply_pass(self, node: Node, pass_instance: TransformPass) -> Node:
        """Apply a single pass to a node and its children."""
        if not pass_instance.should_transform(node):
            return node

        # Transform the current node
        try:
            transformed_node = pass_instance.transform(node)
        except Exception as e:
            raise TransformError(f"Failed to transform node {node.node_type.value}: {str(e)}")

        # Recursively transform child nodes
        if hasattr(transformed_node, 'body') and isinstance(transformed_node.body, list):
            transformed_node.body = [
                self._apply_pass(child, pass_instance) if isinstance(child, Node) else child
                for child in transformed_node.body
            ]

        if hasattr(transformed_node, 'value') and isinstance(transformed_node.value, Node):
            transformed_node.value = self._apply_pass(transformed_node.value, pass_instance)

        if hasattr(transformed_node, 'left') and isinstance(transformed_node.left, Node):
            transformed_node.left = self._apply_pass(transformed_node.left, pass_instance)

        if hasattr(transformed_node, 'right') and isinstance(transformed_node.right, Node):
            transformed_node.right = self._apply_pass(transformed_node.right, pass_instance)

        if hasattr(transformed_node, 'func') and isinstance(transformed_node.func, Node):
            transformed_node.func = self._apply_pass(transformed_node.func, pass_instance)

        if hasattr(transformed_node, 'test') and isinstance(transformed_node.test, Node):
            transformed_node.test = self._apply_pass(transformed_node.test, pass_instance)

        if hasattr(transformed_node, 'target') and isinstance(transformed_node.target, Node):
            transformed_node.target = self._apply_pass(transformed_node.target, pass_instance)

        if hasattr(transformed_node, 'iter') and isinstance(transformed_node.iter, Node):
            transformed_node.iter = self._apply_pass(transformed_node.iter, pass_instance)

        if hasattr(transformed_node, 'targets') and isinstance(transformed_node.targets, list):
            transformed_node.targets = [
                self._apply_pass(target, pass_instance) if isinstance(target, Node) else target
                for target in transformed_node.targets
            ]

        if hasattr(transformed_node, 'args') and isinstance(transformed_node.args, list):
            transformed_node.args = [
                self._apply_pass(arg, pass_instance) if isinstance(arg, Node) else arg
                for arg in transformed_node.args
            ]

        if hasattr(transformed_node, 'orelse') and isinstance(transformed_node.orelse, list):
            transformed_node.orelse = [
                self._apply_pass(child, pass_instance) if isinstance(child, Node) else child
                for child in transformed_node.orelse
            ]

        if hasattr(transformed_node, 'handlers') and isinstance(transformed_node.handlers, list):
            transformed_node.handlers = [
                self._apply_pass(handler, pass_instance) if isinstance(handler, Node) else handler
                for handler in transformed_node.handlers
            ]

        if hasattr(transformed_node, 'finalbody') and isinstance(transformed_node.finalbody, list):
            transformed_node.finalbody = [
                self._apply_pass(child, pass_instance) if isinstance(child, Node) else child
                for child in transformed_node.finalbody
            ]

        return transformed_node

    def pipeline(self, *passes: TransformPass) -> 'Transformer':
        """Create a pipeline with the given passes."""
        for pass_instance in passes:
            self.add_pass(pass_instance)
        return self

    def optimize(self, tree: Node) -> Node:
        """Apply common optimizations."""
        self.passes.clear()
        self.add_pass(ConstantFoldingPass())
        self.add_pass(ExpressionSimplificationPass())
        self.add_pass(DeadCodeEliminationPass())
        self.add_pass(UnusedVariableRemovalPass())
        return self.transform(tree)

    def get_pass_by_name(self, name: str) -> Optional[TransformPass]:
        """Get a pass by name."""
        for pass_instance in self.passes:
            if pass_instance.name == name:
                return pass_instance
        return None

    def remove_pass(self, name: str) -> bool:
        """Remove a pass by name."""
        for i, pass_instance in enumerate(self.passes):
            if pass_instance.name == name:
                del self.passes[i]
                return True
        return False

    def clear_passes(self):
        """Clear all passes."""
        self.passes.clear()

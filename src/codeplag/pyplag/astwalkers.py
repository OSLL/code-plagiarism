import ast
from contextlib import suppress

from typing_extensions import Self

from codeplag.pyplag.const import IGNORE_NODES, KEYWORDS, LITERALS, OPERATORS, TO_TOKEN
from codeplag.types import ASTFeatures, NodeCodePlace, NodeStructurePlace


class ASTWalker(ast.NodeVisitor):
    def __init__(self: Self, features: ASTFeatures) -> None:
        self.features = features
        self.curr_depth = 0

    def add_unique_node(self: Self, node_name: str) -> None:
        self.features.unodes[node_name] = self.features.count_unodes
        self.features.from_num[self.features.count_unodes] = node_name
        self.features.count_unodes += 1

    def __get_actual_name_from_node(self: Self, node: ast.AST) -> str | None:
        # TODO: Also handle ast.Expr
        if isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            if isinstance(node.target, ast.Name):
                return node.target.id
            elif isinstance(node.target, ast.Attribute):
                target_id = getattr(node.target.value, "id", None)
                if target_id is None:
                    return
                return f"{target_id}.{node.target.attr}"
            elif isinstance(node.target, ast.Subscript):
                # TODO
                ...
        elif isinstance(node, ast.Assign):
            target = None
            with suppress(IndexError):
                target = node.targets[0]
            if target is None:
                return
            if isinstance(target, ast.Name):
                return target.id

    def add_node_to_structure(self: Self, node: ast.AST, node_name: str) -> None:
        self.features.structure.append(
            NodeStructurePlace(depth=self.curr_depth, uid=self.features.unodes[node_name])
        )
        if self.curr_depth == 1:
            actual_node_name = self.__get_actual_name_from_node(node)
            if actual_node_name is None:
                actual_node_name = node_name
            self.features.head_nodes.append(f"{actual_node_name}[{node.lineno}]")  # type: ignore

    def generic_visit(self: Self, node: ast.AST) -> None:
        """Traverses, counts operators, keywords, and literals, and saves sequence of operators.

        Args:
        ----
            node (ast.AST): current node.

        """
        type_name = type(node).__name__
        if type_name in TO_TOKEN:
            self.features.tokens.append(TO_TOKEN[type_name])
            if "lineno" in dir(node) and "col_offset" in dir(node):
                self.features.tokens_pos.append(
                    NodeCodePlace(lineno=node.lineno, col_offset=node.col_offset)  # type: ignore
                )
            else:
                self.features.tokens_pos.append(self.features.tokens_pos[-1])

        if type_name in OPERATORS:
            self.features.operators[type_name] += 1
        elif type_name in KEYWORDS:
            self.features.keywords[type_name] += 1
        elif type_name in LITERALS:
            self.features.literals[type_name] += 1

        if type_name not in IGNORE_NODES:
            if self.curr_depth != 0:
                name = getattr(node, "name", None)
                if name is not None:
                    if name not in self.features.unodes:
                        self.add_unique_node(name)
                    self.add_node_to_structure(node, name)
                else:
                    if type_name not in self.features.unodes:
                        self.add_unique_node(type_name)
                    self.add_node_to_structure(node, type_name)
                self.features.count_of_nodes += 1

            self.curr_depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.curr_depth -= 1

import ast
from contextlib import suppress

from codeplag.pyplag.const import IGNORE_NODES, KEYWORDS, LITERALS, OPERATORS, TO_TOKEN
from codeplag.types import ASTFeatures, NodeCodePlace, NodeStructurePlace


class ASTWalker(ast.NodeVisitor):
    def __init__(self, features: ASTFeatures) -> None:
        self.features = features
        self.curr_depth = 0

    def add_unique_node(self, node_name: str) -> None:
        self.features.unodes[node_name] = self.features.count_unodes
        self.features.from_num[self.features.count_unodes] = node_name
        self.features.count_unodes += 1

    def __get_actual_name_from_node(self, node: ast.AST) -> str | None:
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

    def add_node_to_structure(self, node: ast.AST, node_name: str) -> None:
        self.features.structure.append(
            NodeStructurePlace(
                depth=self.curr_depth, uid=self.features.unodes[node_name]
            )
        )
        if self.curr_depth == 1:
            actual_node_name = self.__get_actual_name_from_node(node)
            if actual_node_name is None:
                actual_node_name = node_name
            self.features.head_nodes.append(f"{actual_node_name}[{node.lineno}]")

    def generic_visit(self, node: ast.AST) -> None:
        """Function for traverse, counting operators, keywords, literals
        and save sequence of operators.

        Args:
        ----
            node - current node

        """
        type_name = type(node).__name__
        if type_name in TO_TOKEN:
            self.features.tokens.append(TO_TOKEN[type_name])
            if "lineno" in dir(node) and "col_offset" in dir(node):
                self.features.tokens_pos.append(
                    NodeCodePlace(lineno=node.lineno, col_offset=node.col_offset)
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


# YAGNI
class Visitor(ast.NodeVisitor):
    def __init__(self, write_tree=False):
        self.depth = 0
        self.count_of_nodes = 0
        self.write_tree = write_tree

    def generic_visit(self, node):
        """Function for traverse tree and print it in console.

        Args:
        ----
            node - current node

        """
        type_node = type(node).__name__
        if type_node not in IGNORE_NODES:
            if self.depth != 0:
                self.count_of_nodes += 1
            if self.write_tree:
                print("-" * self.depth + type(node).__name__, self.count_of_nodes)
            self.depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1


# YAGNI
class NodeGetter(ast.NodeVisitor):
    def __init__(self):
        self.depth = 0
        self.nodes = []

    def visit(self, node):
        """Function for visiting node's children.

        Args:
        ----
            node - current node

        """
        if self.depth > 1:
            return
        self.generic_visit(node)

    def generic_visit(self, node):
        """Function for traverse and print in console names of all node's children.

        Args:
        ----
            node - current node

        """
        type_node = type(node).__name__
        if type_node not in IGNORE_NODES:
            if self.depth == 1:
                self.nodes.append(node)

            self.depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1

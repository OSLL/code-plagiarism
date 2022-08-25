import ast

from codeplag.astfeatures import ASTFeatures
from codeplag.pyplag.const import (IGNORE_NODES, KEYWORDS, LITERALS, OPERATORS,
                                   TO_TOKEN)


class ASTWalker(ast.NodeVisitor):

    def __init__(self, features: ASTFeatures) -> None:
        self.features = features
        self.curr_depth = 0

    def add_unique_node(self, node_name: str) -> None:
        self.features.unodes[node_name] = self.features.count_unodes
        self.features.from_num[self.features.count_unodes] = node_name
        self.features.count_unodes += 1

    def add_node_to_structure(self, node_name: str) -> None:
        self.features.structure.append(
            (self.curr_depth, self.features.unodes[node_name])
        )
        if self.curr_depth == 1:
            self.features.head_nodes.append(node_name)

    def generic_visit(self, node: ast.AST) -> None:
        '''
            Function for traverse, counting operators, keywords, literals
            and save sequence of operators
            @param node - current node
        '''
        type_name = type(node).__name__
        if type_name in TO_TOKEN:
            self.features.tokens.append(TO_TOKEN[type_name])
            if 'lineno' in dir(node) and 'col_offset' in dir(node):
                self.features.tokens_pos.append(
                    (node.lineno, node.col_offset)
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
                if 'name' in dir(node) and node.name is not None:
                    if node.name not in self.features.unodes:
                        self.add_unique_node(node.name)
                    self.add_node_to_structure(node.name)
                else:
                    if type_name not in self.features.unodes:
                        self.add_unique_node(type_name)
                    self.add_node_to_structure(type_name)
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
        '''
            Function for traverse tree and print it in console
            @param node - current node
        '''
        type_node = (type(node).__name__)
        if type_node not in IGNORE_NODES:
            if self.depth != 0:
                self.count_of_nodes += 1
            if self.write_tree:
                print('-' * self.depth + type(node).__name__,
                      self.count_of_nodes)
            self.depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1


# YAGNI
class NodeGetter(ast.NodeVisitor):
    def __init__(self):
        self.depth = 0
        self.nodes = []

    def visit(self, node):
        '''
            Function for visiting node's children
            @param node - current node
        '''
        if self.depth > 1:
            return
        self.generic_visit(node)

    def generic_visit(self, node):
        '''
            Function for traverse and print in console names of all
            node's children
            @param node - current node
        '''
        type_node = (type(node).__name__)
        if type_node not in IGNORE_NODES:
            if self.depth == 1:
                self.nodes.append(node)

            self.depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1

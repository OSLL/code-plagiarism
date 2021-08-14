import ast
from numba.typed import List, Dict
from numba.core import types

from codeplag.pyplag.const import (
    IGNORE_NODES, OPERATORS,
    KEYWORDS, LITERALS,
    TO_TOKEN
)


# Можно сохранять название узлов только самого верхнего, первого уровня,
# чтобы экономить ресурсы
class ASTWalker(ast.NodeVisitor):
    def __init__(self):
        self.curr_depth = 0
        self.count_of_nodes = 0
        self.seq_ops = List().empty_list(types.unicode_type)
        self.operators = Dict.empty(key_type=types.unicode_type,
                                    value_type=types.int64)
        self.keywords = Dict.empty(key_type=types.unicode_type,
                                   value_type=types.int64)
        self.literals = Dict.empty(key_type=types.unicode_type,
                                   value_type=types.int64)
        # uniq nodes
        self.unodes = Dict.empty(key_type=types.unicode_type,
                                 value_type=types.int64)
        self.from_num = Dict.empty(key_type=types.int64,
                                   value_type=types.unicode_type)
        # count of uniq nodes
        self.cunodes = 0
        self.structure = List([(1, 2)])
        self.structure.clear()
        self.tokens = List().empty_list(types.int64)

    def generic_visit(self, node):
        '''
            Function for traverse, counting operators, keywords, literals
            and save sequence of operators
            @param node - current node
        '''
        type_name = type(node).__name__
        if type_name in TO_TOKEN:
            self.tokens.append(TO_TOKEN[type_name])

        if type_name in OPERATORS:
            if type_name not in self.operators:
                self.operators[type_name] = 1
            else:
                self.operators[type_name] += 1
            self.seq_ops.append(type_name)
        elif type_name in KEYWORDS:
            if type_name not in self.keywords:
                self.keywords[type_name] = 1
            else:
                self.keywords[type_name] += 1
        elif type_name in LITERALS:
            if type_name not in self.literals:
                self.literals[type_name] = 1
            else:
                self.literals[type_name] += 1

        if type_name not in IGNORE_NODES:
            if self.curr_depth != 0:
                if 'name' in dir(node) and node.name is not None:
                    if node.name not in self.unodes:
                        self.unodes[node.name] = self.cunodes
                        self.from_num[self.cunodes] = node.name
                        self.cunodes += 1
                    self.structure.append((self.curr_depth,
                                           self.unodes[node.name]))
                else:
                    if type_name not in self.unodes:
                        self.unodes[type_name] = self.cunodes
                        self.from_num[self.cunodes] = type_name
                        self.cunodes += 1
                    self.structure.append((self.curr_depth,
                                           self.unodes[type_name]))
                self.count_of_nodes += 1

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

            # Будет ли работать, если эти три строки заккоментировать?
            self.depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1

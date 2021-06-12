import context

import ast
import numpy as np
import numba
from numba import njit
from numba.typed import List, Dict
from numba.core import types

from src.pyplag.const import IGNORE_NODES, OPERATORS, KEYWORDS, LITERALS


# Можно сохранять название узлов только самого верхнего, первого уровня,
# чтобы экономить ресурсы
class ASTFeatures(ast.NodeVisitor):
    def __init__(self):
        self.curr_depth = numba.int32(0)
        self.count_of_nodes = numba.int32(0)
        self.seq_ops = List(['tmp'])
        self.seq_ops.clear()
        self.operators = Dict.empty(key_type=types.unicode_type,
                                    value_type=types.int32)
        self.keywords = Dict.empty(key_type=types.unicode_type,
                                   value_type=types.int32)
        self.literals = Dict.empty(key_type=types.unicode_type,
                                   value_type=types.int32)
        # uniq nodes
        self.unodes = Dict.empty(key_type=types.unicode_type,
                                 value_type=types.int32)
        self.from_num = Dict.empty(key_type=types.int32,
                                   value_type=types.unicode_type)
        # count of uniq nodes
        self.cunodes = numba.int32(0)
        self.structure = List([(1, 2)])
        self.structure.clear()

    def generic_visit(self, node):
        '''
            Function for traverse, counting operators, keywords, literals
            and save sequence of operators
            @param node - current node
        '''
        type_name = type(node).__name__
        if type_name in OPERATORS:
            if type_name not in self.operators:
                self.operators[type_name] = numba.int32(1)
            else:
                self.operators[type_name] += numba.int32(1)
            self.seq_ops.append(type_name)
        elif type_name in KEYWORDS:
            if type_name not in self.keywords:
                self.keywords[type_name] = numba.int32(1)
            else:
                self.keywords[type_name] += numba.int32(1)
        elif type_name in LITERALS:
            if type_name not in self.literals:
                self.literals[type_name] = numba.int32(1)
            else:
                self.literals[type_name] += numba.int32(1)

        if type_name not in IGNORE_NODES:
            if self.curr_depth != 0:
                if 'name' in dir(node) and node.name is not None:
                    if node.name not in self.unodes:
                        self.unodes[node.name] = self.cunodes
                        self.from_num[self.cunodes] = node.name
                        self.cunodes += numba.int32(1)
                    self.structure.append((self.curr_depth,
                                           self.unodes[node.name]))
                else:
                    if type_name not in self.unodes:
                        self.unodes[type_name] = self.cunodes
                        self.from_num[self.cunodes] = type_name
                        self.cunodes += numba.int32(1)
                    self.structure.append((self.curr_depth,
                                           self.unodes[type_name]))
                self.count_of_nodes += 1
            self.curr_depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.curr_depth -= 1


@njit(fastmath=True)
def get_children_ind(tree, count_of_nodes):
    count_of_children = 0
    if count_of_nodes == 0:
        return None, count_of_children

    ind = List([0])
    count_of_children = 1
    curr_level = tree[0][0]
    for i in np.arange(1, count_of_nodes, 1):
        if curr_level == tree[i][0]:
            ind.append(i)
            count_of_children += 1

    return ind, count_of_children


# YAGNI
class OpKwCounter(ast.NodeVisitor):
    def __init__(self):
        self.seq_ops = List(['tmp'])
        self.seq_ops.clear()
        self.operators = {}
        self.keywords = {}
        self.literals = {}

    def generic_visit(self, node):
        '''
            Function for traverse, counting operators, keywords, literals
            and save sequence of operators
            @param node - current node
        '''
        type_name = type(node).__name__
        if type_name in OPERATORS:
            if type_name not in self.operators.keys():
                self.operators[type_name] = 1
            else:
                self.operators[type_name] += 1
            self.seq_ops.append(type_name)
        elif type_name in KEYWORDS:
            if type_name not in self.keywords.keys():
                self.keywords[type_name] = 1
            else:
                self.keywords[type_name] += 1
        elif type_name in LITERALS:
            if type_name not in self.literals.keys():
                self.literals[type_name] = 1
            else:
                self.literals[type_name] += 1
        ast.NodeVisitor.generic_visit(self, node)


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


# Tested
# YAGNI
def get_count_of_nodes(tree):
    '''
        Get count of nodes of tree without head
        @param tree - One of the nodes of the AST type whose count of nodes
        we want to receive
    '''
    if not isinstance(tree, ast.AST):
        return TypeError

    traverser = Visitor()
    traverser.visit(tree)
    return traverser.count_of_nodes

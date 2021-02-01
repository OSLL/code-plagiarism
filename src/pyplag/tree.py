from context import *

import ast
import os
import numpy as np

from src.pyplag.const import *

class OpKwCounter(ast.NodeVisitor):
    def __init__(self):
        self.seq_ops = []
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


def get_AST(filename):
    '''
        Function return ast which has type ast.Module
        @param filename - full path to file with code which will have
        analyzed
    '''
    if type(filename) is not str:
        return TypeError

    if not os.path.isfile(filename):
        print(filename, "Is not a file / doesn't exist")
        return None

    tree = None
    with open(filename) as f:
        tree = ast.parse(f.read())

    return tree

    # Tested
def get_nodes(tree):
    '''
        Function return all tree's nodes
        @param tree - One of the nodes of the AST type whose nodes we
        want to receive
    '''
    if not isinstance(tree, ast.AST):
        return TypeError

    traverser = NodeGetter()
    traverser.visit(tree)
    return traverser.nodes


# Tested
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


# Tested
def find_max_index(array, len1, len2):
    '''
        Function for finding index of max element in matrix
        @param array - matrix of compliance (np.ndarray object)
        @param len1 - number of nodes in children1
        @param len2 - number of nodes in children2
    '''
    if (not isinstance(array, np.ndarray) or type(len1) is not int
       or type(len2) is not int):
        return TypeError

    if array.shape[0] != len1 or array.shape[1] != len2:
        return IndexError

    maximum = 0
    index = (0, 0)
    for i in range(len1):
        for j in range(len2):
            if array[i][j][1] == 0:
                continue
            value = array[i][j][0] / array[i][j][1]
            if value > maximum:
                maximum = value
                index = (i, j)

    return index


def getn_count_nodes(len_min, len_max, indexes, axis, children):
    '''
        Function return count of not accounted nodes
        @param len_min - length of less node
        @param len_max - length of longer node
        @param indexes - indexes of metrics taken into account list of tuples
        @param axis - if 0 then iteration on row
        if 1 then iteration on column
        @param children - list of nodes of type ast
    '''
    add = [indexes[i][axis] for i in range(len_min)]

    count = 0
    for i in range(len_max):
        if i not in add:
            count += get_count_of_nodes(children[i]) + 1

    return count
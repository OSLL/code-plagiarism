import context

import numpy as np
import numba
import ast

from numba import njit
from numba.typed import List
from src.pyplag.const import IGNORE_NODES
from src.pyplag.tfeatures import get_count_of_nodes


# Tested
@njit(fastmath=True)
def find_max_index(array):
    '''
        Function for finding index of max element in matrix
        @param array - matrix of compliance (np.ndarray object)
    '''
    # if (not isinstance(array, np.ndarray) or type(len1) is not int
    #    or type(len2) is not int):
    #    return TypeError

    maximum = 0
    index = numba.int32([0, 0])
    for i in np.arange(0, array.shape[0], 1):
        for j in np.arange(0, array.shape[1], 1):
            if array[i][j][1] == 0:
                continue
            value = array[i][j][0] / array[i][j][1]
            if value > maximum:
                maximum = value
                index[0] = i
                index[1] = j

    return index


@njit(fastmath=True)
def matrix_value(array):
    same_struct_metric = [1, 1]
    minimal = min(array.shape[0], array.shape[1])
    indexes = List()
    for i in np.arange(0, minimal, 1):
        ind = find_max_index(array)
        indexes.append(ind)
        same_struct_metric[0] += array[ind[0]][ind[1]][0]
        same_struct_metric[1] += array[ind[0]][ind[1]][1]

        for i in np.arange(0, array.shape[1], 1):
            array[ind[0]][i] = [0, 0]
        for j in np.arange(0, array.shape[0], 1):
            array[j][ind[1]] = [0, 0]

    return same_struct_metric, indexes


@njit(fastmath=True)
def get_from_tree(tree, start, finish):
    return tree[start:finish]


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


# Tested
# YAGNI
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


# YAGNI
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
    added = [indexes[i][axis] for i in np.arange(0, len_min, 1)]

    count = 0
    for i in np.arange(0, len_max, 1):
        if i not in added:
            count += get_count_of_nodes(children[i]) + 1

    return count

import numpy as np
import ast

from codeplag.pyplag.const import IGNORE_NODES
from codeplag.pyplag.tfeatures import get_count_of_nodes


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

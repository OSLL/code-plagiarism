import os
from clang.cindex import Cursor
from codeplag.cplag.const import IGNORE

# Tested
def get_not_ignored(tree, src):
    '''
        Function helps to discard unnecessary nodes such as imports
        @param tree - clang.cindex.Cursor object
        @param src - str path to file
    '''

    if(type(tree) is not Cursor or type(src) is not str):
        return TypeError

    elif (not os.path.isfile(src)):
        return FileNotFoundError

    children = list(tree.get_children())
    length = len(children)
    parsed_nodes = []
    for i in range(length):
        loc = children[i].location.file
        if (str(loc).split('/')[-1] == src.split('/')[-1]
           and children[i].kind not in IGNORE):
            parsed_nodes.append(children[i])

    if(len(parsed_nodes) > 0):
        return parsed_nodes
    return None


# Tested
def get_count_of_nodes(tree):
    '''
        Get count of nodes of tree without head
        @param tree - clang.cindex.Cursor object
    '''
    if(not hasattr(tree, 'get_children')):
        return TypeError

    count = 0
    children = list(tree.get_children())
    length = len(children)
    count += length
    for i in range(length):
        count += get_count_of_nodes(children[i])

    return count


def getn_count_nodes(len_min, len_max, indexes, axis, children):
    '''
        Function return count of not accounted nodes
        @param len_min - length of less node
        @param len_max - length of longer node
        @param indexes - indexes of metrics taken into account list of tuples
        @param axis - if 0 then iteration on row
        if 1 then iteration on column
        @param children - list of nodes of type clang.cindex.Cursor object
    '''
    add = [indexes[i][axis] for i in range(len_min)]

    count = 0
    for i in range(len_max):
        if i not in add:
            count += get_count_of_nodes(children[i]) + 1

    return count


def find_max_index(array, len1, len2):
    '''
        Function for finding index of max element in matrix
        @param array - matrix of compliance
        @param len1 - number of nodes in children1
        @param len2 - number of nodes in children2
    '''
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

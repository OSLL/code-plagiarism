from context import *

import ast
import pandas as pd
from numba import njit

from src.pyplag.tree import *

# Tested
def nodes_metric(res1, res2):
    '''
        Function return how same operators or keywords or literals
        in two trees
        @param res1 - dict object with counts of op or kw or lit
        @param res2 - dict object with counts of op or kw or lit
    '''
    if(type(res1) is not dict or type(res2) is not dict):
        return TypeError

    percent_of_same = [0, 0]
    for key in res1.keys():
        if key not in res2.keys():
            percent_of_same[1] += res1[key]
            continue
        percent_of_same[0] += min(res1[key],
                                  res2[key])
        percent_of_same[1] += max(res1[key],
                                  res2[key])
    for key in res2.keys():
        if key not in res1.keys():
            percent_of_same[1] += res2[key]
            continue

    if percent_of_same[1] == 0:
        return 0.0

    return percent_of_same[0] / percent_of_same[1]


def calculate_metric(children1, children2, len1, len2, array):
    '''
        Function calculate percent of compliance from matrix
        @param children1 - list of nodes of type ast object
        @param children2 - list of nodes of type ast object
        @param len1 - count of nodes in children1
        @param len2 - count of nodes in children2
        @param array - matrix of compliance
    '''
    same_struct_metric = [1, 1]
    indexes = []
    for i in range(min(len1, len2)):
        ind = find_max_index(array, len1, len2)
        indexes.append(ind)
        same_struct_metric[0] += array[ind][0]
        same_struct_metric[1] += array[ind][1]
        # same_struct_metric = [same_struct_metric[0] +
        #                       array[ind][0],
        #                       same_struct_metric[1] +
        #                       array[ind][1]]
        for i in range(len2):
            array[ind[0]][i] = [0, 0]
        for j in range(len1):
            array[j][ind[1]] = [0, 0]

    not_count = 0
    if len1 > len2:
        not_count = getn_count_nodes(len2, len1, indexes, 0, children1)
    elif len2 > len1:
        not_count = getn_count_nodes(len1, len2, indexes, 1, children2)

    same_struct_metric[1] += not_count
    # same_struct_metric = [same_struct_metric[0],
    #                       same_struct_metric[1] + not_count]

    return same_struct_metric


# Tested
def struct_compare(tree1, tree2, output=False):
    '''
        Function for compare structure of two trees
        @param tree1 - ast object
        @param tree2 - ast object
        @param output - if equal True, then in console prints matrix
        of compliance else not
    '''
    if (not isinstance(tree1, ast.AST) or not isinstance(tree2, ast.AST)
       or type(output) is not bool):
        return TypeError

    parsed_nodes1 = get_nodes(tree1)
    parsed_nodes2 = get_nodes(tree2)
    len1 = len(parsed_nodes1)
    len2 = len(parsed_nodes2)

    if (len1 == 0 and len2 == 0):
        return [1, 1]
    elif (len1 == 0):
        return [1, (get_count_of_nodes(tree2) + 1)]
    elif (len2 == 0):
        return [1, (get_count_of_nodes(tree1) + 1)]

    array = np.zeros((len1, len2), dtype=(np.int32, 2))
    if output:
        indexes = []
        columns = []

    for i in range(len1):
        if output:
            if 'name' in dir(parsed_nodes1[i]):
                indexes.append(parsed_nodes1[i].name)
            else:
                indexes.append(type(parsed_nodes1[i]).__name__)

        for j in range(len2):
            array[i][j] = struct_compare(parsed_nodes1[i],
                                         parsed_nodes2[j])

    if output:
        for j in range(len2):
            if 'name' in dir(parsed_nodes2[j]):
                columns.append(parsed_nodes2[j].name)
            else:
                columns.append(type(parsed_nodes2[j]).__name__)

        a = np.zeros((len1, len2), dtype=object)
        for i in range(len1):
            for j in range(len2):
                a[i][j] = '{:.2%}'.format(array[i][j][0] / array[i][j][1])

        table = pd.DataFrame(a, index=indexes, columns=columns)
        print()
        print(table)

    same_struct_metric = calculate_metric(parsed_nodes1,
                                          parsed_nodes2,
                                          len1,
                                          len2,
                                          array)

    if output:
        print()
        print('Structure is same by {:.2%}'.format(same_struct_metric[0] /
                                                   same_struct_metric[1]))
    return same_struct_metric


# Tested
@njit(fastmath=True)
def op_shift_metric(ops1, ops2):
    '''
        Returns the maximum value of the operator match and the shift under
        this condition
        @param ops1 - sequence of operators of tree1
        @param ops2 - sequence of operators of tree2
    '''
    #if (type(ops1) is not list or type(ops2) is not list):
     #   return TypeError

    count_el_f = len(ops1)
    count_el_s = len(ops2)
    if count_el_f > count_el_s:
        tmp = ops1
        ops1 = ops2
        ops2 = tmp
        count_el_f = len(ops1)
        count_el_s = len(ops2)

    y = np.zeros(count_el_s, dtype=np.float32)

    shift = 0
    while shift < count_el_s:
        counter = 0
        first_ind = 0
        second_ind = shift
        while first_ind < count_el_f and second_ind < count_el_s:
            if ops1[first_ind] == ops2[second_ind]:
                counter += 1
            first_ind += 1
            second_ind += 1
        count_all = count_el_f + count_el_s - counter
        if count_all != 0:
            y[shift] = counter / count_all

        shift += 1

    max_shift = 0
    for index in range(1, len(y)):
        if y[index] > y[max_shift]:
            max_shift = index

    if len(y) > 0:
        return max_shift, y[max_shift]
    else:
        return 0, 0.0
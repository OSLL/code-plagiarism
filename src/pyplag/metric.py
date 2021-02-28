from context import *

import ast
#import pandas as pd
import numba
from numba import njit
from numba.typed import List

from src.pyplag.tree import *

# Tested
@njit(fastmath=True)
def nodes_metric(res1, res2):
    '''
        Function return how same operators or keywords or literals
        in two trees
        @param res1 - dict object with counts of op or kw or list
        @param res2 - dict object with counts of op or kw or list
    '''
    #if(type(res1) is not dict or type(res2) is not dict):
     #   return TypeError

    percent_of_same = [0, 0]
    for key in res1.keys():
        if key not in res2:
            percent_of_same[1] += res1[key]
            continue
        percent_of_same[0] += min(res1[key],
                                  res2[key])
        percent_of_same[1] += max(res1[key],
                                  res2[key])
    for key in res2.keys():
        if key not in res1:
            percent_of_same[1] += res2[key]
            continue

    if percent_of_same[1] == 0:
        return 0.0

    return percent_of_same[0] / percent_of_same[1]


@njit(fastmath=True)
def matrix_value(array):
    same_struct_metric = [1, 1]
    minimal = min(array.shape[0], array.shape[1])
    indexes = List()
    for i in range(minimal):
        ind = find_max_index(array)
        indexes.append(ind)
        same_struct_metric[0] += array[ind[0]][ind[1]][0]
        same_struct_metric[1] += array[ind[0]][ind[1]][1]

        for i in range(array.shape[1]):
            array[ind[0]][i] = [0, 0]
        for j in range(array.shape[0]):
            array[j][ind[1]] = [0, 0]

    return same_struct_metric, indexes


# Tested
@njit(fastmath=True)
def struct_compare(tree1, tree2, output=False):
    '''
        Function for compare structure of two trees
        @param tree1 - ast object
        @param tree2 - ast object
        @param output - if equal True, then in console prints matrix
        of compliance else not
    '''
    #if (not isinstance(tree1, ast.AST) or not isinstance(tree2, ast.AST)
     #  or type(output) is not bool):
      #  return TypeError

    count_of_nodes1 = len(tree1)
    count_of_nodes2 = len(tree2)
    ch_inds1, count_of_children1 = get_children_ind(tree1, count_of_nodes1)
    ch_inds2, count_of_children2 = get_children_ind(tree2, count_of_nodes2)

    if (count_of_children1 == 0 and count_of_children2 == 0):
        return [1, 1]
    elif (count_of_children1 == 0):
        return [1, (count_of_nodes2 + 1)]
    elif (count_of_children2 == 0):
        return [1, (count_of_nodes1 + 1)]

    array = np.zeros((count_of_children1, count_of_children2, 2), dtype=numba.int32)
    if output:
        indexes = List()
        columns = List()

    for i in range(count_of_children1 - 1):
        if output:
            indexes.append(tree1[ch_inds1[i]].split(" ")[1])

        for j in range(count_of_children2 - 1):
            section1 = get_from_tree(tree1, ch_inds1[i] + 1, ch_inds1[i + 1])
            section2 = get_from_tree(tree2, ch_inds2[j] + 1, ch_inds2[j + 1])
            array[i][j] = struct_compare(section1,
                                         section2)

    last_ind1 = ch_inds1[-1]
    last_ind2 = ch_inds2[-1]
    for j in range(count_of_children2 - 1):
        if output:
            columns.append(tree2[ch_inds2[j]].split(" ")[1])
        section1 = get_from_tree(tree1, ch_inds1[-1] + 1, count_of_nodes1)
        section2 = get_from_tree(tree2, ch_inds2[j] + 1, ch_inds2[j + 1])
        array[count_of_children1 - 1][j] = struct_compare(section1,
                                                          section2)

    for i in range(count_of_children1 - 1):
        section1 = get_from_tree(tree1, ch_inds1[i] + 1, ch_inds1[i + 1])
        section2 = get_from_tree(tree2, ch_inds2[-1] + 1, count_of_nodes2)
        array[i][count_of_children2 - 1] = struct_compare(section1,
                                                          section2)

    section1 = get_from_tree(tree1, ch_inds1[-1] + 1, count_of_nodes1)
    section2 = get_from_tree(tree2, ch_inds2[-1] + 1, count_of_nodes2)
    array[count_of_children1 - 1][count_of_children2 - 1] = struct_compare(section1,
                                                                           section2)

    if output:
        indexes.append(tree1[ch_inds1[-1]].split(" ")[1])
        columns.append(tree2[ch_inds2[-1]].split(" ")[1])

        #a = np.zeros((count_of_children1, count_of_children2), dtype=object)
        #for i in range(count_of_children1):
         #   for j in range(count_of_children2):
          #      a[i][j] = '{:.2%}'.format(array[i][j][0] / array[i][j][1])

        #table = pd.DataFrame(a, index=indexes, columns=columns)
        print()
        print(array)
        #print(table)

    same_struct_metric, indexes = matrix_value(array)
    if count_of_children1 > count_of_children2:
        added = [indexes[i][0] for i in range(count_of_children2)]
        for k in range(count_of_children1 - 1):
            if k in added:
                continue
            else:
                same_struct_metric[1] += len(tree1[ch_inds1[k]:ch_inds1[k + 1]])
        if (count_of_children1 - 1) in added:
            pass
        else:
            same_struct_metric[1] += len(tree1[ch_inds1[-1]:count_of_nodes1])
    elif count_of_children2 > count_of_children1:
        added = [indexes[i][1] for i in range(count_of_children1)]
        for k in range(count_of_children2 - 1):
            if k in added:
                continue
            else:
                same_struct_metric[1] += len(tree2[ch_inds2[k]:ch_inds2[k + 1]])
        if (count_of_children2 - 1) in added:
            pass
        else:
            same_struct_metric[1] += len(tree2[ch_inds2[-1]:count_of_nodes2])

    if output:
        print()
        #print('Structure is same by {:.2%}'.format(same_struct_metric[0] /
         #                                          same_struct_metric[1]))

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
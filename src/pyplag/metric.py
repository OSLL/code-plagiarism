import context

import numpy as np
from numba import njit

from src.pyplag.tfeatures import get_children_ind, generate_unique_ngrams
from src.pyplag.other import get_from_tree, matrix_value


@njit(fastmath=True)
def counter_metric(counter1, counter2):
    '''
        Function return how same operators or keywords or literals
        in two trees
        @param counter1 - dict object with counts of op or kw or list
        @param counter2 - dict object with counts of op or kw or list
    '''
    # if(type(counter1) is not dict or type(counter2) is not dict):
    #    return TypeError

    if len(counter1) == 0 and len(counter2) == 0:
        return 1.0

    percent_of_same = [0, 0]
    for key in counter1.keys():
        if key not in counter2:
            percent_of_same[1] += counter1[key]
            continue
        percent_of_same[0] += min(counter1[key],
                                  counter2[key])
        percent_of_same[1] += max(counter1[key],
                                  counter2[key])
    for key in counter2.keys():
        if key not in counter1:
            percent_of_same[1] += counter2[key]
            continue

    if percent_of_same[1] == 0:
        return 0.0

    return percent_of_same[0] / percent_of_same[1]


@njit(fastmath=True)
def struct_compare(tree1, tree2, matrix=np.array([[[]]]), dtype=np.int64):
    '''
        Function for compare structure of two trees
        @param tree1 - ast object
        @param tree2 - ast object
        @param output - if equal True, then in console prints matrix
        of compliance else not
    '''
    # if (not isinstance(tree1, ast.AST) or not isinstance(tree2, ast.AST)
    #   or type(output) is not bool):
    #   return TypeError

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

    array = np.zeros((count_of_children1, count_of_children2, 2),
                     dtype=np.int64)

    for i in np.arange(0, count_of_children1 - 1, 1):
        for j in np.arange(0, count_of_children2 - 1, 1):
            section1 = get_from_tree(tree1, ch_inds1[i] + 1, ch_inds1[i + 1])
            section2 = get_from_tree(tree2, ch_inds2[j] + 1, ch_inds2[j + 1])
            array[i][j] = struct_compare(section1,
                                         section2)

    for j in np.arange(0, count_of_children2 - 1, 1):
        section1 = get_from_tree(tree1, ch_inds1[-1] + 1, count_of_nodes1)
        section2 = get_from_tree(tree2, ch_inds2[j] + 1, ch_inds2[j + 1])
        array[count_of_children1 - 1][j] = struct_compare(section1,
                                                          section2)

    for i in np.arange(0, count_of_children1 - 1, 1):
        section1 = get_from_tree(tree1, ch_inds1[i] + 1, ch_inds1[i + 1])
        section2 = get_from_tree(tree2, ch_inds2[-1] + 1, count_of_nodes2)
        array[i][count_of_children2 - 1] = struct_compare(section1,
                                                          section2)

    section1 = get_from_tree(tree1, ch_inds1[-1] + 1, count_of_nodes1)
    section2 = get_from_tree(tree2, ch_inds2[-1] + 1, count_of_nodes2)
    array[count_of_children1 - 1][count_of_children2 - 1] = struct_compare(section1,
                                                                           section2)

    if matrix.size != 0:
        for i in np.arange(0, count_of_children1, 1):
            for j in np.arange(0, count_of_children2, 1):
                matrix[i][j] = array[i][j]

    same_struct_metric, indexes = matrix_value(array)
    if count_of_children1 > count_of_children2:
        added = [indexes[i][0] for i in np.arange(0, count_of_children2, 1)]
        for k in np.arange(0, count_of_children1 - 1, 1):
            if k in added:
                continue
            else:
                same_struct_metric[1] += len(tree1[ch_inds1[k]:ch_inds1[k + 1]])
        if (count_of_children1 - 1) in added:
            pass
        else:
            same_struct_metric[1] += len(tree1[ch_inds1[-1]:count_of_nodes1])
    elif count_of_children2 > count_of_children1:
        added = [indexes[i][1] for i in np.arange(0, count_of_children1, 1)]
        for k in np.arange(0, count_of_children2 - 1, 1):
            if k in added:
                continue
            else:
                same_struct_metric[1] += len(tree2[ch_inds2[k]:ch_inds2[k + 1]])
        if (count_of_children2 - 1) in added:
            pass
        else:
            same_struct_metric[1] += len(tree2[ch_inds2[-1]:count_of_nodes2])

    return same_struct_metric


@njit(fastmath=True)
def op_shift_metric(ops1, ops2):
    '''
        Returns the maximum value of the operator match and the shift under
        this condition
        @param ops1 - sequence of operators of tree1
        @param ops2 - sequence of operators of tree2
    '''
    # if (type(ops1) is not list or type(ops2) is not list):
    #    return TypeError
    count_el_f = len(ops1)
    count_el_s = len(ops2)
    if count_el_f == 0 and count_el_s == 0:
        return 0, 1.0
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
    for index in np.arange(1, len(y), 1):
        if y[index] > y[max_shift]:
            max_shift = index

    if len(y) > 0:
        return max_shift, y[max_shift]
    else:
        return 0, 0.0


def value_jakkar_coef(tokens_first, tokens_second):
    ngrams_first = generate_unique_ngrams(tokens_first, 3)
    ngrams_second = generate_unique_ngrams(tokens_second, 3)

    intersection = len(ngrams_first.intersection(ngrams_second))
    union = len(ngrams_first | ngrams_second)

    if union == 0:
        return 0.0

    return intersection / union


@njit(fastmath=True)
def lcs(X, Y):
    m = len(X)
    n = len(Y)

    if m == 0 or n == 0:
        return 0

    # m + 1 строк
    # n + 1 столбцов
    L = [[0] * (n + 1) for i in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    return L[m][n]

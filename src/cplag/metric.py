from context import *

import numpy as np
import pandas as pd
from clang.cindex import TokenKind
from src.cplag.tree import *

def calculate_metric(children1, children2, len1, len2, array):
    '''
        Function calculate percent of compliance from matrix
        @param children1 - list of nodes of type clang.cindex.Cursor object
        @param children2 - list of nodes of type clang.cindex.Cursor object
        @param len1 - count of nodes in children1
        @param len2 - count of nodes in children2
        @param array - matrix of compliance
    '''
    same_struct_metric = [0, 0]
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

    same_struct_metric[0] += 1
    same_struct_metric[1] += 1
    # same_struct_metric = [same_struct_metric[0] + 1,
    #                       same_struct_metric[1] + 1]

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
def smart_compare_nodes(tree1, tree2):
    '''
        Function for compare two trees
        @param tree1 - clang.cindex.Cursor object
        @param tree2 - clang.cindex.Cursor object
        tree1 and tree2 are parsed
    '''

    if(type(tree1) is not Cursor or type(tree2) is not Cursor):
        return TypeError

    children1 = list(tree1.get_children())
    children2 = list(tree2.get_children())
    len1 = len(children1)
    len2 = len(children2)

    # Can add the compare two leaves (len1 = len2 = 0)
    if (len1 == 0 and len2 == 0):
        return [1, 1]
    elif (len1 == 0):
        return [1, (get_count_of_nodes(tree2) + 1)]
    elif (len2 == 0):
        return [1, (get_count_of_nodes(tree1) + 1)]

    array = np.zeros((len1, len2), dtype=object)
    # indexes = []
    # columns = []

    for i in range(len1):
        # indexes.append(children1[i].spelling)
        for j in range(len2):
            array[i][j] = smart_compare_nodes(children1[i],
                                              children2[j])
            # print(repr(array[i][j]))

    # for j in range(len2):
    #    columns.append(children2[j].spelling)

    # table = pd.DataFrame(array, index=indexes, columns=columns)
    # print()
    # print(table)

    same_struct_metric = calculate_metric(children1,
                                          children2,
                                          len1,
                                          len2,
                                          array)

    return same_struct_metric


# Tested
def ast_compare(cursor1, cursor2, filename1, filename2, output=False):
    '''
        Function compares structure of two ast and return how they are
        same in percent
        @param cursor1- clang.cindex.Cursor object
        @param cursor2 - clang.cindex.Cursor object
        @param filename1 - name first file plus path to it from folder
        with get_ast.py
        @param filename2 - name second file plus path to it from folder
        with get_ast.py
    '''
    if(type(filename1) is not str or type(filename2) is not str or
       type(cursor1) is not Cursor or type(cursor2) is not Cursor):
        return TypeError
    elif(not os.path.isfile(filename1) or not os.path.isfile(filename2)):
        return FileNotFoundError

    parsed_nodes1 = get_not_ignored(cursor1, filename1)
    parsed_nodes2 = get_not_ignored(cursor2, filename2)

    if parsed_nodes1 is None:
        len1 = 0
    else:
        len1 = len(parsed_nodes1)

    if parsed_nodes2 is None:
        len2 = 0
    else:
        len2 = len(parsed_nodes2)

    array = np.zeros((len1, len2), dtype=object)
    indexes = []
    columns = []

    for i in range(len1):
        indexes.append(parsed_nodes1[i].spelling)
        for j in range(len2):
            array[i][j] = smart_compare_nodes(parsed_nodes1[i],
                                              parsed_nodes2[j])

    for j in range(len2):
        columns.append(parsed_nodes2[j].spelling)

    if output:
        table = pd.DataFrame(array, index=indexes, columns=columns)
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
def get_operators_frequency(tree1, tree2):
    '''
        Function estimates frequency of operators in tree
        @param tree1 - clang.cindex.Cursor object
        @param tree2 - clang.cindex.Cursor object
        returns an object with 3 lists like
        (operators:['>','<', ..],
        frequencies:[ [ 1, 0, 2, ..], [2, 1, 1, ..] ],
        operators_counter = [3, 7])
    '''
    if(type(tree1) is not Cursor or type(tree2) is not Cursor):
        return TypeError

    trees = [tree1, tree2]
    operators = ['+', '-', '*', '/', '%',               # Arithmetic Operators
                 '+=', '-=', '*=', '/=', '%=', '=',     # Assignment Operators
                 '!', '&&', '||',                       # Logical Operators
                 '!=', '==', '<=', '>=', '<', '>',      # Relational Operators
                 '^', '&', '|', '<<', '>>', '~'         # Bitwise Operators
                 ]
    frequencies = [[0] * len(operators), [0] * len(operators)]
    count_keywords = [{}, {}]
    operators_counter = [0, 0]
    seq_ops = [[], []]

    for i in range(len(trees)):
        child = trees[i]
        tokens = child.get_tokens()
        for token in tokens:
            if (token.kind == TokenKind.PUNCTUATION and
               token.spelling in operators):
                frequencies[i][operators.index(token.spelling)] += 1
                operators_counter[i] += 1
                seq_ops[i].append(token.spelling)
            if (token.kind == TokenKind.KEYWORD):
                keyword = token.spelling
                if keyword not in count_keywords[i].keys():
                    count_keywords[i][keyword] = 1
                else:
                    count_keywords[i][keyword] += 1
                if keyword not in count_keywords[(i + 1) % 2].keys():
                    count_keywords[(i + 1) % 2][keyword] = 0

    return (operators, frequencies, operators_counter,
            count_keywords, seq_ops)


# using commented in main (function is not in use)
def print_freq_analysis(op, fr, co):
    '''
        The Function prints table with result of frequency analysis
        @param op - array with most of the operators C/C++ language
        @param fr - array with count of appearence of operators
        @param co - array with count of operators in first and second file
    '''
    print()
    print('Operators freq analysis')
    print('{: <7}  total  {: >7}\n-----------------------'.format(co[0],
                                                                  co[1]))
    for i in range(len(op)):
        if fr[0][i] > 0 or fr[1][i] > 0:
            fr[0][i] /= co[0]
            fr[1][i] /= co[1]
            print('{:-7.2%}    {:4s}{:-7.2%}  '.format(fr[0][i], op[i],
                                                       fr[1][i]))


# Tested
def get_op_freq_percent(op, fr, co):
    '''
        The function returns how similar the operators are in the two AST
        @param op - array with most of the operators C/C++ language
        @param fr - array with count of appearence of operators
        @param co - array with count of operators in first and second file
    '''

    if(type(op) is not list or type(fr) is not list or type(co) is not list):
        return TypeError

    percent_of_same = [0, 0]
    for i in range(len(op)):
        if fr[0][i] > 0 or fr[1][i] > 0:
            percent_of_same[0] += min(fr[0][i], fr[1][i])
            percent_of_same[1] += max(fr[0][i], fr[1][i])
    if percent_of_same[1] == 0:
        return 0.0
    return percent_of_same[0] / percent_of_same[1]


# Tested
def get_kw_freq_percent(count_keywords):
    '''
        Function return how same keywords in two trees
        @param count_keywords - list with two dict objects with counts of
        keywords
    '''
    if(type(count_keywords) is not list):
        return TypeError

    percent_of_same = [0, 0]
    if(len(count_keywords) > 0):
        if(hasattr(count_keywords[0], "keys")):
            for key in count_keywords[0].keys():
                percent_of_same[0] += min(count_keywords[0][key],
                                          count_keywords[1][key])
                percent_of_same[1] += max(count_keywords[0][key],
                                          count_keywords[1][key])

            if percent_of_same[1] == 0:
                return 0.0
        else:
            return 0.0

        return percent_of_same[0] / percent_of_same[1]
    return 0


# Tested
def op_shift_metric(ops1, ops2):
    '''
        Returns the maximum value of the operator match and the shift under
        this condition
        @param ops1 - sequence of operators of tree1
        @param ops2 - sequence of operators of tree2
    '''

    if(type(ops1) is not list or type(ops2) is not list):
        return TypeError

    y = []

    count_el_f = len(ops1)
    count_el_s = len(ops2)
    if count_el_f > count_el_s:
        tmp = ops1
        ops1 = ops2
        ops2 = tmp
        count_el_f = len(ops1)
        count_el_s = len(ops2)
        del tmp

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
        if count_all == 0:
            y.append(0)
        else:
            y.append(counter / count_all)
        shift += 1

    max_shift = 0
    for index in range(1, len(y)):
        if y[index] > y[max_shift]:
            max_shift = index

    if len(y) > 0:
        return max_shift, y[max_shift]
    else:
        return 0, 0
        
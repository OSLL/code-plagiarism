from context import *

import os
import sys
import numpy as np
import pandas as pd
import ccsyspath
from clang.cindex import CursorKind, Index, TranslationUnit, TokenKind, Cursor
from time import perf_counter

IGNORE = [CursorKind.PREPROCESSING_DIRECTIVE,
          # CursorKind.MACRO_DEFINITION,
          CursorKind.MACRO_INSTANTIATION,
          CursorKind.INCLUSION_DIRECTIVE,
          CursorKind.USING_DIRECTIVE,
          CursorKind.NAMESPACE]


def get_cursor_from_file(filename, args=[]):
    '''
        Returns clang.cindex.Cursor object or 0 if file is undefined
        @param filename - full path to source file
        @param args - list of arguments for clang.cindex.Index.parse() method
    '''
    if not os.path.isfile(filename):
        print(filename, "Is not a file / doesn't exist")
        return 0

    index = Index.create()
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    file_obj = index.parse(filename, args=args, options=options) or 0
    return file_obj.cursor


# def traverse_and_print_values(cursor, src, output_path='./tree.ast',
#                               depth=0):
#     '''
#         Traverses and make file with AST of input file
#         @param cursor - clang.cindex.Cursor object
#         (look at get_cursor_from_file() )
#         @param src - path to source .c or .cpp file
#         @param output_path - full path to the output file
#         (with name and extension)
#         @param depth - level of depth in AST tree (influences indentation)
#     '''
#     children = cursor.get_children()
#     for child in children:
#         if (str(child.location.file).split('/')[-1] == src.split('/')[-1]
#            and child.kind not in IGNORE):
#             output = (str('|  ' * depth) +
#                       repr(child.kind).split('.')[-1] + " '" +
#                       str(child.spelling) + "' " + '\n')
#             # print(output)

#             with open(output_path, 'a') as output_file:
#                 output_file.write(output)
#             traverse_and_print_values(child, src, output_path, depth + 1)
#     return


# def get_code(node):
#     '''
#         Function return code which place in node as string
#         @param node - clang.cindex.Cursor object
#     '''
#     code = ''
#     for token in node.get_tokens():
#         code += token.spelling + ' '
#     return code


# def full_compare_nodes(node1, node2):
#     '''
#         Function compare to nodes in their top level and will
#         return true if all conditions will true
#         @param node1 - clang.cindex.Cursor object
#         @param node2 - clang.cindex.Cursor object
#     '''
#     first_cond = (node1.kind == node2.kind)
#     second_cond = (node1.spelling == node2.spelling)
#     node1_len = len(list(node1.get_children()))
#     node2_len = len(list(node2.get_children()))
#     third_cond = (node1_len == node2_len)
#     fourth_cond = (get_code(node1) == get_code(node2))
#     return first_cond and second_cond and third_cond and fourth_cond


# def full_compare(cursor1, cursor2, src1, src2):
#     '''
#         Function compare two trees on full compliance
#         @param cursor1 - clang.cindex.Cursor object
#         @param cursor2 - clang.cindex.Cursor object
#         @param src1 - str path to first file
#         @param src2 - str path to second file
#     '''
#     children1 = list(cursor1.get_children())
#     children2 = list(cursor2.get_children())
#     len1 = len(children1)
#     len2 = len(children2)
#     if len1 != len2:
#         print('Different count of nodes.')
#         return False
#     for index in range(len1):
#         loc1 = children1[index].location.file
#         loc2 = children2[index].location.file
#         if (str(loc1).split('/')[-1] == src1.split('/')[-1]
#            and str(loc2).split('/')[-1] == src2.split('/')[-1]
#            and children1[index].kind not in IGNORE
#            and children2[index].kind not in IGNORE):
#             if not full_compare_nodes(children1[index], children2[index]):
#                 return False
#     return True


# def is_same_structure(tree1, tree2, src1, src2):
#     '''
#         Function compare two trees on full compliance of structures
#         @param cursor1 - clang.cindex.Cursor object
#         @param cursor2 - clang.cindex.Cursor object
#         @param src1 - str path to first file
#         @param src2 - str path to second file
#     '''
#     children1 = list(tree1.get_children())
#     children2 = list(tree2.get_children())
#     len1 = len(children1)
#     len2 = len(children2)
#     if len1 != len2:
#         print('Different count of nodes.')
#         return False
#     for i in range(len1):
#         loc1 = children1[i].location.file
#         loc2 = children2[i].location.file
#         if (str(loc1).split('/')[-1] == src1.split('/')[-1]
#            and str(loc2).split('/')[-1] == src1.split('/')[-1]
#            and children1[i].kind not in IGNORE
#            and children2[i].kind not in IGNORE):
#             if not is_same_structure(children1[i], children2[i]):
#                 return False
#     return True

# def same_by(tree1, tree2, src1, src2):
#     '''
#         Function which return percent of compliance two trees
#         Small functions with big compliance add big contribution
#         what bad
#         Function waits delete
#         @param tree1 - clang.cindex.Cursor object
#         @param tree2 - clang.cindex.Cursor object
#         @param src1 - str path to first file
#         @param src2 - str path to second file
#     '''
#     parsed_nodes1 = get_not_ignored(tree1, src1)
#     parsed_nodes2 = get_not_ignored(tree2, src2)
#     len1 = len(parsed_nodes1)
#     len2 = len(parsed_nodes2)
#     array = np.zeros((len1, len2))
#     indexes = []
#     columns = []

#     for i in range(len1):
#         indexes.append(parsed_nodes1[i].spelling)
#         for j in range(len2):
#             count_nodes1 = get_count_of_nodes(parsed_nodes1[i])
#             count_nodes2 = get_count_of_nodes(parsed_nodes2[j])
#             compare_result = stupid_compare_nodes(parsed_nodes1[i],
#                                                   parsed_nodes2[j])
#             result = compare_result / (count_nodes1 + count_nodes2
#                                        - compare_result)
#             array[i][j] = result
#             # print(parsed_nodes1[i].spelling, '{:.2%} %'.format(result))

#     for j in range(len2):
#         columns.append(parsed_nodes2[j].spelling)

#     table = pd.DataFrame(array, index=indexes, columns=columns)
#     print(table)

#     same_struct_metric = 0
#     for i in range(min(len1, len2)):
#         ind = np.unravel_index(np.argmax(array, axis=None), array.shape)
#         same_struct_metric += array[ind]
#         array[ind[0]] = 0
#         array[:, ind[1]] = 0
#     same_struct_metric /= max(len1, len2)
#     print()
#     print('Structure is same by {:.2%}'.format(same_struct_metric))


# def stupid_compare_nodes(node1, node2):
#     '''
#         Works with same by, read documentation above
#         node1 and node2 are parsed
#         @param node1 - clang.cindex.Curosr object
#         @param node2 - clang.cindex.Curosr object
#     '''
#     same = 0
#     children1 = list(node1.get_children())
#     children2 = list(node2.get_children())
#     len1 = len(children1)
#     len2 = len(children2)
#     same += min(len1, len2)
#     for i in range(min(len1, len2)):
#         same += stupid_compare_nodes(children1[i], children2[i])

#     return same


# def compare_leaves(leaf1, leaf2):
#     '''
#         Function compare two leaves and return value from 0 to 1
#         If node haven't other nodes then it is leaf
#         @param leaf1 - first leaf
#         @param leaf2 - second leaf
#         values_first(second)[0] - keyword
#         values_first(second)[1] - literal
#     '''
#     tokens1 = leaf1.get_tokens()
#     values_first = [None, None]
#     tokens2 = leaf2.get_tokens()
#     values_second = [None, None]
#     count_same = 0
#     for token in tokens1:
#         if token.kind.name == 'LITERAL':
#             # If Russian language than crash
#             values_first[1] = token.spelling
#         if token.kind.name == 'KEYWORD':
#             values_first[0] = token.spelling
#     for token in tokens2:
#         if token.kind.name == 'LITERAL':
#             values_second[1] = token.spelling
#         if token.kind.name == 'KEYWORD':
#             values_second[0] = token.spelling

#     if values_second[0] == values_first[0]:
#         count_same += 2
#     elif values_first[0] is not None and values_second[0] is not None:
#         count_same += 1

#     if values_second[1] == values_first[1]:
#         count_same += 2
#     elif values_first[1] is not None and values_second[1] is not None:
#         count_same += 1

#     # print(values_first, values_second)
#     return [count_same, 4]

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


if __name__ == '__main__':
    args = '-x c++ --std=c++11'.split()
    syspath = ccsyspath.system_include_paths('clang++')
    incargs = [b'-I' + inc for inc in syspath]
    args = args + incargs

    directory = 'cpp/'
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    if not os.path.exists(directory):
        print('Directory isn\'t exist')
        exit()

    files = os.listdir(directory)
    files = list(filter(lambda x: (x.endswith('.cpp') or
                                   x.endswith('.c') or
                                   x.endswith('h')), files))

    count_files = len(files)

    start_eval = perf_counter()
    if(count_files > 0):
        iterrations = 0
        for i in range(1, count_files):
            iterrations += i
        iterration = 0

        # matrix_compliance = np.zeros((count_files, count_files))
        # indexes_cpp = []
        # columns_cpp = []
        for row in range(count_files):
            if directory[-1] != '/':
                directory += '/'
            filename = directory + files[row]
            # indexes_cpp.append(filename.split('/')[-1])
            for col in range(count_files):
                filename2 = directory + files[col]
                # if row == 1:
                #     columns_cpp.append(filename2.split('/')[-1])
                if row == col:
                    # matrix_compliance[row - 1][col - 1] = 1.0
                    continue
                if row > col:
                    continue

                cursor = get_cursor_from_file(filename, args)
                cursor2 = get_cursor_from_file(filename2, args)
                if cursor and cursor2:
                    res = ast_compare(cursor, cursor2, filename, filename2)

                    struct_res = round(res[0] / res[1], 3)
                    (op, fr, co, ck, seq) = get_operators_frequency(cursor,
                                                                    cursor2)

                    operators_res = get_op_freq_percent(op, fr, co)
                    keywords_res = get_kw_freq_percent(ck)
                    if(len(seq) >= 2):
                        b_sh, sh_res = op_shift_metric(seq[0], seq[1])
                    else:
                        b_sh, sh_res = 0
                    # matrix_compliance[row - 1][col - 1] = struct_res
                    # matrix_compliance[col - 1][row - 1] = struct_res

                    # summ = (struct_res * 1.2 + operators_res * 0.8
                    #         + keywords_res * 0.8 + sh_res * 0.3)
                    # max * 0.70
                    # if summ > 2.325:

                    similarity = (struct_res * 1.6 + operators_res * 1
                                  + keywords_res * 1.1 + sh_res * 0.3) / 4

                    if similarity > 0.72:
                        print("         ")
                        print('+' * 40)
                        print('May be similar:', filename.split('/')[-1],
                              filename2.split('/')[-1])
                        print("Total similarity -",
                              '{:.2%}'.format(similarity))

                        ast_compare(cursor, cursor2, filename, filename2, True)
                        text = 'Operators match percentage:'
                        print(text, '{:.2%}'.format(operators_res))
                        # print_freq_analysis(op, fr, co)
                        text = 'Keywords match percentage:'
                        print(text, '{:.2%}'.format(keywords_res))

                        print('---')
                        print('Op shift metric.')
                        print('Best op shift:', b_sh)
                        print('Persent same: {:.2%}'.format(sh_res))
                        print('---')
                        print('+' * 40)

                iterration += 1
                print('  {:.2%}'.format(iterration / iterrations), end="\r")
    else:
        print("Folder is empty")

    print("Analysis complete")
    print('Time for all {:.2f}'.format(perf_counter() - start_eval))
    # same_cpp = pd.DataFrame(matrix_compliance, index=indexes_cpp,
    #                         columns=columns_cpp)
    # same_cpp.to_csv('same_structure.csv', sep=';')

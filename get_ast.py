import os
import sys
import numpy as np
import pandas as pd
import ccsyspath
from clang.cindex import CursorKind, Index, TranslationUnit, TokenKind
from time import perf_counter
# from clang.cindex import *

IGNORE = [CursorKind.PREPROCESSING_DIRECTIVE,
          CursorKind.MACRO_DEFINITION,
          CursorKind.MACRO_INSTANTIATION,
          CursorKind.INCLUSION_DIRECTIVE,
          CursorKind.USING_DIRECTIVE,
          CursorKind.NAMESPACE]


def get_cursor_from_file(filename, args=[]):
    '''
        Returns clang.cindex.Cursor object or 0 if file is undefined
        @param filename - fuul path to source file
        @param args - list of arguments for clang.cindex.Index.parse() method
    '''
    if not os.path.isfile(filename):
        print(filename, "Is not a file / doesn't exist")
        return 0

    index = Index.create()
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    file_obj = index.parse(filename, args=args, options=options) or 0
    return file_obj.cursor


def traverse_and_print_values(cursor, src, output_path='./tree.ast', depth=0):
    '''
        Traverses and make file with AST of input file
        @param cursor - clang.cindex.Cursor object
        (look at get_cursor_from_file() )
        @param src - path to source .c or .cpp file
        @param output_path - full path to the output file
        (with name and extension)
        @param depth - level of depth in AST tree (influences indentation)
    '''
    children = cursor.get_children()
    for child in children:
        if (str(child.location.file).split('/')[-1] == src.split('/')[-1]
           and child.kind not in IGNORE):
            output = (str('|  ' * depth) +
                      repr(child.kind).split('.')[-1] + " '" +
                      str(child.spelling) + "' " + '\n')
            # print(output)

            with open(output_path, 'a') as output_file:
                output_file.write(output)
            traverse_and_print_values(child, src, output_path, depth + 1)
    return


def get_code(node):
    '''
        Function return code which place in node as string
        @param node - clang.cindex.Cursor object
    '''
    code = ''
    for token in node.get_tokens():
        code += token.spelling + ' '
    return code


def full_compare_nodes(node1, node2):
    '''
        Function compare to nodes in their top level and will
        return true if all conditions will true
        @param node1 - clang.cindex.Cursor object
        @param node2 - clang.cindex.Cursor object
    '''
    first_cond = (node1.kind == node2.kind)
    second_cond = (node1.spelling == node2.spelling)
    node1_len = len(list(node1.get_children()))
    node2_len = len(list(node2.get_children()))
    third_cond = (node1_len == node2_len)
    fourth_cond = (get_code(node1) == get_code(node2))
    return first_cond and second_cond and third_cond and fourth_cond


def full_compare(cursor1, cursor2, src1, src2):
    '''
        Function compare two trees on full compliance
        @param cursor1 - clang.cindex.Cursor object
        @param cursor2 - clang.cindex.Cursor object
        @param src1 - str path to first file
        @param src2 - str path to second file
    '''
    children1 = list(cursor1.get_children())
    children2 = list(cursor2.get_children())
    len1 = len(children1)
    len2 = len(children2)
    if len1 != len2:
        print('Different count of nodes.')
        return False
    for index in range(len1):
        loc1 = children1[index].location.file
        loc2 = children2[index].location.file
        if (str(loc1).split('/')[-1] == src1.split('/')[-1]
           and str(loc2).split('/')[-1] == src2.split('/')[-1]
           and children1[index].kind not in IGNORE
           and children2[index].kind not in IGNORE):
            if not full_compare_nodes(children1[index], children2[index]):
                return False
    return True


def is_same_structure(tree1, tree2, src1, src2):
    '''
        Function compare two trees on full compliance of structures
        @param cursor1 - clang.cindex.Cursor object
        @param cursor2 - clang.cindex.Cursor object
        @param src1 - str path to first file
        @param src2 - str path to second file
    '''
    children1 = list(tree1.get_children())
    children2 = list(tree2.get_children())
    len1 = len(children1)
    len2 = len(children2)
    if len1 != len2:
        print('Different count of nodes.')
        return False
    for i in range(len1):
        loc1 = children1[i].location.file
        loc2 = children2[i].location.file
        if (str(loc1).split('/')[-1] == src1.split('/')[-1]
           and str(loc2).split('/')[-1] == src1.split('/')[-1]
           and children1[i].kind not in IGNORE
           and children2[i].kind not in IGNORE):
            if not is_same_structure(children1[i], children2[i]):
                return False
    return True


def get_not_ignored(tree, src):
    '''
        Function helps to discard unnecessary nodes such as imports
        @param tree - clang.cindex.Cursor object
        @param src - str path to file
    '''
    children = list(tree.get_children())
    length = len(children)
    parsed_nodes = []
    for i in range(length):
        loc = children[i].location.file
        if (str(loc).split('/')[-1] == src.split('/')[-1]
           and children[i].kind not in IGNORE):
            parsed_nodes.append(children[i])
    return parsed_nodes


# tree is parsed.
def get_count_of_nodes(tree):
    '''
        Get count of nodes of tree without head
        @param tree - clang.cindex.Cursor object
    '''
    count = 0
    children = list(tree.get_children())
    length = len(children)
    count += length
    for i in range(length):
        count += get_count_of_nodes(children[i])

    return count


def same_by(tree1, tree2, src1, src2):
    '''
        Function which return percent of compliance two trees
        Small functions with big compliance add big contribution
        what bad
        Function waits delete
        @param tree1 - clang.cindex.Cursor object
        @param tree2 - clang.cindex.Cursor object
        @param src1 - str path to first file
        @param src2 - str path to second file
    '''
    parsed_nodes1 = get_not_ignored(tree1, src1)
    parsed_nodes2 = get_not_ignored(tree2, src2)
    len1 = len(parsed_nodes1)
    len2 = len(parsed_nodes2)
    array = np.zeros((len1, len2))
    indexes = []
    columns = []

    for i in range(len1):
        indexes.append(parsed_nodes1[i].spelling)
        for j in range(len2):
            count_nodes1 = get_count_of_nodes(parsed_nodes1[i])
            count_nodes2 = get_count_of_nodes(parsed_nodes2[j])
            compare_result = stupid_compare_nodes(parsed_nodes1[i],
                                                  parsed_nodes2[j])
            result = compare_result / (count_nodes1 + count_nodes2
                                       - compare_result)
            array[i][j] = result
            # print(parsed_nodes1[i].spelling, '{:.2%} %'.format(result))

    for j in range(len2):
        columns.append(parsed_nodes2[j].spelling)

    table = pd.DataFrame(array, index=indexes, columns=columns)
    print(table)

    same_struct_metric = 0
    for i in range(min(len1, len2)):
        ind = np.unravel_index(np.argmax(array, axis=None), array.shape)
        same_struct_metric += array[ind]
        array[ind[0]] = 0
        array[:, ind[1]] = 0
    same_struct_metric /= max(len1, len2)
    print()
    print('Structure is same by {:.2%}'.format(same_struct_metric))


def stupid_compare_nodes(node1, node2):
    '''
        Works with same by, read documentation above
        node1 and node2 are parsed
        @param node1 - clang.cindex.Curosr object
        @param node2 - clang.cindex.Curosr object
    '''
    same = 0
    children1 = list(node1.get_children())
    children2 = list(node2.get_children())
    len1 = len(children1)
    len2 = len(children2)
    same += min(len1, len2)
    for i in range(min(len1, len2)):
        same += stupid_compare_nodes(children1[i], children2[i])

    return same


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
    same_struct_metric = (0, 0)
    indexes = []
    for i in range(min(len1, len2)):
        ind = find_max_index(array, len1, len2)
        indexes.append(ind)
        same_struct_metric = (same_struct_metric[0] +
                              array[ind][0],
                              same_struct_metric[1] +
                              array[ind][1])
        for i in range(len2):
            array[ind[0]][i] = (0, 0)
        for j in range(len1):
            array[j][ind[1]] = (0, 0)

    same_struct_metric = (same_struct_metric[0] + 1,
                          same_struct_metric[1] + 1)

    not_count = 0
    if len1 > len2:
        not_count = getn_count_nodes(len2, len1, indexes, 0, children1)
    elif len2 > len1:
        not_count = getn_count_nodes(len1, len2, indexes, 1, children2)

    same_struct_metric = (same_struct_metric[0],
                          same_struct_metric[1] + not_count)

    return same_struct_metric


def smart_compare_nodes(tree1, tree2):
    '''
        Function for compare two trees
        @param tree1 - clang.cindex.Cursor object
        @param tree2 - clang.cindex.Cursor object
        tree1 and tree2 are parsed
    '''
    children1 = list(tree1.get_children())
    children2 = list(tree2.get_children())
    len1 = len(children1)
    len2 = len(children2)

    if (len1 == 0 and len2 == 0):
        return (1, 1)
    elif (len1 == 0):
        return (1, (get_count_of_nodes(tree2) + 1))
    elif (len2 == 0):
        return (1, (get_count_of_nodes(tree1) + 1))

    array = np.zeros((len1, len2), dtype=object)
    # indexes = []
    # columns = []

    for i in range(len1):
        # indexes.append(children1[i].spelling)
        for j in range(len2):
            result = smart_compare_nodes(children1[i],
                                         children2[j])
            array[i][j] = result
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

    # print('Structure is same by {:.2%}'.format(same_struct_metric[0] /
    #                                           same_struct_metric[1]))
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
    parsed_nodes1 = get_not_ignored(cursor1, filename1)
    parsed_nodes2 = get_not_ignored(cursor2, filename2)
    len1 = len(parsed_nodes1)
    len2 = len(parsed_nodes2)

    array = np.zeros((len1, len2), dtype=object)
    indexes = []
    columns = []
    for i in range(len1):
        indexes.append(parsed_nodes1[i].spelling)
        for j in range(len2):
            result = smart_compare_nodes(parsed_nodes1[i],
                                         parsed_nodes2[j])
            array[i][j] = result
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
    trees = [tree1, tree2]
    operators = ['+', '-', '*', '/', '%',               # Arithmetic Operators
                 '+=', '-=', '*=', '/=', '%=', '=',     # Assignment Operators
                 '!', '&&', '||',                       # Logical Operators
                 '!=', '==', '<=', '>=', '<', '>',      # Relational Operators
                 '^', '&', '|', '<<', '>>', '~'         # Bitwise Operators
                 ]
    frequencies = [[0] * len(operators), [0] * len(operators)]
    operators_counter = [0, 0]

    for i in range(len(trees)):
        child = trees[i]
        tokens = child.get_tokens()
        for token in tokens:
            if (token.kind == TokenKind.PUNCTUATION and
               token.spelling in operators):
                frequencies[i][operators.index(token.spelling)] += 1
                operators_counter[i] += 1

        # раскомментить для возвращения доли каждого опратора,
        # а не его количества
        # for j in range(len(operators)):
        #     frequencies[i][j] /= operators_counter[i]

    return (operators, frequencies, operators_counter)


def print_freq_analysis(op, fr, co):
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


def get_freq_percent(op, fr, co):
    percent_of_same = [0, 0]
    for i in range(len(op)):
        if fr[0][i] > 0 or fr[1][i] > 0:
            percent_of_same[0] += min(fr[0][i], fr[1][i])
            percent_of_same[1] += max(fr[0][i], fr[1][i])
    if percent_of_same[1] == 0:
        return 0.0
    return percent_of_same[0] / percent_of_same[1]


if __name__ == '__main__':
    filename = 'cpp/test1.cpp'
    filename2 = 'cpp/test2.cpp'
    output_path_first = str(filename.split('/')[-1].split('.')[0])+".ast"
    output_path_second = str(filename2.split('/')[-1].split('.')[0])+".ast"

    if len(sys.argv) > 4:
        filename = sys.argv[1]
        filename2 = sys.argv[2]
        output_path_first = sys.argv[3]
        output_path_second = sys.argv[4]
    elif len(sys.argv) > 3:
        filename = sys.argv[1]
        filename2 = sys.argv[2]
        output_path_first = sys.argv[3]
    elif len(sys.argv) > 2:
        filename = sys.argv[1]
        filename2 = sys.argv[2]
    elif len(sys.argv) > 1:
        filename = sys.argv[1]

    args = '-x c++ --std=c++11'.split()
    syspath = ccsyspath.system_include_paths('clang++')
    incargs = [b'-I' + inc for inc in syspath]
    args = args + incargs
    cursor = get_cursor_from_file(filename, args)
    cursor2 = get_cursor_from_file(filename2, args)
    if cursor and cursor2:
        if os.path.isfile(output_path_first):
            os.remove(output_path_first)
        if os.path.isfile(output_path_second):
            os.remove(output_path_second)

        # traverse_and_print_values(cursor, filename, output_path_first)
        # traverse_and_print_values(cursor2, filename2, output_path_second)
        # print('Same Structure:',
        #      is_same_structure(cursor, cursor2, filename,
        #                        filename2), '\n')
        # print('Is same:', full_compare(cursor, cursor2,
        #                                filename, filename2), '\n')
        # same_by(cursor, cursor2, filename, filename2)

        # ast_compare(cursor, cursor2, filename, filename2)
        # (op, fr, co) = get_operators_frequency(cursor, cursor2)
        # print_freq_analysis(op, fr, co)

    matrix_compliance = np.zeros((12, 12))
    indexes_cpp = []
    columns_cpp = []
    start_eval = perf_counter()
    for row in range(1, 13):
        filename = 'cpp/dataset/sample' + str(row) + '.cpp'
        indexes_cpp.append(filename.split('/')[-1])
        for col in range(1, 13):
            filename2 = 'cpp/dataset/sample' + str(col) + '.cpp'
            if row == 1:
                columns_cpp.append(filename2.split('/')[-1])
            if row == col:
                matrix_compliance[row - 1][col - 1] = 1.0
                continue
            if row > col:
                continue

            cursor = get_cursor_from_file(filename, args)
            cursor2 = get_cursor_from_file(filename2, args)
            if cursor and cursor2:
                start = perf_counter()
                res = ast_compare(cursor, cursor2, filename, filename2)

                percent = round(res[0] / res[1], 3)
                matrix_compliance[row - 1][col - 1] = percent
                matrix_compliance[col - 1][row - 1] = percent

                if percent >= 0.8:
                    print()
                    print('+'*40)
                    print('May be similar:', filename.split('/')[-1],
                          filename2.split('/')[-1])
                    ast_compare(cursor, cursor2, filename, filename2, True)
                    (op, fr, co) = get_operators_frequency(cursor, cursor2)
                    print('Operators match percentage:')
                    print('{:.2%}'.format(get_freq_percent(op, fr, co)))
                    print_freq_analysis(op, fr, co)
                    print('+'*22)

    print()
    print('Time for all', perf_counter() - start_eval)
    same_cpp = pd.DataFrame(matrix_compliance, index=indexes_cpp,
                            columns=columns_cpp)
    same_cpp.to_csv('same_structure.csv', sep=';')

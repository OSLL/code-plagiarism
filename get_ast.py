import os
import sys
import numpy as np
import pandas as pd
from clang.cindex import CursorKind, Index, TranslationUnit
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
            # str(len(list(child.get_children()))) + '\n')
            print(output)

            if child.kind == CursorKind.UNEXPOSED_EXPR:
                for token in child.get_tokens():
                    print(token.spelling)

            with open(output_path, 'a') as output_file:
                output_file.write(output)
            traverse_and_print_values(child, src, output_path, depth + 1)
    return


def get_code(node):
    code = ''
    for token in node.get_tokens():
        code += token.spelling + ' '
    return code


def full_compare_nodes(node1, node2):
    first_cond = (node1.kind == node2.kind)
    second_cond = (node1.spelling == node2.spelling)
    node1_len = len(list(node1.get_children()))
    node2_len = len(list(node2.get_children()))
    third_cond = (node1_len == node2_len)
    fourth_cond = (get_code(node1) == get_code(node2))
    return first_cond and second_cond and third_cond and fourth_cond


def full_compare(cursor1, cursor2, src1, src2):
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
    count = 0
    children = list(tree.get_children())
    length = len(children)
    count += length
    for i in range(length):
        count += get_count_of_nodes(children[i])

    return count


def same_by(tree1, tree2, src1, src2):
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
        array[ind] = 0
    same_struct_metric /= max(len1, len2)
    print()
    print('Structure is same by {:2%}'.format(same_struct_metric))


# node1 and node2 are parsed.
def stupid_compare_nodes(node1, node2):
    same = 0
    children1 = list(node1.get_children())
    children2 = list(node2.get_children())
    len1 = len(children1)
    len2 = len(children2)
    same += min(len1, len2)
    for i in range(min(len1, len2)):
        same += stupid_compare_nodes(children1[i], children2[i])

    return same


# Nodes are parsed and turn in list
def smart_compare_nodes(tree1, tree2):
    children1 = list(tree1.get_children())
    children2 = list(tree2.get_children())
    len1 = len(children1)
    len2 = len(children2)

    if (len1 == 0 and len2 == 0):
        return 1.0
    elif (len1 == 0):
        return 1 / (get_count_of_nodes(tree2) + 1)
    elif (len2 == 0):
        return 1 / (get_count_of_nodes(tree1) + 1)

    array = np.zeros((len1, len2))
    indexes = []
    columns = []

    for i in range(len1):
        indexes.append(children1[i].spelling)
        for j in range(len2):
            result = smart_compare_nodes(children1[i],
                                         children2[j])
            array[i][j] = result

    for j in range(len2):
        columns.append(children2[j].spelling)

    table = pd.DataFrame(array, index=indexes, columns=columns)
    print()
    print(table)

    same_struct_metric = 0
    for i in range(min(len1, len2)):
        ind = np.unravel_index(np.argmax(array, axis=None), array.shape)
        same_struct_metric += array[ind]
        print('index:', ind[0], ind[1])
        array[ind[0]] = 0
        array[:, ind[1]] = 0
    same_struct_metric /= max(len1, len2)
    print('Structure is same by {:.2%}'.format(same_struct_metric))
    return same_struct_metric


if __name__ == '__main__':
    filename = 'cpp/test1.cpp'
    filename2 = 'cpp/test2.cpp'
    output_path_first = "tree_first.ast"
    output_path_second = "tree_second.ast"

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    cursor = get_cursor_from_file(filename)
    cursor2 = get_cursor_from_file(filename2)
    if cursor:
        if len(sys.argv) > 2:
            filename2 = sys.argv[2]
        elif len(sys.argv) > 3:
            output_path = sys.argv[3]
        else:
            output_path = str(filename.split('/')[-1].split('.')[0])+".ast"

        if os.path.isfile(output_path):
            os.remove(output_path)

        print('First tree: ')
        traverse_and_print_values(cursor, filename, output_path_first)
        print('Second tree: ')
        traverse_and_print_values(cursor2, filename2, output_path_second)
        print('Same Structure:',
              is_same_structure(cursor, cursor2, filename,
                                filename2), '\n')
        print('Is same:', full_compare(cursor, cursor2,
                                       filename, filename2), '\n')
        same_by(cursor, cursor2, filename, filename2)

        parsed_nodes1 = get_not_ignored(cursor, filename)
        parsed_nodes2 = get_not_ignored(cursor2, filename2)
        len1 = len(parsed_nodes1)
        len2 = len(parsed_nodes2)
        array = np.zeros((len1, len2))
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

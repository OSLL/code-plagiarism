import os
import sys
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
                                       filename, filename2))

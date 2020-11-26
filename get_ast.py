from clang.cindex import *
import os
import sys

    
IGNORE = [ CursorKind.PREPROCESSING_DIRECTIVE, 
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


def traverse_and_print_values(cursor, src, output_path = './tree.ast', depth = 0):
    '''
        Traverses and make file with AST of input file
        @param cursor - clang.cindex.Cursor object (look at get_cursor_from_file() )
        @param src - path to source .c or .cpp file 
        @param output_path - full path to the output file (with name and extension)
        @param depth - level of depth in AST tree (influences indentation)
    '''
    children = cursor.get_children()
    for child in children:
        if str(child.location.file).split('/')[-1] == src.split('/')[-1] and child.kind not in IGNORE:
            output = (str('|  ' * depth) +
                str(child.kind) + " '" + 
                str(child.spelling) + "' " + 
                str(len(list(child.get_children()))) + '\n')
            # print(output)

            with open(output_path, 'a') as output_file:
                output_file.write(output)
            traverse_and_print_values(child, src, output_path, depth + 1)
    return


if __name__ == '__main__':
    filename = 'cpp/test.cpp'
    output_path = "tree.ast"

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    cursor = get_cursor_from_file(filename)
    if cursor:
        if len(sys.argv) > 2:
            output_path = sys.argv[2]
        else:
            output_path = str(sys.argv[1].split('/')[-1].split('.')[0])+".ast"

        if os.path.isfile(output_path):
            os.remove(output_path)

        traverse_and_print_values(cursor, filename, output_path)
    
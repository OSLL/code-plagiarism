import os
from clang.cindex import Index, TranslationUnit

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

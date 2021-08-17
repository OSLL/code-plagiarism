import os
import warnings
import ccsyspath
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


def prepare_cursors(file1, file2):
    warnings.simplefilter("ignore", ResourceWarning)
    args = '-x c++ --std=c++11'.split()
    syspath = ccsyspath.system_include_paths('clang++')
    incargs = [b'-I' + inc for inc in syspath]
    args = args + incargs
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             './tests/data')
    files = list(filter(lambda x: (x.endswith('.cpp') or
                                   x.endswith('.c') or
                                   x.endswith('h')), os.listdir(directory)))

    if(len(files) < 2):
        message = 'At least 2 files in /tests folder are needed'
        raise FileNotFoundError(message)
    else:
        if(file1 == ""):
            filename = os.path.join(directory, "./rw1.cpp")
        else:
            filename = os.path.join(directory, "./" + file1)

        if(file2 == ""):
            filename2 = os.path.join(directory, "./rw2.cpp")
        else:
            filename2 = os.path.join(directory, "./" + file2)

        cursor = get_cursor_from_file(filename, args)
        cursor2 = get_cursor_from_file(filename2, args)
        return (filename, filename2, cursor, cursor2)

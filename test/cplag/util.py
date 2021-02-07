from context import *

import warnings
import ccsyspath
import os

from src.cplag.util import get_cursor_from_file

def prepare_cursors(file1, file2):
    warnings.simplefilter("ignore", ResourceWarning)
    args = '-x c++ --std=c++11'.split()
    syspath = ccsyspath.system_include_paths('clang++')
    incargs = [b'-I' + inc for inc in syspath]
    args = args + incargs
    directory = 'cpp/tests/'
    files = list(filter(lambda x: (x.endswith('.cpp') or
                                    x.endswith('.c') or
                                    x.endswith('h')), os.listdir(directory)))

    if(len(files) < 2):
        raise FileNotFoundError('At least 2 files in /tests folder are needed') 
    else:
        if(file1 == ""):
            filename = directory + "/" + 'rw1.cpp'
        else:
            filename = directory + "/" + file1

        if(file2 == ""):
            filename2 = directory + "/" + 'rw2.cpp'
        else:
            filename2 = directory + "/" + file2

        cursor = get_cursor_from_file(filename, args)
        cursor2 = get_cursor_from_file(filename2, args)
        return (filename, filename2, cursor, cursor2)
        
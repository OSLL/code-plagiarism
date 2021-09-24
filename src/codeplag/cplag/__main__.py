import ccsyspath
import sys
import os
import pandas as pd

from time import perf_counter
from codeplag.cplag.util import get_cursor_from_file
from codeplag.cplag.tree import get_features
from codeplag.utils import print_compare_res

args = '-x c++ --std=c++11'.split()
syspath = ccsyspath.system_include_paths('clang++')
incargs = [b'-I' + inc for inc in syspath]
args = args + incargs

pd.options.display.float_format = '{:,.2%}'.format

if __name__ == '__main__':
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
    if (count_files > 0):
        iterrations = 0
        for i in range(1, count_files):
            iterrations += i
        iterration = 0

        for row in range(count_files):
            if directory[-1] != '/':
                directory += '/'
            filename = directory + files[row]
            for col in range(count_files):
                filename2 = directory + files[col]
                if row == col:
                    continue
                if row > col:
                    continue

                cursor = get_cursor_from_file(filename, args)
                cursor2 = get_cursor_from_file(filename2, args)
                if cursor and cursor2:
                    features1 = get_features(cursor, filename)
                    features2 = get_features(cursor2, filename2)
                    print_compare_res(features1, features2)

                iterration += 1
                print('  {:.2%}'.format(iterration / iterrations), end="\r")
    else:
        print("Folder is empty")

    print("Analysis complete")
    print('Time for all {:.2f}'.format(perf_counter() - start_eval))

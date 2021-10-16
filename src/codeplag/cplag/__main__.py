import ccsyspath
import sys
import os
import numpy as np
import pandas as pd

from time import perf_counter
from codeplag.cplag.util import get_cursor_from_file
from codeplag.cplag.tree import get_features
from codeplag.utils import print_compare_res, get_files_path_from_directory
from codeplag.mode import get_mode

mode, args = get_mode()
compile_args = '-x c++ --std=c++11'.split()
syspath = ccsyspath.system_include_paths('clang++')
incargs = [b'-I' + inc for inc in syspath]
compile_args = compile_args + incargs

pd.options.display.float_format = '{:,.2%}'.format

start_eval = perf_counter()

if mode == 2:
    # Local file compares with files in a local directory
    # Use variablse 'file' and 'dir'

    files = os.listdir(args.dir)
    files = list(filter(lambda x: (x.endswith('.cpp') or\
                                   x.endswith('.c') or\
                                   x.endswith('.h')), files))

    count_files = len(files)
    if count_files == 0:
        print("Folder is empty")
        exit(0)

    iterrations = (count_files)
    iterration = 0

    cursor1 = get_cursor_from_file(args.file, compile_args)
    features1 = get_features(cursor1, args.file)
    for row in np.arange(0, count_files, 1):
        filename = os.path.join(args.dir, files[row])
        cursor2 = get_cursor_from_file(filename, compile_args)
        if cursor1 and cursor2:
            features2 = get_features(cursor2, filename)
            print_compare_res(features1, features2, args.threshold)

        iterration += 1
        print('  {:.2%}'.format(iterration / iterrations), end="\r")

elif mode == 4:
    # Local project compares with a local directory
    # Use variables 'project' and 'dir'

    dir_files = os.listdir(args.dir)
    dir_files = list(filter(lambda x: (x.endswith('.cpp') or\
                                   x.endswith('.c') or\
                                   x.endswith('.h')), dir_files))
    project_files = get_files_path_from_directory(args.project,
                                                  extensions=[r'.c\b',
                                                              r'.cpp\b',
                                                              r'.h\b'])

    count_files = len(dir_files) * len(project_files)
    if count_files == 0:
        print("One of the folder is empty")
        exit(0)

    iterrations = (count_files)
    iterration = 0

    for row in np.arange(0, len(dir_files), 1):
        filename = os.path.join(args.dir, dir_files[row])
        cursor1 = get_cursor_from_file(filename, compile_args)
        features1 = get_features(cursor1, filename)
        for file in project_files:
            cursor2 = get_cursor_from_file(file, compile_args)
            features2 = get_features(cursor2, file)
            print_compare_res(features1, features2, args.threshold)

            iterration += 1
            print('  {:.2%}'.format(iterration / iterrations), end="\r")
else:
    logger.warning("Incorrect arguments or not supported!")
    print("Check the arguments (use --help)")
    logger.info("Cplag stopping...")
    exit(0)

print("Analysis complete")
print('Time for all {:.2f}'.format(perf_counter() - start_eval))

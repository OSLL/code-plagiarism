import ccsyspath
import sys
import os
from time import perf_counter
from codeplag.cplag.util import get_cursor_from_file
from codeplag.cplag.metric import *

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
                    b_sh = sh_res = 0
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

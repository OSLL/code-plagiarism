from context import *

import os
import sys
import datetime

from time import perf_counter
from src.pyplag.tree import *
from src.pyplag.metric import *

directory = 'py/'
if len(sys.argv) > 1:
    directory = sys.argv[1]
if not os.path.exists(directory):
    print('Directory isn\'t exist')
    exit()

files = os.listdir(directory)
files = list(filter(lambda x: (x.endswith('.py')), files))

count_files = len(files)
start_eval = perf_counter()
date = datetime.datetime.now().strftime('%Y%m%d-%H#%M#%S')
log_file = open('./logs/pylog' + date + '.txt', 'w')

iterrations = (count_files * count_files - count_files) / 2
iterration = 0

for row in np.arange(0, count_files, 1):
    if directory[-1] != '/':
        directory += '/'
    filename = directory + files[row]
    # indexes_py.append(filename.split('/')[-1])
    for col in np.arange(0, count_files, 1):
        filename2 = directory + files[col]
        # if row == 1:
        #     columns_cpp.append(filename2.split('/')[-1])
        if row == col:
            # matrix_compliance[row - 1][col - 1] = 1.0
            continue
        if row > col:
            continue

        tree1 = get_AST(filename)
        tree2 = get_AST(filename2)
        if tree1 is None or tree2 is None:
            continue

        features1 = ASTFeatures()
        features2 = ASTFeatures()
        features1.visit(tree1)
        features2.visit(tree2)
        res = struct_compare(features1.structure, features2.structure)
        struct_res = round(res[0] / res[1], 3)
        operators_res = nodes_metric(features1.operators,
                                     features2.operators)
        keywords_res = nodes_metric(features1.keywords, features2.keywords)
        literals_res = nodes_metric(features1.literals, features2.literals)
        b_sh, sh_res = op_shift_metric(features1.seq_ops,
                                       features2.seq_ops)
        # keywords_res = get_kw_freq_percent(ck)
        # matrix_compliance[row - 1][col - 1] = struct_res
        # matrix_compliance[col - 1][row - 1] = struct_res

        similarity = (struct_res * 1.5 + operators_res * 0.8 +
                      keywords_res * 0.9 + literals_res * 0.5 +
                      sh_res * 0.3) / 4

        if similarity > 0.72:
            print("         ")
            print('+' * 40)
            log_file.write('+' * 40 + '\n')
            print('May be similar:', filename.split('/')[-1],
                    filename2.split('/')[-1])
            print("Total similarity -", '{:.2%}'.format(similarity))
            log_file.write('May be similar:' + filename.split('/')[-1] +
                            ' ' + filename2.split('/')[-1] + '\n')
            print()
            print('Structure is same by {:.2%}'.format(res[0] / res[1]))
            text = 'Operators match percentage:'
            print(text, '{:.2%}'.format(operators_res))
            log_file.write(text + '{:.2%}'.format(operators_res) + '\n')
            text = 'Keywords match percentage:'
            print(text, '{:.2%}'.format(keywords_res))
            log_file.write(text + '{:.2%}'.format(keywords_res) + '\n')
            text = 'Literals match percentage:'
            print(text, '{:.2%}'.format(literals_res))
            log_file.write(text + '{:.2%}'.format(literals_res) + '\n')

            print('---')
            print('Op shift metric.')
            print('Best op shift:', b_sh)
            print('Persent same: {:.2%}'.format(sh_res))
            print('---')
            log_file.write('---\n' + 'Op shift metric.\n' +
                            'Best op shift:' + str(b_sh) + '\n'
                            + 'Persent same: {:.2%}'.format(sh_res) +
                            '\n' + '---\n')
            print('+' * 40)
            log_file.write('+' * 40 + '\n\n')

        iterration += 1
        print('  {:.2%}'.format(iterration / iterrations), end="\r")

if count_files == 0:
    print("Folder is empty")

print("Analysis complete")
print('Time for all {:.2f}'.format(perf_counter() - start_eval))
log_file.close()
# same_cpp = pd.DataFrame(matrix_compliance, index=indexes_cpp,
#                         columns=columns_cpp)
# same_cpp.to_csv('same_structure.csv', sep=';')

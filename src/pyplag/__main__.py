import context
import ast
import os
import sys
import datetime
import numpy as np
import pandas as pd
pd.options.display.float_format = '{:,.2%}'.format

from time import perf_counter
# from src.pyplag.tree import *
from src.pyplag.tree import ASTFeatures, get_AST
from src.pyplag.metric import nodes_metric, run_compare
from src.pyplag.metric import op_shift_metric, get_children_ind
from src.github_helper.utils import get_list_of_repos, select_repos
from src.github_helper.utils import get_python_files_links, get_code
# from src.pyplag.metric import *


def print_compare_res(metrics, total_similarity, best_shift, 
                      matrix, struct1, struct2, to_names1, to_names2,
                      filename1, filename2):
    ch_inds1, count_of_children1 = get_children_ind(struct1, len(struct1))
    ch_inds2, count_of_children2 = get_children_ind(struct2, len(struct2))
    indexes = [to_names1[struct1[ind][1]] for ind in ch_inds1]
    columns = [to_names2[struct2[ind][1]] for ind in ch_inds2]
    data = np.zeros((matrix.shape[0], matrix.shape[1]), dtype=np.float32)
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            data[row][col] = matrix[row][col][0] / matrix[row][col][1]
    df = pd.DataFrame(data=data,
                      index=indexes, columns=columns)

    print("         ")
    print('+' * 40)
    print('May be similar:', filename1, filename2)
    print("Total similarity -", '{:.2%}'.format(total_similarity))
    print()
    print('Structure is same by {:.2%}'.format(metrics[0]))
    print(df, '\n')

    text = 'Operators match percentage:'
    print(text, '{:.2%}'.format(metrics[1]))
    text = 'Keywords match percentage:'
    print(text, '{:.2%}'.format(metrics[2]))
    text = 'Literals match percentage:'
    print(text, '{:.2%}'.format(metrics[3]))
    print('---')
    print('Op shift metric.')
    print('Best op shift:', best_shift)
    print('Persent same: {:.2%}'.format(metrics[4]))
    print('---')
    print('+' * 40)

# 0 mode works with GitHub repositoryes
# 1 mode works with directory in user computer

directory = 'py/'
if len(sys.argv) > 2:
    file_path = sys.argv[1]
    reg_exp = sys.argv[2]
    mode = 0
elif len(sys.argv) == 2:
    directory = sys.argv[1]
    mode = 1
    if not os.path.exists(directory):
        print('Directory isn\'t exist')
        exit()
elif len(sys.argv) == 1:
    exit()

start_eval = perf_counter()
weights = np.array([1.5, 0.8, 0.9, 0.5, 0.3], dtype=np.float32)
if mode == 0:
    try:
        with open(file_path) as f:
            tree1 = ast.parse(f.read())
    except PermissionError:
        print("File denied.")
        exit()
    except FileNotFoundError:
        print("File not found")
        exit()

    features1 = ASTFeatures()
    features1.visit(tree1)

    iteration = 0
    repos, repos_url = get_list_of_repos()
    repos, repos_url = select_repos(repos, repos_url, reg_exp)
    count_iter = len(repos)
    for repo_url in repos_url:
        url_files_in_repo = get_python_files_links(repo_url + '/contents')
        inner_iter = 0
        inner_iters = len(url_files_in_repo)
        for url_file in url_files_in_repo:
            try:
                tree2 = ast.parse(get_code(url_file))
            except:
                print('Not compiled: ', url_file)
                continue
            features2 = ASTFeatures()
            features2.visit(tree2)
            metrics, best_shift, matrix = run_compare(features1.structure,
                                                      features2.structure,
                                                      features1.operators,
                                                      features2.operators,
                                                      features1.keywords,
                                                      features2.keywords,
                                                      features1.literals,
                                                      features2.literals,
                                                      features1.seq_ops,
                                                      features2.seq_ops)
            total_similarity = np.sum(metrics * weights) / 4

            if total_similarity > 0.72:
                print_compare_res(metrics, total_similarity, best_shift,
                                  matrix, features1.structure,
                                  features2.structure, features1.from_num,
                                  features2.from_num, file_path.split('\\')[-1],
                                  url_file)

            inner_iter += 1
            print('In repo {:.2%}, In repos {:.2%}'.format(inner_iter / inner_iters,
                                                           iteration / count_iter), end="\r")
        iteration += 1
        print(" " * 40, end="\r")
        print('In repos {:.2%}'.format(iteration / count_iter), end="\r")
elif mode == 1:
    files = os.listdir(directory)
    files = list(filter(lambda x: (x.endswith('.py')), files))

    count_files = len(files)
    # date = datetime.datetime.now().strftime('%Y%m%d-%H#%M#%S')
    # log_file = open('./logs/pylog' + date + '.txt', 'w')

    iterrations = (count_files * count_files - count_files) / 2
    iterration = 0

    for row in np.arange(0, count_files, 1):
        if directory[-1] != '/':
            directory += '/'
        filename = directory + files[row]
        for col in np.arange(0, count_files, 1):
            filename2 = directory + files[col]
            if row == col:
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

            metrics, best_shift, matrix = run_compare(features1.structure,
                                                      features2.structure,
                                                      features1.operators,
                                                      features2.operators,
                                                      features1.keywords,
                                                      features2.keywords,
                                                      features1.literals,
                                                      features2.literals,
                                                      features1.seq_ops,
                                                      features2.seq_ops)
            total_similarity = np.sum(metrics * weights) / 4

            if total_similarity > 0.72:
                print_compare_res(metrics, total_similarity, best_shift,
                                  matrix, features1.structure,
                                  features2.structure, features1.from_num,
                                  features2.from_num, filename.split('/')[-1],
                                  filename2.split('/')[-1])

            iterration += 1
            print('  {:.2%}'.format(iterration / iterrations), end="\r")

    if count_files == 0:
        print("Folder is empty")

print("Analysis complete")
print('Time for all {:.2f}'.format(perf_counter() - start_eval))
# log_file.close()

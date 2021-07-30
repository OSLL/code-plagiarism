import context

import os
import numpy as np
import ast
import pandas as pd

from termcolor import colored
from src.pyplag.tfeatures import get_children_indexes, ASTFeatures
from src.pyplag.metric import counter_metric, struct_compare, op_shift_metric
from src.pyplag.metric import value_jakkar_coef, lcs


def get_ast_from_content(code, path):
    tree = None

    try:
        tree = ast.parse(code)
    except IndentationError as err:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored('IdentationError: ' + err.args[0], 'red'))
        print(colored('In line ' + str(err.args[1][1]), 'red'))
        print('-' * 40)
    except SyntaxError as err:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored('SyntaxError: ' + err.args[0], 'red'))
        print(colored('In line ' + str(err.args[1][1]), 'red'))
        print(colored('In column ' + str(err.args[1][2]), 'red'))
        print('-' * 40)
    except TabError as err:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored('TabError: ' + err.args[0], 'red'))
        print(colored('In line ' + str(err.args[1][1]), 'red'))
        print('-' * 40)
    except Exception as e:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored(e.__class__.__name__, 'red'))
        for el in e.args:
            print(colored(el, 'red'))
        print('-' * 40)

    return tree


def get_ast_from_filename(filename):
    '''
        Function return ast which has type ast.Module
        @param filename - full path to file with code which will have
        analyzed
    '''
    if type(filename) is not str:
        return TypeError

    if not os.path.isfile(filename):
        print(filename, "Is not a file / doesn't exist")
        return None

    tree = None
    try:
        with open(filename) as f:
            tree = get_ast_from_content(f.read(), filename)
    except PermissionError:
        print("File denied.")
    except FileNotFoundError:
        print("File not found")

    return tree


def run_compare(features_f, features_s):
    jakkar_coef = value_jakkar_coef(features_f.tokens, features_s.tokens)
    ops_res = counter_metric(features_f.operators, features_s.operators)
    kw_res = counter_metric(features_f.keywords, features_s.keywords)
    lits_res = counter_metric(features_f.literals, features_s.literals)

    metrics = np.array([jakkar_coef, ops_res, kw_res, lits_res],
                       dtype=np.float32)

    return metrics


def print_compare_res(metrics, total_similarity,
                      struct1, struct2, to_names1, to_names2,
                      seq_ops_f, seq_ops_s,
                      tokens_f, tokens_s,
                      filename1, filename2):
    ch_inds1, count_ch1 = get_children_indexes(struct1)
    ch_inds2, count_ch2 = get_children_indexes(struct2)
    compliance_matrix = np.zeros((count_ch1, count_ch2, 2), dtype=np.int64)
    struct_res = struct_compare(struct1, struct2,
                                compliance_matrix)
    struct_res = struct_res[0] / struct_res[1]
    best_shift, shift_res = op_shift_metric(seq_ops_f, seq_ops_s)

    print("         ")
    print('+' * 40)
    print('May be similar:', filename1, filename2, end='\n\n', sep='\n')
    main_metrics_df = pd.DataFrame()
    main_metrics_df.loc['Total match', 'Same'] = total_similarity
    main_metrics_df.loc['Jakkar coef', 'Same'] = metrics[0]
    main_metrics_df.loc['Operators match', 'Same'] = metrics[1]
    main_metrics_df.loc['Keywords match', 'Same'] = metrics[2]
    main_metrics_df.loc['Literals match', 'Same'] = metrics[3]

    print(main_metrics_df)
    print()
    additional_metrics_df = pd.DataFrame()
    additional_metrics_df.loc['Structure match', 'Same'] = struct_res
    additional_metrics_df.loc['Op shift match (max)', 'Same'] = shift_res
    additional_metrics_df.loc['LCS'] = (2 * lcs(tokens_f, tokens_s) /
                                        (len(tokens_f) + len(tokens_s)))
    print(additional_metrics_df)
    print()

    if struct_res > 0.75:
        indexes = [to_names1[struct1[ind][1]] for ind in ch_inds1]
        columns = [to_names2[struct2[ind][1]] for ind in ch_inds2]
        data = np.zeros((compliance_matrix.shape[0],
                         compliance_matrix.shape[1]),
                        dtype=np.float32)
        for row in range(compliance_matrix.shape[0]):
            for col in range(compliance_matrix.shape[1]):
                data[row][col] = (compliance_matrix[row][col][0] /
                                  compliance_matrix[row][col][1])
        df = pd.DataFrame(data=data,
                          index=indexes, columns=columns)

        print(df, '\n')

    print('+' * 40)


def compare_file_pair(filename, filename2, threshold, weights):
    '''
        Function compares 2 files
        filename - path to the first file (dir/file1.py)
        filename2 - path the second file (dir/file2.py)
    '''
    tree1 = get_ast_from_filename(filename)
    tree2 = get_ast_from_filename(filename2)

    if tree1 is None:
        return
    if tree2 is None:
        return

    features1 = ASTFeatures()
    features2 = ASTFeatures()
    features1.visit(tree1)
    features2.visit(tree2)

    metrics = run_compare(features1, features2)
    total_similarity = np.sum(metrics * weights) / weights.sum()

    if (total_similarity * 100) > threshold:
        print_compare_res(metrics, total_similarity,
                          features1.structure,
                          features2.structure,
                          features1.from_num,
                          features2.from_num,
                          features1.seq_ops,
                          features2.seq_ops,
                          features1.tokens,
                          features2.tokens,
                          filename.split('/')[-1],
                          filename2.split('/')[-1])

    return (metrics, total_similarity)


def get_files_path_from_directory(directory):
    cur_dir_files = os.listdir(directory)
    allowed_files = []
    for file in cur_dir_files:
        path = directory + '/' + file
        if file.endswith('.py'):
            allowed_files.append(path)
        elif os.path.isdir(path):
            allowed_files.extend(get_files_path_from_directory(path))

    return allowed_files

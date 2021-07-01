import context

import os
import numpy as np
import ast
import pandas as pd

from termcolor import colored
from src.pyplag.tfeatures import get_children_ind
from src.pyplag.metric import nodes_metric, struct_compare, op_shift_metric
from src.pyplag.metric import value_jakkar_coef
from numba import njit


def get_AST(filename):
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
            try:
                tree = ast.parse(f.read())
            except IndentationError as err:
                print('-' * 40)
                print(colored('Not compiled: ' + filename, 'red'))
                print(colored('IdentationError: ' + err.args[0], 'red'))
                print(colored('In line ' + str(err.args[1][1]), 'red'))
                print('-' * 40)
            except SyntaxError as err:
                print('-' * 40)
                print(colored('Not compiled: ' + filename, 'red'))
                print(colored('SyntaxError: ' + err.args[0], 'red'))
                print(colored('In line ' + str(err.args[1][1]), 'red'))
                print(colored('In column ' + str(err.args[1][2]), 'red'))
                print('-' * 40)
            except TabError as err:
                print('-' * 40)
                print(colored('Not compiled: ' + filename, 'red'))
                print(colored('TabError: ' + err.args[0], 'red'))
                print(colored('In line ' + str(err.args[1][1]), 'red'))
                print('-' * 40)
            except Exception as e:
                print('-' * 40)
                print(colored('Not compiled: ' + filename, 'red'))
                print(colored(e.__class__.__name__, 'red'))
                for el in e.args:
                    print(colored(el, 'red'))
                print('-' * 40)
    except PermissionError:
        print("File denied.")
    except FileNotFoundError:
        print("File not found")

    return tree


def run_compare(features_f, features_s):
    jakkar_coef = value_jakkar_coef(features_f.tokens, features_s.tokens)
    ops_res = nodes_metric(features_f.operators, features_s.operators)
    kw_res = nodes_metric(features_f.keywords, features_s.keywords)
    lits_res = nodes_metric(features_f.literals, features_s.literals)

    metrics = np.array([jakkar_coef, ops_res, kw_res, lits_res],
                       dtype=np.float32)

    return metrics


def print_compare_res(metrics, total_similarity,
                      struct1, struct2, to_names1, to_names2,
                      seq_ops_f, seq_ops_s,
                      filename1, filename2):
    ch_inds1, count_ch1 = get_children_ind(struct1, len(struct1))
    ch_inds2, count_ch2 = get_children_ind(struct2, len(struct2))
    compliance_matrix = np.zeros((count_ch1, count_ch2, 2), dtype=np.int64)
    struct_res = struct_compare(struct1, struct2,
                                compliance_matrix)
    struct_res = struct_res[0] / struct_res[1]
    best_shift, shift_res = op_shift_metric(seq_ops_f, seq_ops_s)

    print("         ")
    print('+' * 40)
    print('May be similar:', filename1, filename2, end='\n\n')
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
    print(additional_metrics_df)
    print()

    if struct_res > 0.75:
        indexes = [to_names1[struct1[ind][1]] for ind in ch_inds1]
        columns = [to_names2[struct2[ind][1]] for ind in ch_inds2]
        data = np.zeros((compliance_matrix.shape[0], compliance_matrix.shape[1]),
                        dtype=np.float32)
        for row in range(compliance_matrix.shape[0]):
            for col in range(compliance_matrix.shape[1]):
                data[row][col] = (compliance_matrix[row][col][0] /
                                  compliance_matrix[row][col][1])
        df = pd.DataFrame(data=data,
                          index=indexes, columns=columns)

        print(df, '\n')

    print('+' * 40)

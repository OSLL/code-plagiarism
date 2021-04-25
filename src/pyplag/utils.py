import context

import os
import numpy as np
import ast
import pandas as pd

from termcolor import colored
from src.pyplag.tfeatures import get_children_ind
from src.pyplag.metric import nodes_metric, struct_compare, op_shift_metric
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
        exit()
    except FileNotFoundError:
        print("File not found")
        exit()

    return tree


@njit
def run_compare(f_struct, s_struct, f_ops, s_ops,
                f_kw, s_kw, f_lits, s_lits, f_seq_ops, s_seq_ops):
    count_ch1 = (get_children_ind(f_struct, len(f_struct)))[1]
    count_ch2 = (get_children_ind(s_struct, len(s_struct)))[1]
    compliance_matrix = np.zeros((count_ch1, count_ch2, 2), dtype=np.int32)

    struct_res = struct_compare(f_struct, s_struct, compliance_matrix)
    struct_res = struct_res[0] / struct_res[1]
    ops_res = nodes_metric(f_ops, s_ops)
    kw_res = nodes_metric(f_kw, s_kw)
    lits_res = nodes_metric(f_lits, s_lits)
    best_shift, shift_res = op_shift_metric(f_seq_ops, s_seq_ops)

    metrics = np.array([struct_res, ops_res, kw_res, lits_res, shift_res],
                       dtype=np.float32)

    return metrics, best_shift, compliance_matrix


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

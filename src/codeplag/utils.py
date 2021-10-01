import os
import re
import numpy as np
import pandas as pd

from codeplag.algorithms.featurebased import (
    counter_metric, struct_compare
)
from codeplag.algorithms.tokenbased import value_jakkar_coef


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def run_compare(features_f, features_s):
    """The function calculates the similarity of features of two programmes
    using four algorithms and returns similarity coefficients.

    @features_f - the features of the first  source file
    @features_s - the features of the second  source file
    """

    jakkar_coef = value_jakkar_coef(features_f.tokens, features_s.tokens)
    ops_res = counter_metric(features_f.operators, features_s.operators)
    kw_res = counter_metric(features_f.keywords, features_s.keywords)
    lits_res = counter_metric(features_f.literals, features_s.literals)

    metrics = np.array([jakkar_coef, ops_res, kw_res, lits_res],
                       dtype=np.float32)

    return metrics


def print_compare_res(features1, features2, threshold=60,
                      weights=np.array([1, 0.4, 0.4, 0.4],
                                       dtype=np.float32)):
    """The function prints the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @threshold - threshold of plagiarism searcher alarm
    @weights - weights of metrics that participate in
    counting total similarity coefficient
    """

    metrics = run_compare(features1, features2)
    total_similarity = np.sum(metrics * weights) / weights.sum()
    if (total_similarity * 100) < threshold:
        return

    compliance_matrix = np.zeros((len(features1.head_nodes),
                                  len(features2.head_nodes), 2),
                                 dtype=np.int64)
    struct_res = struct_compare(features1.structure, features2.structure,
                                compliance_matrix)
    struct_res = struct_res[0] / struct_res[1]

    print("         ")
    print('+' * 40)
    print('May be similar:', features1.filepath, features2.filepath,
          end='\n\n', sep='\n')
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
    print(additional_metrics_df)
    print()

    if (struct_res * 100) > threshold:
        data = np.zeros((compliance_matrix.shape[0],
                         compliance_matrix.shape[1]),
                        dtype=np.float32)
        for row in range(compliance_matrix.shape[0]):
            for col in range(compliance_matrix.shape[1]):
                data[row][col] = (compliance_matrix[row][col][0] /
                                  compliance_matrix[row][col][1])
        df = pd.DataFrame(data=data,
                          index=features1.head_nodes,
                          columns=features2.head_nodes)

        print(df, '\n')

    print('+' * 40)


def get_files_path_from_directory(directory, extension=r".*\b"):
    '''
        The function returns paths to all files in the directory
        and its subdirectories which have the extension transmitted
        in arguments
    '''
    allowed_files = []
    for current_dir, folders, files in os.walk(directory):
        for file in files:
            if re.search(extension, file) is not None:
                allowed_files.append(os.path.join(current_dir, file))

    return allowed_files


def print_suspect_parts(source_code, marked_tokens, tokens_pos,
                        color=Colors.FAIL):
    ROWS = {row for (row, column) in
            [tokens_pos[index] for index in marked_tokens]}

    row = 1
    column = 1

    for symbol in source_code:
        if symbol == '\n':
            row += 1
            column = 1

        if row in ROWS:
            print(color + symbol, end=Colors.ENDC)

        column += 1


def print_code_and_highlight_suspect(source_code, marked_tokens, tokens_pos,
                                     color=Colors.FAIL):
    ROWS = {row for (row, column) in
            [tokens_pos[index] for index in marked_tokens]}

    row = 1
    column = 1

    for symbol in source_code:
        if symbol == '\n':
            row += 1
            column = 1

        if row in ROWS:
            print(color + symbol, end=Colors.ENDC)
        else:
            print(symbol, end="")

        column += 1

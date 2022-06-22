import os
import re

import numpy as np
import pandas as pd

from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.astfeatures import ASTFeatures


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


def fast_compare(features_f: ASTFeatures,
                 features_s: ASTFeatures,
                 weights: tuple = (1, 0.4, 0.4, 0.4)) -> np.array:
    """The function calculates the similarity of features of two programmes
    using four algorithms and returns similarity coefficients.

    @features_f - the features of the first  source file
    @features_s - the features of the second  source file
    @weights - weights of fast metrics that participate in
    counting total similarity coefficient
    """

    jakkar_coef = value_jakkar_coef(features_f.tokens, features_s.tokens)
    ops_res = counter_metric(features_f.operators, features_s.operators)
    kw_res = counter_metric(features_f.keywords, features_s.keywords)
    lits_res = counter_metric(features_f.literals, features_s.literals)

    fast_metrics = {
        'Jakkar': jakkar_coef,
        'Operators': ops_res,
        'Keywords': kw_res,
        'Literals': lits_res
    }
    weighted_average = np.average(
        [jakkar_coef, ops_res, kw_res, lits_res],
        weights=weights
    )
    fast_metrics['WeightedAverage'] = weighted_average

    return fast_metrics


def compare_works(features1: ASTFeatures,
                  features2: ASTFeatures,
                  threshold: int = 60) -> dict:
    """The function returns the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @threshold - threshold of plagiarism searcher alarm
    """

    metrics = {}
    fast_metrics = fast_compare(features1, features2)
    metrics['fast'] = fast_metrics
    if (metrics['fast']['WeightedAverage'] * 100) < threshold:
        return metrics

    compliance_matrix = np.zeros(
        (len(features1.head_nodes), len(features2.head_nodes), 2),
        dtype=np.int64
    )
    struct_res = struct_compare(features1.structure, features2.structure,
                                compliance_matrix)
    struct_res = struct_res[0] / struct_res[1]

    metrics['structure'] = {
        'similarity': struct_res,
        'matrix': compliance_matrix
    }

    return metrics


def print_compare_result(features1: ASTFeatures,
                         features2: ASTFeatures,
                         metrics: dict,
                         threshold: int = 60) -> None:
    """The function prints the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @metrics - dictionary with fast and structure metrics information
    @threshold - threshold of plagiarism searcher alarm
    """

    print(" " * 40)
    print('+' * 40)
    print(
        'May be similar:',
        features1.filepath,
        features2.filepath,
        end='\n\n', sep='\n'
    )
    main_metrics_df = pd.DataFrame(
        metrics['fast'], index=['Similarity'],
        columns=pd.Index(
            metrics['fast'].keys(),
            name='FastMetrics:'
        )
    )
    print(main_metrics_df)
    print()

    additional_metrics_df = pd.DataFrame(
        metrics['structure']['similarity'], index=['Similarity'],
        columns=pd.Index(
            ['Structure'],
            name='AdditionalMetrics:'
        )
    )
    print(additional_metrics_df)
    print()

    if (metrics['structure']['similarity'] * 100) > threshold:
        data = np.zeros(
            (
                metrics['structure']['matrix'].shape[0],
                metrics['structure']['matrix'].shape[1]
            ),
            dtype=np.float64
        )
        for row in range(metrics['structure']['matrix'].shape[0]):
            for col in range(metrics['structure']['matrix'].shape[1]):
                data[row][col] = (
                    metrics['structure']['matrix'][row][col][0] /
                    metrics['structure']['matrix'][row][col][1]
                )
        df = pd.DataFrame(data=data,
                          index=features1.head_nodes,
                          columns=features2.head_nodes)

        print(df, '\n')

    print('+' * 40)


def get_files_path_from_directory(directory: str,
                                  extensions: list = None):
    '''
        The function returns paths to all files in the directory
        and its subdirectories which have the extension transmitted
        in arguments
    '''
    if not extensions:
        extensions = [r".*\b"]

    allowed_files = []
    for current_dir, _folders, files in os.walk(directory):
        for file in files:
            allowed = False
            for extension in extensions:
                if re.search(extension, file):
                    allowed = True

                    break
            if allowed:
                allowed_files.append(os.path.join(current_dir, file))

    return allowed_files


def print_suspect_parts(source_code: str,
                        marked_tokens,
                        tokens_pos,
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


def print_code_and_highlight_suspect(source_code: str,
                                     marked_tokens,
                                     tokens_pos,
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

import numpy as np
import pandas as pd

from codeplag.algorithms.featurebased import (
    counter_metric, struct_compare
)
from codeplag.algorithms.tokenbased import value_jakkar_coef, lcs_based_coeff


def run_compare(features_f, features_s):
    jakkar_coef = value_jakkar_coef(features_f.tokens, features_s.tokens)
    ops_res = counter_metric(features_f.operators, features_s.operators)
    kw_res = counter_metric(features_f.keywords, features_s.keywords)
    lits_res = counter_metric(features_f.literals, features_s.literals)

    metrics = np.array([jakkar_coef, ops_res, kw_res, lits_res],
                       dtype=np.float32)

    return metrics


def print_compare_res(metrics, total_similarity,
                      features1, features2):
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
    additional_metrics_df.loc['LCS'] = lcs_based_coeff(features1.tokens,
                                                       features2.tokens)
    print(additional_metrics_df)
    print()

    if struct_res > 0.75:
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

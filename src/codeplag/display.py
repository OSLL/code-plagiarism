from enum import Enum
from functools import partial
from typing import List

import numpy as np
import pandas as pd

from codeplag.types import ASTFeatures, CompareInfo, NodeCodePlace


class Color(Enum):
    HEADER: str = '\033[95m'
    OKBLUE: str = '\033[94m'
    OKCYAN: str = '\033[96m'
    OKGREEN: str = '\033[92m'
    WARNING: str = '\033[93m'
    FAIL: str = '\033[91m'
    BOLD: str = '\033[1m'
    UNDERLINE: str = '\033[4m'
    END: str = '\033[0m'


def colorize(text: str, color: Color,
             bold: bool = False, underline: bool = False) -> str:
    if bold:
        text = f"{Color.BOLD.value}{text}"
    if underline:
        text = f"{Color.UNDERLINE.value}{text}"

    return f"{color.value}{text}{Color.END.value}"


red_bold = partial(colorize, color=Color.FAIL, bold=True)


def print_suspect_parts(source_code: str,
                        marked_tokens: List[int],
                        tokens_pos: List[NodeCodePlace]) -> None:
    ROWS = {
        row for (row, _column) in
        [tokens_pos[index] for index in marked_tokens]
    }

    row = 1
    column = 1  # noqa

    for symbol in source_code:
        if symbol == '\n':
            row += 1
            column = 1

        if row in ROWS:
            print(red_bold(symbol))

        column += 1


def print_code_and_highlight_suspect(source_code: str,
                                     marked_tokens: List[int],
                                     tokens_pos: List[NodeCodePlace]) -> None:
    ROWS = {row for (row, column) in
            [tokens_pos[index] for index in marked_tokens]}

    row = 1
    column = 1  # noqa

    for symbol in source_code:
        if symbol == '\n':
            row += 1
            column = 1

        if row in ROWS:
            print(red_bold(symbol))
        else:
            print(symbol, end="")

        column += 1


def print_compare_result(features1: ASTFeatures,
                         features2: ASTFeatures,
                         compare_info: CompareInfo,
                         threshold: int = 60) -> None:
    """The function prints the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @compare_info - structure consist compare metrics of two works
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
        [compare_info.fast], index=['Similarity'],
        columns=pd.Index(
            (field.upper() for field in compare_info.fast._fields),
            name='FastMetrics:'
        )
    )
    print(main_metrics_df)
    print()

    additional_metrics_df = pd.DataFrame(
        compare_info.structure.similarity, index=['Similarity'],
        columns=pd.Index(
            ['Structure'],
            name='AdditionalMetrics:'
        )
    )
    print(additional_metrics_df)
    print()

    if (compare_info.structure.similarity * 100) > threshold:
        data = np.zeros(
            (
                compare_info.structure.compliance_matrix.shape[0],
                compare_info.structure.compliance_matrix.shape[1]
            ),
            dtype=np.float64
        )
        for row in range(
            compare_info.structure.compliance_matrix.shape[0]
        ):
            for col in range(
                compare_info.structure.compliance_matrix.shape[1]
            ):
                data[row][col] = (
                    compare_info.structure.compliance_matrix[row][col][0]
                    / compare_info.structure.compliance_matrix[row][col][1]
                )
        compliance_matrix_df = pd.DataFrame(
            data=data,
            index=features1.head_nodes,
            columns=features2.head_nodes
        )

        print(compliance_matrix_df, '\n')

    print('+' * 40)

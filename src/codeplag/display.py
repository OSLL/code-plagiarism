from enum import Enum
from functools import partial
from typing import List, Optional

import pandas as pd

from codeplag.types import ASTFeatures, CompareInfo, NodeCodePlace


class Color(Enum):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def colorize(
    text: str, color: Color, bold: bool = False, underline: bool = False
) -> str:
    if bold:
        text = f"{Color.BOLD.value}{text}"
    if underline:
        text = f"{Color.UNDERLINE.value}{text}"

    return f"{color.value}{text}{Color.END.value}"


info = partial(colorize, color=Color.OKGREEN)
warning = partial(colorize, color=Color.WARNING)
error = partial(colorize, color=Color.FAIL)
red_bold = partial(colorize, color=Color.FAIL, bold=True)


def print_suspect_parts(
    source_code: str, marked_tokens: List[int], tokens_pos: List[NodeCodePlace]
) -> None:
    ROWS = {row for (row, _column) in [tokens_pos[index] for index in marked_tokens]}

    row = 1
    column = 1  # noqa

    for symbol in source_code:
        if symbol == "\n":
            row += 1
            column = 1

        if row in ROWS:
            print(red_bold(symbol))

        column += 1


def print_code_and_highlight_suspect(
    source_code: str, marked_tokens: List[int], tokens_pos: List[NodeCodePlace]
) -> None:
    ROWS = {row for (row, column) in [tokens_pos[index] for index in marked_tokens]}

    row = 1
    column = 1  # noqa

    for symbol in source_code:
        if symbol == "\n":
            row += 1
            column = 1

        if row in ROWS:
            print(red_bold(symbol))
        else:
            print(symbol, end="")

        column += 1


def print_compare_result(
    features1: ASTFeatures,
    features2: ASTFeatures,
    compare_info: CompareInfo,
    compliance_matrix_df: Optional[pd.DataFrame] = None,
) -> None:
    """The function prints the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @compare_info - structure consist compare metrics of two works
    @threshold - threshold of plagiarism searcher alarm
    """

    print(" " * 40)
    print("+" * 40)
    if features1.modify_date is not None and features2.modify_date is not None:
        message = (
            "-----\n"
            f"{features1.filepath}\n{features1.modify_date}\n"
            "-----\n"
            f"{features2.filepath}\n{features2.modify_date}\n"
            "-----\n"
        )
    else:
        message = f"{features1.filepath}\n{features2.filepath}\n"

    print("May be similar:", message, end="\n\n", sep="\n")
    main_metrics_df = pd.DataFrame(
        [compare_info.fast],
        index=["Similarity"],
        columns=pd.Index(
            (field.upper() for field in compare_info.fast._fields), name="FastMetrics:"
        ),
    )
    print(main_metrics_df)
    print()

    if compare_info.structure is None:
        return

    additional_metrics_df = pd.DataFrame(
        compare_info.structure.similarity,
        index=["Similarity"],
        columns=pd.Index(["Structure"], name="AdditionalMetrics:"),
    )
    print(additional_metrics_df)
    print()

    if compliance_matrix_df is not None:
        print(compliance_matrix_df, "\n")

    print("+" * 40)

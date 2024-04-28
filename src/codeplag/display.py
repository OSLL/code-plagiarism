from datetime import timedelta
from enum import Enum
from functools import partial
from time import monotonic
from typing import Final, List, Optional

import pandas as pd
from typing_extensions import Self

from codeplag.types import ASTFeatures, CompareInfo, NodeCodePlace

CHARS_CNT: Final[int] = 40
USEFUL_CHARS: Final[int] = 100


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


class Progress:
    def __init__(self, iterations: int) -> None:
        self.__iterations: Final[int] = iterations
        self.__iteration: int = -1
        self.__start_time_sec = monotonic()

    @property
    def progress(self) -> float:
        if self.iterations == 0:
            return 1.0
        if self.__iteration <= 0:
            return 0.0
        return self.__iteration / self.iterations

    @property
    def start_time_sec(self) -> float:
        return self.__start_time_sec

    @property
    def iterations(self) -> int:
        return self.__iterations if self.__iterations > 0 else 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> float:
        if self.progress == 1.0:
            raise StopIteration("The progress has already been completed.")
        self.__iteration += 1
        return self.progress

    def __str__(self) -> str:
        return f"Progress: {self.progress:.2%}"


class ComplexProgress(Progress):
    def __init__(self, iterations: int) -> None:
        super(ComplexProgress, self).__init__(iterations)
        self.__internal_progresses: List[Progress] = []

    def add_internal_progress(self, internal_iterations: int) -> None:
        if len(self.__internal_progresses) == self.iterations:
            raise IndexError("The internal iteration count limit was exceeded.")
        self.__internal_progresses.append(Progress(internal_iterations))

    @property
    def progress(self) -> float:
        if self.iterations == 0:
            return 1.0
        return float(
            sum(
                internal_progress.progress / self.iterations
                for internal_progress in self.__internal_progresses
            )
        )

    def __next__(self) -> float:
        if self.progress == 1.0:
            raise StopIteration("The progress has already been completed.")
        for internal_progress in self.__internal_progresses:
            if internal_progress.progress == 1.0:
                continue
            if next(internal_progress) == 1.0:
                continue
            break
        return self.progress


def colorize(
    text: str, color: Color, bold: bool = False, underline: bool = False
) -> str:
    """Wraps provided text to change color, bold, or underline it for printing."""
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


def clear_line() -> None:
    print(" " * USEFUL_CHARS, end="\r")


def print_compare_result(
    features1: ASTFeatures,
    features2: ASTFeatures,
    compare_info: CompareInfo,
    compliance_matrix_df: Optional[pd.DataFrame] = None,
) -> None:
    """Prints the pretty result of comparing two files.

    Args:
        features1: The features of the first  source file.
        features2: The features of the second  source file.
        compare_info: The compare metrics of two works.
        threshold: Threshold of plagiarism searcher alarm.
    """

    clear_line()
    print("+" * CHARS_CNT)
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

    print("+" * CHARS_CNT)


def print_pretty_progress(progress: Progress, workers: int) -> None:
    time_spent_seconds = monotonic() - progress.start_time_sec
    time_spent = timedelta(seconds=int(time_spent_seconds))
    current_progress = progress.progress
    if current_progress != 0.0:
        predicated_time_left = timedelta(
            seconds=int(
                (1.0 - current_progress) / current_progress * time_spent_seconds
            )
        )
    else:
        predicated_time_left = "N/A"
    print(
        f"{progress}, "
        f"{time_spent} time spent [predicted time left {predicated_time_left}], "
        f"{workers} workers",
        end="\r",
    )

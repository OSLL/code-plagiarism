from datetime import timedelta
from enum import Enum
from functools import partial
from time import monotonic
from typing import Final

import numpy as np
import pandas as pd
from typing_extensions import Self

from codeplag.types import FullCompareInfo, NodeCodePlace

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
    def __init__(self: Self, iterations: int) -> None:
        self.__iterations: Final[int] = iterations
        self.__iteration: int = -1
        self.__start_time_sec = monotonic()

    @property
    def progress(self: Self) -> float:
        if self.iterations == 0:
            return 1.0
        if self.__iteration <= 0:
            return 0.0
        return self.__iteration / self.iterations

    @property
    def start_time_sec(self: Self) -> float:
        return self.__start_time_sec

    @property
    def iterations(self: Self) -> int:
        return self.__iterations if self.__iterations > 0 else 0

    def __iter__(self: Self) -> Self:
        return self

    def __next__(self: Self) -> float:
        if self.progress == 1.0:
            raise StopIteration("The progress has already been completed.")
        self.__iteration += 1
        return self.progress

    def __str__(self: Self) -> str:
        return f"Progress: {self.progress:.2%}"


class ComplexProgress(Progress):
    def __init__(self: Self, iterations: int) -> None:
        super(ComplexProgress, self).__init__(iterations)
        self.__internal_progresses: list[Progress] = []

    def add_internal_progress(self: Self, internal_iterations: int) -> None:
        if len(self.__internal_progresses) == self.iterations:
            raise IndexError("The internal iteration count limit was exceeded.")
        self.__internal_progresses.append(Progress(internal_iterations))

    @property
    def progress(self: Self) -> float:
        if self.iterations == 0:
            return 1.0
        return float(
            sum(
                internal_progress.progress / self.iterations
                for internal_progress in self.__internal_progresses
            )
        )

    def __next__(self: Self) -> float:
        if self.progress == 1.0:
            raise StopIteration("The progress has already been completed.")
        for internal_progress in self.__internal_progresses:
            if internal_progress.progress == 1.0:
                continue
            if next(internal_progress) == 1.0:
                continue
            break
        return self.progress


def colorize(text: str, color: Color, bold: bool = False, underline: bool = False) -> str:
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
    source_code: str, marked_tokens: list[int], tokens_pos: list[NodeCodePlace]
) -> None:
    ROWS = {row for (row, _column) in [tokens_pos[index] for index in marked_tokens]}

    row = 1
    column = 1  # noqa

    for symbol in source_code:
        if symbol == "\n":
            row += 1
            column = 1

        if row in ROWS:
            print(red_bold(symbol), end="")

        column += 1


def print_code_and_highlight_suspect(
    source_code: str, marked_tokens: list[int], tokens_pos: list[NodeCodePlace]
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
    compare_info: FullCompareInfo,
    compliance_matrix_df: pd.DataFrame | None = None,
) -> None:
    """Prints the pretty result of comparing two files.

    Args:
    ----
        compare_info (FullCompareInfo): The compare metrics of two works.
        compliance_matrix_df (pd.DataFrame | None, optional): DataFrame consisting
          structures similarity information of two works.

    """
    clear_line()
    print("+" * CHARS_CNT)
    message = (
        "-----\n"
        f"{compare_info.first_path}\n{compare_info.first_modify_date}\n"
        "-----\n"
        f"{compare_info.first_path}\n{compare_info.first_modify_date}\n"
        "-----\n"
    )

    print("May be similar:", message, end="\n\n", sep="\n")
    main_metrics_df = pd.DataFrame(
        [compare_info.fast],
        index=np.array(["Similarity"]),
        columns=pd.Index(
            (field.upper() for field in compare_info.fast._fields), name="FastCompareInfo:"
        ),
    )
    print(main_metrics_df)
    print()

    additional_metrics_df = pd.DataFrame(
        compare_info.structure.similarity,
        index=np.array(["Similarity"]),
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
            seconds=int((1.0 - current_progress) / current_progress * time_spent_seconds)
        )
    else:
        predicated_time_left = "N/A"
    print(
        f"{progress}, "
        f"{time_spent} time spent [predicted time left {predicated_time_left}], "
        f"{workers} workers",
        end="\r",
    )

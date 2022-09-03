from enum import Enum
from functools import partial
from typing import List

from codeplag.types import NodeCodePlace


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
             bold: bool = False, underline: bool = False):
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

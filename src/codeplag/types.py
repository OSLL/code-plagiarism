import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from functools import total_ordering
from pathlib import Path
from typing import (
    DefaultDict,
    Literal,
    NamedTuple,
    Pattern,
    TypedDict,
)

import numpy.typing as npt
from typing_extensions import NotRequired, Self

Extension = Literal["py", "cpp"]
Extensions = tuple[Pattern, ...]
Flag = Literal[0, 1]
MaxDepth = Literal[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 999]
Mode = Literal["many_to_many", "one_to_one"]
NgramsLength = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ReportsExtension = Literal["csv", "mongo"]
ReportType = Literal["general", "sources"]
Language = Literal["en", "ru"]
LogLevel = Literal["trace", "debug", "info", "warning", "error"]
# fmt: off
Threshold = Literal[
    50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
    60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
    70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99
]
# fmt: on

# ----------------------------------------------------------------------------
# AST


class NodeCodePlace(NamedTuple):
    lineno: int
    col_offset: int


class NodeStructurePlace(NamedTuple):
    depth: int
    uid: int


def __return_zero() -> Literal[0]:
    return 0


def _create_a_defaultdict_returning_zero_by_default() -> DefaultDict[str, int]:
    return defaultdict(__return_zero)


@total_ordering
@dataclass
class ASTFeatures:
    """Class contains the source code metadata."""

    filepath: Path | str
    sha256: str = ""

    count_of_nodes: int = 0
    head_nodes: list[str] = field(default_factory=list)
    operators: DefaultDict[str, int] = field(
        default_factory=_create_a_defaultdict_returning_zero_by_default
    )
    keywords: DefaultDict[str, int] = field(
        default_factory=_create_a_defaultdict_returning_zero_by_default
    )
    literals: DefaultDict[str, int] = field(
        default_factory=_create_a_defaultdict_returning_zero_by_default
    )

    # unique nodes
    unodes: dict[str, int] = field(default_factory=dict)
    from_num: dict[int, str] = field(default_factory=dict)
    count_unodes: int = 0

    structure: list[NodeStructurePlace] = field(default_factory=list)
    tokens: list[int] = field(default_factory=list)
    tokens_pos: list[NodeCodePlace] = field(default_factory=list)

    def __post_init__(self: Self) -> None:
        if isinstance(self.filepath, Path) and self.filepath.exists():
            self.modify_date = datetime.fromtimestamp(self.filepath.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            self.modify_date = ""

    def __eq__(self: Self, other: "ASTFeatures") -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return str(self.filepath) == str(other.filepath)

    def __lt__(self: Self, other: "ASTFeatures") -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return str(self.filepath) < str(other.filepath)

    def get_sha256(self: Self) -> str:
        return hashlib.sha256(str(self.tokens).encode("utf-8")).hexdigest()


class NodeStructurePlaceDict(TypedDict):
    depth: int
    uid: int


class NodeCodePlaceDict(TypedDict):
    lineno: int
    col_offset: int


class ASTFeaturesDict(TypedDict):
    filepath: str
    sha256: str
    count_of_nodes: int
    head_nodes: list[str]
    operators: dict[str, int]
    keywords: dict[str, int]
    literals: dict[str, int]
    unodes: dict[str, int]
    from_num: dict[str, str]
    count_unodes: int
    structure: list[NodeStructurePlaceDict]
    tokens: list[int]
    tokens_pos: list[NodeCodePlaceDict]
    modify_date: str


# ----------------------------------------------------------------------------
# Compare information


class FastCompareInfo(NamedTuple):
    jakkar: float
    operators: float
    keywords: float
    literals: float
    weighted_average: float


class StructureCompareInfo(NamedTuple):
    similarity: float
    compliance_matrix: npt.NDArray


class FullCompareInfo(NamedTuple):
    fast: FastCompareInfo
    structure: StructureCompareInfo


# Exceptions and errors
# ----------------------------------------------------------------------------


class CLIException(Exception):
    """A common exception occurred while using CLI."""


class ExitCode(IntEnum):
    EXIT_SUCCESS = 0
    EXIT_KEYBOARD = 1
    EXIT_PARSER = 2
    EXIT_INVAL = 3
    EXIT_UNKNOWN = 5
    # Exit codes that are 200 or greater are auxiliary codes.
    EXIT_FOUND_SIM = 200


class ShortOutput(IntEnum):
    SHOW_ALL = 0
    SHOW_NEW = 1
    NO_SHOW = 2


# Misc
# ----------------------------------------------------------------------------


class Settings(TypedDict):
    environment: NotRequired[Path]
    language: Language
    log_level: LogLevel
    reports: NotRequired[Path]
    reports_extension: ReportsExtension
    show_progress: Flag
    short_output: ShortOutput
    max_depth: MaxDepth
    ngrams_length: NgramsLength
    threshold: Threshold
    workers: int
    mongo_host: str
    mongo_port: int
    mongo_user: str
    mongo_pass: NotRequired[str]


class SameHead(NamedTuple):
    name: str
    percent: float


class ProcessingWorks(NamedTuple):
    work1: ASTFeatures
    work2: ASTFeatures


SameFuncs = dict[str, list[SameHead]]


# Problem title: Pickling of a namedtuple instance succeeds normally,
# but fails when module is Cythonized.
# -----
# In order for pickle to work, the attribute __module__ of the some type must
# be set and should be correct.
# namedtuple uses a trick/heuristic (i.e lookup in sys._getframe(1).f_globals)
# to get this information. The problem with the Cython- or C-extensions is that,
# this heuristic will not work and _sys._getframe(1).f_globals.get('__name__', '__main__')
# will yield importlib._bootstrap and not correct module.
# To fix that you need to pass right module-name to namedtuple-factory
NodeCodePlace.__module__ = __name__
NodeStructurePlace.__module__ = __name__
FastCompareInfo.__module__ = __name__
StructureCompareInfo.__module__ = __name__
FullCompareInfo.__module__ = __name__

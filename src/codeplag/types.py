from collections import defaultdict
from concurrent.futures import Future
from dataclasses import dataclass, field
from functools import total_ordering
from pathlib import Path
from typing import (
    DefaultDict,
    Dict,
    List,
    Literal,
    NamedTuple,
    Optional,
    Pattern,
    Tuple,
    TypedDict,
    Union,
)

import numpy.typing as npt
from typing_extensions import NotRequired

Extension = Literal["py", "cpp"]
Extensions = Tuple[Pattern, ...]
Flag = Literal[0, 1]
Mode = Literal["many_to_many", "one_to_one"]
ReportsExtension = Literal["json", "csv"]
Language = Literal["en", "ru"]
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

    filepath: Union[Path, str]
    modify_date: Optional[str] = None

    count_of_nodes: int = 0
    head_nodes: List[str] = field(default_factory=list)
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
    unodes: Dict[str, int] = field(default_factory=dict)
    from_num: Dict[int, str] = field(default_factory=dict)
    count_unodes: int = 0

    structure: List[NodeStructurePlace] = field(default_factory=list)
    tokens: List[int] = field(default_factory=list)
    tokens_pos: List[NodeCodePlace] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return str(self.filepath) == str(other.filepath)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return str(self.filepath) < str(other.filepath)


# ----------------------------------------------------------------------------
# Compare information


class FastMetrics(NamedTuple):
    jakkar: float
    operators: float
    keywords: float
    literals: float
    weighted_average: float


class StructuresInfo(NamedTuple):
    similarity: float
    compliance_matrix: npt.NDArray


class CompareInfo(NamedTuple):
    fast: FastMetrics
    structure: Optional[StructuresInfo] = None


# TODO: Rework it structure
class WorksReport(TypedDict):
    date: str
    first_path: str
    second_path: str
    first_modify_date: NotRequired[str]
    second_modify_date: NotRequired[str]
    first_heads: List[str]
    second_heads: List[str]
    fast: Dict[str, int]  # dict from FastMetrics
    structure: dict  # dict from StructuresInfo


# Misc
# ----------------------------------------------------------------------------


class Settings(TypedDict):
    environment: NotRequired[Path]
    language: Language
    reports: NotRequired[Path]
    reports_extension: ReportsExtension
    show_progress: Flag
    threshold: Threshold
    workers: int


class SameHead(NamedTuple):
    name: str
    percent: float


class ProcessingWorksInfo(NamedTuple):
    work1: ASTFeatures
    work2: ASTFeatures
    compare_future: Future


SameFuncs = Dict[str, List[SameHead]]


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
FastMetrics.__module__ = __name__
StructuresInfo.__module__ = __name__
CompareInfo.__module__ = __name__

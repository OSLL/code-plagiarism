from collections import defaultdict
from dataclasses import dataclass, field
from functools import total_ordering
from pathlib import Path
from typing import (
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

import numpy as np
import numpy.typing as npt
from typing_extensions import NotRequired

Extension = Literal["py", "cpp"]
Extensions = Tuple[Pattern, ...]
Flag = Literal[0, 1]
Mode = Literal["many_to_many", "one_to_one"]
ReportsExtension = Literal["json", "csv"]
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


@total_ordering
@dataclass
class ASTFeatures:
    """Class contains the source code metadata."""

    filepath: Union[Path, str]
    modify_date: Optional[str] = None

    count_of_nodes: int = 0
    head_nodes: List[str] = field(default_factory=list)
    operators: Dict[str, int] = field(default_factory=lambda: defaultdict(lambda: 0))
    keywords: Dict[str, int] = field(default_factory=lambda: defaultdict(lambda: 0))
    literals: Dict[str, int] = field(default_factory=lambda: defaultdict(lambda: 0))

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
    weighted_average: np.float64


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


# ----------------------------------------------------------------------------


class Settings(TypedDict):
    environment: NotRequired[Path]
    reports: NotRequired[Path]
    reports_extension: Literal["json", "csv"]
    show_progress: Flag
    threshold: Threshold

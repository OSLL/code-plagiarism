from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import (Dict, List, Literal, NamedTuple, Optional, Pattern, Tuple,
                    TypedDict, Union)

import numpy as np


class NodeCodePlace(NamedTuple):
    lineno: int
    col_offset: int


class NodeStructurePlace(NamedTuple):
    depth: int
    uid: int


@dataclass
class ASTFeatures:
    """Class contains the source code metadata."""

    filepath: Union[Path, str]

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


class FastMetrics(NamedTuple):
    jakkar: float
    operators: float
    keywords: float
    literals: float
    weighted_average: float


class StructuresInfo(NamedTuple):
    similarity: float
    compliance_matrix: np.array


class CompareInfo(NamedTuple):
    fast: FastMetrics
    structure: Optional[StructuresInfo] = None


class WorksReport(TypedDict):
    date: str
    first_path: str
    second_path: str
    first_heads: List[str]
    second_heads: List[str]
    fast: Dict[str, int]
    structure: dict


Extensions = Tuple[Pattern, ...]
Mode = Literal["many_to_many", "one_to_one"]

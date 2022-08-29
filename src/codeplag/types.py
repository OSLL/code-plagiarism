from typing import Dict, List, NamedTuple, TypedDict

import numpy as np


class NodeCodePlace(NamedTuple):
    lineno: int
    col_offset: int


class NodeStructurePlace(NamedTuple):
    depth: int
    uid: int


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
    structure: StructuresInfo = None


class WorksReport(TypedDict):
    date: str
    first_path: str
    second_path: str
    first_heads: List[str]
    second_heads: List[str]
    fast: Dict[str, int]
    structure: dict

from typing import NamedTuple

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

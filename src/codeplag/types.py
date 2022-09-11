from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Literal, NamedTuple, TypedDict

import numpy as np


class NodeCodePlace(NamedTuple):
    lineno: int
    col_offset: int


class NodeStructurePlace(NamedTuple):
    depth: int
    uid: int


class ASTFeatures:
    def __init__(self, filepath: Path):
        self.filepath = filepath

        self.count_of_nodes = 0
        self.head_nodes: List[str] = []
        self.operators: Dict[str, int] = defaultdict(lambda: 0)
        self.keywords: Dict[str, int] = defaultdict(lambda: 0)
        self.literals: Dict[str, int] = defaultdict(lambda: 0)

        # unique nodes
        self.unodes: Dict[str, int] = {}
        self.from_num: Dict[int, str] = {}
        self.count_unodes = 0

        self.structure: List[NodeStructurePlace] = []
        self.tokens: List[int] = []
        self.tokens_pos: List[NodeCodePlace] = []


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


Mode = Literal["many_to_many", "one_to_one"]

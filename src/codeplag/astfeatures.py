from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from codeplag.types import NodeCodePlace, NodeStructurePlace


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

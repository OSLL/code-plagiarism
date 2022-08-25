from collections import defaultdict
from typing import Dict, List, Tuple


class ASTFeatures:
    def __init__(self, filepath: str):
        self.filepath: str = filepath

        self.count_of_nodes = 0
        self.head_nodes: List[str] = []
        self.operators: Dict[str, int] = defaultdict(lambda: 0)
        self.keywords: Dict[str, int] = defaultdict(lambda: 0)
        self.literals: Dict[str, int] = defaultdict(lambda: 0)

        # unique nodes
        self.unodes: Dict[str, int] = {}
        self.from_num: Dict[int, str] = {}
        self.count_unodes: int = 0

        self.structure: List[Tuple[int]] = []
        self.tokens: List[int] = []
        self.tokens_pos: List[Tuple[int]] = []

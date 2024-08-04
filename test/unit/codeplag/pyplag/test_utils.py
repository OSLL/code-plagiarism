import os
from pathlib import Path
from typing import Final

import numpy as np
from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast

CWD: Final[Path] = Path(os.path.dirname(os.path.abspath(__file__)))
FILEPATH1: Final[Path] = CWD / "./data/test1.py"


def test_get_features_from_ast():
    tree = get_ast_from_filename(FILEPATH1)
    assert tree
    features = get_features_from_ast(tree, FILEPATH1)
    unodes = 15

    assert features.count_of_nodes == 42
    assert features.operators == {"AugAssign": 2, "Add": 2, "AnnAssign": 1, "Assign": 1}
    assert features.keywords == {
        "FunctionDef": np.int64(1),
        "Return": np.int64(1),
        "If": np.int64(1),
    }
    assert features.literals == {
        # ast.Constant с python >= 3.8 use for all constants
        # before was NameConstant, Num and etc.
        "Constant": 6
    }
    assert len(features.unodes) == unodes
    assert len(features.from_num) == unodes
    assert features.count_unodes == np.int64(unodes)
    assert len(features.structure) == 42
    assert features.head_nodes == [
        "INT_CONST[1]",
        "INT_CONST[2]",
        "FLOAT_CONST[3]",
        "my_func[6]",
        "If[12]",
    ]
    assert (
        features.sha256
        == "f231b049ada761d534bb611cc7e92efdf8fd985d8092a72a132e79becff338d0"
    )

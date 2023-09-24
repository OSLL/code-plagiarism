import os
from pathlib import Path

import numpy as np
from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.pyplag.utils import get_ast_from_filename
from codeplag.types import ASTFeatures

pwd = Path(os.path.dirname(os.path.abspath(__file__)))


def test_astwalker_class_normal():
    path = pwd / "./data/test1.py"
    tree = get_ast_from_filename(path)
    assert tree is not None
    features = ASTFeatures(path)
    walker = ASTWalker(features)
    walker.visit(tree)
    operators = {"AugAssign": 2, "Add": 2, "AnnAssign": 1, "Assign": 1}
    keywords = {
        "FunctionDef": np.int64(1),
        "Return": np.int64(1),
        "If": np.int64(1),
    }
    literals = {
        # ast.Constant с python >= 3.8 use for all constants
        # before was NameConstant, Num and etc.
        "Constant": 6
    }
    unodes = 15

    assert features.count_of_nodes == 42
    assert features.operators == operators
    assert features.keywords == keywords
    assert features.literals == literals
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

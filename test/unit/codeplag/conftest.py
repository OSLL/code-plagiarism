import ast
import os
from pathlib import Path

import pytest

from codeplag.algorithms.compare import compare_works
from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast
from codeplag.types import ASTFeatures, FullCompareInfo

CWD = Path(os.path.dirname(os.path.abspath(__file__)))
FILEPATH1 = CWD / "./data/test1.py"
FILEPATH2 = CWD / "./data/test2.py"
FILEPATH3 = CWD / "./data/test3.py"


@pytest.fixture
def first_tree() -> ast.Module:
    tree = get_ast_from_filename(FILEPATH1)
    assert tree is not None
    return tree


@pytest.fixture
def second_tree() -> ast.Module:
    tree = get_ast_from_filename(FILEPATH2)
    assert tree is not None
    return tree


@pytest.fixture
def third_tree() -> ast.Module:
    tree = get_ast_from_filename(FILEPATH3)
    assert tree is not None
    return tree


@pytest.fixture
def first_features(first_tree: ast.Module) -> ASTFeatures:
    return get_features_from_ast(first_tree, FILEPATH1)


@pytest.fixture
def second_features(second_tree: ast.Module) -> ASTFeatures:
    return get_features_from_ast(second_tree, FILEPATH2)


@pytest.fixture
def third_features(third_tree: ast.Module) -> ASTFeatures:
    return get_features_from_ast(third_tree, FILEPATH3)


@pytest.fixture
def first_compare_result(
    first_features: ASTFeatures, second_features: ASTFeatures
) -> FullCompareInfo:
    compare_info = compare_works(features1=first_features, features2=second_features)
    assert isinstance(compare_info, FullCompareInfo)
    return compare_info

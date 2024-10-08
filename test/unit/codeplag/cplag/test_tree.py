# fmt: off
from pathlib import Path
from typing import Final

import pytest
from clang.cindex import Cursor, CursorKind

from codeplag.cplag.tree import generic_visit, get_features, get_not_ignored
from codeplag.cplag.utils import get_cursor_from_file
from codeplag.types import ASTFeatures

_DATA_PATH: Final[Path] = Path("test/unit/codeplag/cplag/data").resolve()
_SAMPLE1_PATH: Final[Path] = _DATA_PATH / "sample1.cpp"
_SAMPLE2_PATH: Final[Path] = _DATA_PATH / "sample2.cpp"
_SAMPLE3_PATH: Final[Path] = _DATA_PATH / "sample3.cpp"
_SAMPLE4_PATH: Final[Path] = _DATA_PATH / "sample4.cpp"


@pytest.fixture(scope='module', autouse=True)
def setup() -> None:
    assert _SAMPLE1_PATH.exists() and _SAMPLE2_PATH.exists()
    assert _SAMPLE3_PATH.exists() and _SAMPLE4_PATH.exists()


@pytest.fixture()
def first_cursor() -> Cursor:
    cursor = get_cursor_from_file(_SAMPLE1_PATH)
    assert cursor is not None

    return cursor


@pytest.fixture()
def second_cursor() -> Cursor:
    cursor = get_cursor_from_file(_SAMPLE2_PATH)
    assert cursor is not None

    return cursor


@pytest.fixture()
def third_cursor() -> Cursor:
    cursor = get_cursor_from_file(_SAMPLE3_PATH)
    assert cursor is not None

    return cursor


def test_get_not_ignored_normal(first_cursor: Cursor, second_cursor: Cursor) -> None:
    res1 = get_not_ignored(first_cursor, _SAMPLE1_PATH)
    res2 = get_not_ignored(second_cursor, _SAMPLE2_PATH)

    main_node = res1[0]
    assert main_node.spelling == 'gcd'
    assert main_node.kind == CursorKind.FUNCTION_DECL

    children = main_node.get_children()
    expected_res = [
        ('l', CursorKind.PARM_DECL),
        ('r', CursorKind.PARM_DECL),
        ('', CursorKind.COMPOUND_STMT)
    ]
    for index, child in enumerate(children):
        assert expected_res[index][0] == child.spelling
        assert expected_res[index][1] == child.kind

    main_node = res2[0]
    assert main_node.spelling == 'gcd'
    assert main_node.kind == CursorKind.FUNCTION_DECL

    children = main_node.get_children()
    expected_res = [
        ('a', CursorKind.PARM_DECL),
        ('b', CursorKind.PARM_DECL),
        ('', CursorKind.COMPOUND_STMT)
    ]
    for index, child in enumerate(children):
        assert expected_res[index][0] == child.spelling
        assert expected_res[index][1] == child.kind

    assert isinstance(res1, list)
    assert isinstance(res2, list)
    assert len(res1) == 1
    assert len(res2) == 1


def test_generic_visit(first_cursor: Cursor) -> None:
    features = ASTFeatures(_SAMPLE1_PATH)
    generic_visit(first_cursor, features)

    assert features.filepath == _SAMPLE1_PATH
    assert features.count_of_nodes == 0
    assert features.head_nodes == ['gcd']
    assert features.operators == {}
    assert features.keywords == {}
    assert features.literals == {}
    assert len(features.unodes) == 10
    assert len(features.from_num) == 10
    assert features.count_unodes == 10
    assert len(features.structure) == 23
    assert features.tokens == [8, 10, 10, 202, 205, 114, 100,
                               101, 106, 214, 100, 101, 214,
                               103, 100, 101, 100, 101, 114,
                               100, 101, 100, 101]


def test_get_features(second_cursor: Cursor) -> None:
    features = get_features(second_cursor, _SAMPLE2_PATH)

    assert features.filepath == _SAMPLE2_PATH
    assert features.count_of_nodes == 0
    assert features.head_nodes == ['gcd']
    assert features.operators == {'==': 1, '%': 1}
    assert features.keywords == {'int': 1, 'if': 1, 'return': 2, 'long': 2}
    assert features.literals == {'0L': 1}
    assert len(features.unodes) == 10
    assert len(features.from_num) == 10
    assert features.count_unodes == 10
    assert len(features.structure) == 25
    assert features.tokens == [8, 10, 10, 202, 205, 114, 100,
                               101, 106, 202, 214, 100, 100,
                               101, 214, 103, 100, 101, 100,
                               101, 114, 100, 101, 100, 101]
    assert features.sha256 == "957da24c9f9340954aaa9df303922a0fbdcea69b6d3556c2bd462d195ab89052"


def test_bad_encoding_syms(third_cursor: Cursor) -> None:
    features = get_features(third_cursor, _SAMPLE3_PATH)

    assert features.filepath == _SAMPLE3_PATH
    assert features.count_of_nodes == 0
    assert features.head_nodes == ['main']
    # TODO: why so many '<', '>' may be from include, ignore it
    assert features.operators == {'==': 1, '<': 5, '>': 3, '!=': 1, '&': 3, '*': 1, '=': 4}
    assert features.keywords == {'char': 2, 'for': 2, 'if': 2, 'int': 3, 'return': 2, 'while': 1}
    # Ignored bad symbols
    assert '" .\\n"' in features.literals.keys()  # noqa
    assert len(features.literals.keys()) == 12
    assert len(features.unodes) == 18
    assert len(features.from_num) == 18
    assert features.count_unodes == 18
    assert len(features.structure) == 167
    assert len(features.tokens) == 167
    assert features.sha256 == "40f5feba75390d171f3e719be450989150aa232878ed4d10e0736221bad29b91"

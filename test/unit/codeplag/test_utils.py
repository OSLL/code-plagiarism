import logging
import os
import re
from unittest.mock import call

import pytest

from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast
from codeplag.utils import (CodeplagEngine, compare_works, fast_compare,
                            get_files_path_from_directory)

CWD = os.path.dirname(os.path.abspath(__file__))


def test_fast_compare_normal():
    tree1 = get_ast_from_filename(os.path.join(CWD, './data/test1.py'))
    tree2 = get_ast_from_filename(os.path.join(CWD, './data/test2.py'))
    features1 = get_features_from_ast(tree1)
    features2 = get_features_from_ast(tree2)

    metrics = fast_compare(features1, features2)

    assert metrics.jakkar == pytest.approx(0.737, 0.001)
    assert metrics.operators == pytest.approx(0.667, 0.001)
    assert metrics.keywords == 1.
    assert metrics.literals == 0.75
    assert metrics.weighted_average == pytest.approx(0.774, 0.001)

    metrics2 = fast_compare(
        features1,
        features2,
        weights=(0.5, 0.6, 0.7, 0.8)
    )

    assert metrics2.weighted_average == pytest.approx(0.796, 0.001)


def test_compare_works():
    tree1 = get_ast_from_filename(os.path.join(CWD, './data/test1.py'))
    tree2 = get_ast_from_filename(os.path.join(CWD, './data/test2.py'))
    tree3 = get_ast_from_filename(os.path.join(CWD, './data/test3.py'))
    features1 = get_features_from_ast(tree1)
    features2 = get_features_from_ast(tree2)
    features3 = get_features_from_ast(tree3)

    compare_info = compare_works(features1, features2)

    assert compare_info.fast.jakkar == pytest.approx(0.737, 0.001)
    assert compare_info.fast.operators == pytest.approx(0.667, 0.001)
    assert compare_info.fast.keywords == 1.
    assert compare_info.fast.literals == 0.75
    assert compare_info.fast.weighted_average == pytest.approx(0.774, 0.001)
    assert compare_info.structure.similarity == pytest.approx(0.823, 0.001)
    assert compare_info.structure.compliance_matrix.tolist() == [
        [[19, 24], [7, 21]],
        [[5, 27], [8, 9]]
    ]

    compare_info2 = compare_works(features1, features3)

    assert compare_info2.fast.jakkar == 0.24
    assert compare_info2.fast.operators == 0.0
    assert compare_info2.fast.keywords == 0.6
    assert compare_info2.fast.literals == 0.0
    assert compare_info2.fast.weighted_average == pytest.approx(0.218, 0.001)
    assert compare_info2.structure is None


def test_get_files_path_from_directory():
    files = get_files_path_from_directory(CWD, extensions=(r"\.py$",))

    assert os.path.join(CWD, 'test_utils.py') in files
    assert os.path.join(CWD, 'data/test1.py') in files
    assert os.path.join(CWD, 'data/test2.py') in files


def test_save_result(mocker):
    mocker.patch('logging.Logger')
    code_engine = CodeplagEngine(logging.Logger)
    tree1 = get_ast_from_filename(os.path.join(CWD, './data/test1.py'))
    tree2 = get_ast_from_filename(os.path.join(CWD, './data/test2.py'))
    features1 = get_features_from_ast(tree1)
    features2 = get_features_from_ast(tree2)
    compare_info = compare_works(features1, features2)

    mocker.patch('builtins.open', side_effect=FileNotFoundError)
    code_engine.save_result(
        features1,
        features2,
        compare_info,
        '/bad_dir'
    )
    open.assert_called_once()
    assert logging.Logger.warning.call_args == call(
        'Provided folder for reports now is not exists.'
    )

    mocker.patch('builtins.open', side_effect=PermissionError)
    code_engine.save_result(
        features1,
        features2,
        compare_info,
        '/etc'
    )
    open.assert_called_once()
    assert logging.Logger.warning.call_args == call(
        'Not enough rights to write reports to the folder.'
    )

    mocker.patch('builtins.open')
    code_engine.save_result(
        features1,
        features2,
        compare_info,
        './src'
    )

    open.assert_called_once()
    assert re.search('./src/.*[.]json$', open.call_args[0][0])
    assert re.search('w', open.call_args[0][1])

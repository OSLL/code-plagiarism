import logging
import os
import re
from pathlib import Path
from unittest.mock import call

import pytest

from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast
from codeplag.utils import (CodeplagEngine, calc_iterations, calc_progress,
                            compare_works, fast_compare)

CWD = Path(os.path.dirname(os.path.abspath(__file__)))
FILEPATH1 = CWD / './data/test1.py'
FILEPATH2 = CWD / './data/test2.py'
FILEPATH3 = CWD / './data/test3.py'


def test_fast_compare_normal():
    tree1 = get_ast_from_filename(FILEPATH1)
    tree2 = get_ast_from_filename(FILEPATH2)
    features1 = get_features_from_ast(tree1, FILEPATH1)
    features2 = get_features_from_ast(tree2, FILEPATH2)

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
    tree1 = get_ast_from_filename(FILEPATH1)
    tree2 = get_ast_from_filename(FILEPATH2)
    tree3 = get_ast_from_filename(FILEPATH3)
    features1 = get_features_from_ast(tree1, FILEPATH1)
    features2 = get_features_from_ast(tree2, FILEPATH2)
    features3 = get_features_from_ast(tree3, FILEPATH3)

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


def test_save_result(mocker):
    mocker.patch('logging.Logger')
    code_engine = CodeplagEngine(
        logging.Logger,
        ['--extension', 'py']
    )
    tree1 = get_ast_from_filename(FILEPATH1)
    tree2 = get_ast_from_filename(FILEPATH2)
    features1 = get_features_from_ast(tree1, FILEPATH1)
    features2 = get_features_from_ast(tree2, FILEPATH2)
    compare_info = compare_works(features1, features2)

    mocker.patch('builtins.open', side_effect=FileNotFoundError)
    code_engine.reports_directory = Path('/bad_dir')
    code_engine.save_result(
        features1,
        features2,
        compare_info
    )
    assert logging.Logger.warning.call_args == call(
        'Provided folder for reports now is not exists.'
    )

    mocker.patch('builtins.open', side_effect=PermissionError)
    code_engine.reports_directory = Path('/etc')
    code_engine.save_result(
        features1,
        features2,
        compare_info
    )
    open.assert_called_once()
    assert logging.Logger.warning.call_args == call(
        'Not enough rights to write reports to the folder.'
    )

    mocker.patch('builtins.open')
    code_engine.reports_directory = Path('./src')
    code_engine.save_result(
        features1,
        features2,
        compare_info
    )

    open.assert_called_once()
    assert re.search('src/.*[.]json$', open.call_args[0][0].__str__())
    assert re.search('w', open.call_args[0][1].__str__())


def test_calc_progress():
    assert calc_progress(4, 10) == 0.4
    assert calc_progress(10, 0) == 0.0
    assert calc_progress(5, 10, 15, 0) == 0.5
    assert calc_progress(5, 6, 1, 4) == 0.875


def test_calc_iterations():
    assert calc_iterations(10) == 45
    assert calc_iterations(3, 'one_to_one') == 3
    assert calc_iterations(10, '') == 0

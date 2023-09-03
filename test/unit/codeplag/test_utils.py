import logging
import os
from pathlib import Path
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast
from codeplag.types import WorksReport
from codeplag.utils import (
    CodeplagEngine,
    calc_iterations,
    calc_progress,
    compare_works,
    fast_compare,
)

CWD = Path(os.path.dirname(os.path.abspath(__file__)))
FILEPATH1 = CWD / "./data/test1.py"
FILEPATH2 = CWD / "./data/test2.py"
FILEPATH3 = CWD / "./data/test3.py"


def test_fast_compare_normal():
    tree1 = get_ast_from_filename(FILEPATH1)
    tree2 = get_ast_from_filename(FILEPATH2)
    assert tree1 is not None
    assert tree2 is not None

    features1 = get_features_from_ast(tree1, FILEPATH1)
    features2 = get_features_from_ast(tree2, FILEPATH2)

    metrics = fast_compare(features1, features2)

    assert metrics.jakkar == pytest.approx(0.737, 0.001)
    assert metrics.operators == pytest.approx(0.667, 0.001)
    assert metrics.keywords == 1.0
    assert metrics.literals == 0.75
    assert metrics.weighted_average == pytest.approx(0.774, 0.001)

    metrics2 = fast_compare(features1, features2, weights=(0.5, 0.6, 0.7, 0.8))

    assert metrics2.weighted_average == pytest.approx(0.796, 0.001)


def test_compare_works():
    tree1 = get_ast_from_filename(FILEPATH1)
    tree2 = get_ast_from_filename(FILEPATH2)
    tree3 = get_ast_from_filename(FILEPATH3)
    assert tree1 is not None
    assert tree2 is not None
    assert tree3 is not None

    features1 = get_features_from_ast(tree1, FILEPATH1)
    features2 = get_features_from_ast(tree2, FILEPATH2)
    features3 = get_features_from_ast(tree3, FILEPATH3)

    compare_info = compare_works(features1, features2)

    assert compare_info.fast.jakkar == pytest.approx(0.737, 0.001)
    assert compare_info.fast.operators == pytest.approx(0.667, 0.001)
    assert compare_info.fast.keywords == 1.0
    assert compare_info.fast.literals == 0.75
    assert compare_info.fast.weighted_average == pytest.approx(0.774, 0.001)
    assert compare_info.structure is not None
    assert compare_info.structure.similarity == pytest.approx(0.823, 0.001)
    assert compare_info.structure.compliance_matrix.tolist() == [
        [[19, 24], [7, 21]],
        [[5, 27], [8, 9]],
    ]

    compare_info2 = compare_works(features1, features3)

    assert compare_info2.fast.jakkar == 0.24
    assert compare_info2.fast.operators == 0.0
    assert compare_info2.fast.keywords == 0.6
    assert compare_info2.fast.literals == 0.0
    assert compare_info2.fast.weighted_average == pytest.approx(0.218, 0.001)
    assert compare_info2.structure is None


@pytest.fixture
def mock_default_logger(mocker: MockerFixture):
    mocked_logger = mocker.Mock()
    mocker.patch.object(logging, "getLogger", return_value=mocked_logger)

    return mocked_logger


def test_save_result_json(mocker, mock_default_logger):
    parsed_args = {"extension": "py", "root": "check"}
    code_engine = CodeplagEngine(mock_default_logger, parsed_args)
    tree1 = get_ast_from_filename(FILEPATH1)
    tree2 = get_ast_from_filename(FILEPATH2)
    assert tree1 is not None
    assert tree2 is not None

    features1 = get_features_from_ast(tree1, FILEPATH1)
    features2 = get_features_from_ast(tree2, FILEPATH2)
    compare_info = compare_works(features1, features2)
    assert compare_info.structure is not None

    mocker.patch.object(Path, "open", side_effect=FileNotFoundError)
    code_engine.reports = Path("/bad_dir")
    code_engine.save_result(
        features1, features2, compare_info.fast, compare_info.structure, 'json'
    )
    assert not Path.open.called
    assert mock_default_logger.error.call_args == call(
        "The folder for reports isn't provided or now isn't exists."
    )

    mocker.patch.object(Path, "open", side_effect=PermissionError)
    code_engine.reports = Path("/etc")
    code_engine.save_result(
        features1, features2, compare_info.fast, compare_info.structure, 'json'
    )
    Path.open.assert_called_once()
    assert mock_default_logger.error.call_args == call(
        "Not enough rights to write reports to the folder."
    )

    # First ok test
    mock_write_config = mocker.patch("codeplag.utils.write_config")
    code_engine.reports = Path("./src")
    code_engine.save_result(
        features1, features2, compare_info.fast, compare_info.structure, 'json'
    )
    mock_write_config.assert_called_once()
    assert set(mock_write_config.call_args[0][1].keys()) == set(
        WorksReport.__annotations__.keys() - ["first_modify_date", "second_modify_date"]
    )

    # Second ok test
    mock_write_config.reset_mock()
    features1.modify_date = "2023-07-14T11:22:30Z"
    features2.modify_date = "2023-07-09T14:35:07Z"
    code_engine.save_result(
        features1, features2, compare_info.fast, compare_info.structure, 'json'
    )
    mock_write_config.assert_called_once()
    assert (
        mock_write_config.call_args[0][1].keys() == WorksReport.__annotations__.keys()
    )


@pytest.mark.parametrize(
    "args, result",
    [([4, 10], 0.4), ([10, 0], 0.0), ([5, 10, 15, 0], 0.5), ([5, 6, 1, 4], 0.875)],
)
def test_calc_progress(args, result):
    assert calc_progress(*args) == result


@pytest.mark.parametrize(
    "count, mode, expected",
    [
        (10, "many_to_many", 45),
        (3, "one_to_one", 3),
        (10, "bad_mode", 0),
        (-100, "many_to_many", 0),
        (0, "one_to_one", 0),
        (-10, "bad_mode", 0),
    ],
)
def test_calc_iterations(count, mode, expected):
    assert calc_iterations(count, mode) == expected

import ast
import logging
import os
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, call

import pandas as pd
import pytest
from codeplag.consts import CSV_REPORT_COLUMNS, CSV_REPORT_FILENAME
from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast
from codeplag.types import Mode, Settings, WorksReport
from codeplag.utils import (
    CodeplagEngine,
    calc_iterations,
    calc_progress,
    compare_works,
    deserialize_compare_result,
    fast_compare,
)
from pytest_mock import MockerFixture

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
def mock_default_logger(mocker: MockerFixture) -> MagicMock:
    mocked_logger = mocker.Mock()
    mocker.patch.object(logging, "getLogger", return_value=mocked_logger)

    return mocked_logger


def test_fast_compare_normal(first_tree: ast.Module, second_tree: ast.Module):
    features1 = get_features_from_ast(first_tree, FILEPATH1)
    features2 = get_features_from_ast(second_tree, FILEPATH2)
    metrics = fast_compare(features1, features2)

    assert metrics.jakkar == pytest.approx(0.737, 0.001)
    assert metrics.operators == pytest.approx(0.667, 0.001)
    assert metrics.keywords == 1.0
    assert metrics.literals == 0.75
    assert metrics.weighted_average == pytest.approx(0.774, 0.001)

    metrics2 = fast_compare(features1, features2, weights=(0.5, 0.6, 0.7, 0.8))

    assert metrics2.weighted_average == pytest.approx(0.796, 0.001)


def test_compare_works(
    first_tree: ast.Module,
    second_tree: ast.Module,
    third_tree: ast.Module
):
    features1 = get_features_from_ast(first_tree, FILEPATH1)
    features2 = get_features_from_ast(second_tree, FILEPATH2)
    features3 = get_features_from_ast(third_tree, FILEPATH3)

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


def test_save_result_to_json(
    mocker: MockerFixture,
    mock_default_logger: MagicMock,
    first_tree: ast.Module,
    second_tree: ast.Module
):
    parsed_args = {"extension": "py", "root": "check"}
    code_engine = CodeplagEngine(mock_default_logger, parsed_args)

    features1 = get_features_from_ast(first_tree, FILEPATH1)
    features2 = get_features_from_ast(second_tree, FILEPATH2)
    compare_info = compare_works(features1, features2)
    assert compare_info.structure is not None

    mocker.patch.object(Path, "open", side_effect=FileNotFoundError)
    code_engine.reports = Path("/bad_dir")
    code_engine.save_result(
        features1, features2, compare_info, 'json'
    )
    assert not Path.open.called
    assert mock_default_logger.error.call_args == call(
        "The folder for reports isn't provided or now isn't exists."
    )

    mocker.patch.object(Path, "open", side_effect=PermissionError)
    code_engine.reports = Path("/etc")
    code_engine.save_result(
        features1, features2, compare_info, 'json'
    )
    Path.open.assert_called_once()
    assert mock_default_logger.error.call_args == call(
        "Not enough rights to write reports to the folder."
    )

    # First ok test
    mock_write_config = mocker.patch("codeplag.utils.write_config")
    code_engine.reports = Path("./src")
    code_engine.save_result(
        features1, features2, compare_info, 'json'
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
        features1, features2, compare_info, 'json'
    )
    mock_write_config.assert_called_once()
    assert (
        mock_write_config.call_args[0][1].keys() == WorksReport.__annotations__.keys()
    )


def test_save_result_to_csv(
    mocker: MockerFixture,
    mock_default_logger: MagicMock,
    first_tree: ast.Module,
    second_tree: ast.Module
):
    parsed_args = {"extension": "py", "root": "check"}
    mock_read_config = mocker.patch("codeplag.utils.read_settings_conf")
    mock_read_config.return_value = Settings(
        reports=Path("./src"),
        reports_extension='csv',
        show_progress=0,
        threshold=65
    )
    code_engine = CodeplagEngine(mock_default_logger, parsed_args)

    features1 = get_features_from_ast(first_tree, FILEPATH1)
    features2 = get_features_from_ast(second_tree, FILEPATH2)
    features1.modify_date = "2023-07-14T11:22:30Z"
    features2.modify_date = "2023-07-09T14:35:07Z"
    compare_info = compare_works(features1, features2)
    assert compare_info.structure is not None

    # First ok test
    code_engine.reports = Path("./src")
    code_engine.save_result(
        features1, features2, compare_info, 'csv'
    )
    code_engine._write_df_to_fs()
    df = pd.read_csv(code_engine.reports / CSV_REPORT_FILENAME, sep=';', index_col=0)
    assert df.shape[0] == 1
    assert tuple(df.columns) == CSV_REPORT_COLUMNS

    # Second ok test
    code_engine.save_result(
        features1, features2, compare_info, 'csv'
    )
    code_engine._write_df_to_fs()
    df = pd.read_csv(code_engine.reports / CSV_REPORT_FILENAME, sep=';', index_col=0)
    assert df.shape[0] == 2
    assert tuple(df.columns) == CSV_REPORT_COLUMNS

    # Check deserialization
    for i in range(df.shape[0]):
        assert df.iloc[i].first_path == str(features1.filepath)
        assert df.iloc[i].second_path == str(features2.filepath)
        assert df.iloc[i].first_modify_date == features1.modify_date
        assert df.iloc[i].second_modify_date == features2.modify_date
        deser_compare_info = deserialize_compare_result(df.iloc[i])
        assert deser_compare_info.fast == compare_info.fast
        assert deser_compare_info.structure is not None
        assert deser_compare_info.structure.similarity == compare_info.structure.similarity
        assert (
            deser_compare_info.structure.compliance_matrix.tolist() ==
            compare_info.structure.compliance_matrix.tolist()
        )


@pytest.mark.parametrize(
    "args, result",
    [([4, 10], 0.4), ([10, 0], 0.0), ([5, 10, 15, 0], 0.5), ([5, 6, 1, 4], 0.875)],
)
def test_calc_progress(args: List[int], result: float):
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
def test_calc_iterations(count: int, mode: Mode, expected: int):
    assert calc_iterations(count, mode) == expected

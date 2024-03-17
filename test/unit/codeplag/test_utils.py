import ast
import logging
import os
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, call

import numpy as np
import pandas as pd
import pytest
from codeplag.consts import CSV_REPORT_COLUMNS, CSV_REPORT_FILENAME
from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast
from codeplag.types import (
    ASTFeatures,
    Mode,
    SameHead,
    Settings,
    WorksReport,
)
from codeplag.utils import (
    CodeplagEngine,
    calc_iterations,
    compare_works,
    convert_similarity_matrix_to_percent_matrix,
    deserialize_compare_result,
    deserialize_head_nodes,
    fast_compare,
    get_compliance_matrix_df,
    get_parsed_line,
    get_same_funcs,
    replace_minimal_value,
    serialize_compare_result,
)
from pandas.testing import assert_frame_equal
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
def first_features(first_tree: ast.Module) -> ASTFeatures:
    return get_features_from_ast(first_tree, FILEPATH1)


@pytest.fixture
def second_features(second_tree: ast.Module) -> ASTFeatures:
    return get_features_from_ast(second_tree, FILEPATH1)


@pytest.fixture
def mock_default_logger(mocker: MockerFixture) -> MagicMock:
    mocked_logger = mocker.Mock()
    mocker.patch.object(logging, "getLogger", return_value=mocked_logger)

    return mocked_logger


def test_get_compliance_matrix_df():
    compliance_matrix = np.array([[[1, 2], [1, 10], [3, 4]], [[1, 8], [1, 4], [3, 5]]])
    heads1 = ["get_value", "set_value"]
    heads2 = ["getter", "setter", "returner"]

    assert_frame_equal(
        get_compliance_matrix_df(compliance_matrix, heads1, heads2),
        pd.DataFrame(
            data=[[0.5, 0.1, 0.75], [0.125, 0.25, 0.6]], index=heads1, columns=heads2
        ),
    )


def test_convert_similarity_matrix_to_percent_matrix():
    assert convert_similarity_matrix_to_percent_matrix(
        np.array([[[1, 2], [1, 3], [3, 4]], [[1, 8], [1, 4], [3, 5]]])
    ).tolist() == [[50.0, 33.33, 75.0], [12.5, 25.0, 60.0]]


def test_fast_compare_normal(first_features: ASTFeatures, second_features: ASTFeatures):
    metrics = fast_compare(first_features, second_features)

    assert metrics.jakkar == pytest.approx(0.737, 0.001)
    assert metrics.operators == pytest.approx(0.667, 0.001)
    assert metrics.keywords == 1.0
    assert metrics.literals == 0.75
    assert metrics.weighted_average == pytest.approx(0.774, 0.001)

    metrics2 = fast_compare(
        first_features, second_features, weights=(0.5, 0.6, 0.7, 0.8)
    )

    assert metrics2.weighted_average == pytest.approx(0.796, 0.001)


def test_compare_works(
    first_features: ASTFeatures, second_features: ASTFeatures, third_tree: ast.Module
):
    features3 = get_features_from_ast(third_tree, FILEPATH3)

    compare_info = compare_works(first_features, second_features)

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

    compare_info2 = compare_works(first_features, features3)

    assert compare_info2.fast.jakkar == 0.24
    assert compare_info2.fast.operators == 0.0
    assert compare_info2.fast.keywords == 0.6
    assert compare_info2.fast.literals == 0.0
    assert compare_info2.fast.weighted_average == pytest.approx(0.218, 0.001)
    assert compare_info2.structure is None


@pytest.mark.parametrize(
    "same_parts,new_key,new_value,expected",
    [
        ({"foo": 10.1, "bar": 20.5}, "foorbar", 30.5, {"bar": 20.5, "foorbar": 30.5}),
        ({"foo": 30.1, "bar": 20.5}, "foobar", 5.5, {"foo": 30.1, "bar": 20.5}),
    ],
    ids=[
        "'foo' replaced with 'foobar'",
        "new value is smaller than provided and not inserted",
    ],
)
def test_replace_minimal_value(
    same_parts: Dict[str, float],
    new_key: str,
    new_value: float,
    expected: Dict[str, float],
):
    replace_minimal_value(same_parts, new_key, new_value)

    assert same_parts == expected


def test_get_same_funcs():
    first_heads = ["foo", "bar", "foobar", "barfoo"]
    second_heads = ["func_name", "sum", "mult", "div", "sub"]
    threshold = 70
    n = 2
    percent_matrix = np.array(
        [
            [10.0, 20.0, 30.0, 40.0, 50.0],
            [72.0, 74.0, 3.0, 80.0, 5.0],
            [70.0, 75.0, 80.0, 85.0, 90.0],
            [40.0, 30.0, 20.0, 10.0, 10.0],
        ]
    )
    expected = {
        "foo": [SameHead("sub", 50.0)],
        "bar": [SameHead("div", 80.0), SameHead("sum", 74.0)],
        "foobar": [SameHead("sub", 90.0), SameHead("div", 85.0)],
        "barfoo": [SameHead("func_name", 40.0)],
    }

    result = get_same_funcs(first_heads, second_heads, percent_matrix, threshold, n)
    assert expected == result


def test_get_parsed_line(first_features: ASTFeatures, second_features: ASTFeatures):
    compare_info = compare_works(first_features, second_features)
    assert compare_info.structure
    compare_df = serialize_compare_result(first_features, second_features, compare_info)
    compare_df.iloc[0].first_heads = str(compare_df.iloc[0].first_heads)
    compare_df.iloc[0].second_heads = str(compare_df.iloc[0].second_heads)

    result = list(get_parsed_line(compare_df))

    assert result[0][1].fast == compare_info.fast
    assert result[0][1].structure
    assert result[0][1].structure.similarity == compare_info.structure.similarity
    assert result[0][1].structure.similarity == compare_info.structure.similarity
    assert np.array_equal(
        result[0][1].structure.compliance_matrix,
        compare_info.structure.compliance_matrix,
    )
    assert result[0][2] == {
        "my_func[1]": [SameHead(name="my_func[1]", percent=79.17)],
        "If[7]": [
            SameHead(name="If[7]", percent=88.89),
            SameHead(name="my_func[1]", percent=18.52),
        ],
    }
    assert result[0][3] == {
        "my_func[1]": [SameHead(name="my_func[1]", percent=79.17)],
        "If[7]": [
            SameHead(name="If[7]", percent=88.89),
            SameHead(name="my_func[1]", percent=33.33),
        ],
    }


# TODO: simplify it
def test_save_result_to_json(
    mocker: MockerFixture,
    mock_default_logger: MagicMock,
    first_features: ASTFeatures,
    second_features: ASTFeatures,
):
    parsed_args = {"extension": "py", "root": "check"}
    code_engine = CodeplagEngine(mock_default_logger, parsed_args)

    compare_info = compare_works(first_features, second_features)
    assert compare_info.structure is not None

    mocker.patch.object(Path, "open", side_effect=FileNotFoundError)
    code_engine.reports = Path("/bad_dir")
    code_engine.save_result(first_features, second_features, compare_info, "json")
    assert not Path.open.called
    assert mock_default_logger.error.call_args == call(
        "The folder for reports isn't provided or now isn't exists."
    )

    mocker.patch.object(Path, "open", side_effect=PermissionError)
    code_engine.reports = Path("/etc")
    code_engine.save_result(first_features, second_features, compare_info, "json")
    Path.open.assert_called_once()
    assert mock_default_logger.error.call_args == call(
        "Not enough rights to write reports to the folder."
    )

    # First ok test
    mock_write_config = mocker.patch("codeplag.utils.write_config")
    code_engine.reports = Path("./src")
    code_engine.save_result(first_features, second_features, compare_info, "json")
    mock_write_config.assert_called_once()
    assert set(mock_write_config.call_args[0][1].keys()) == set(
        WorksReport.__annotations__.keys() - ["first_modify_date", "second_modify_date"]
    )

    # Second ok test
    mock_write_config.reset_mock()
    first_features.modify_date = "2023-07-14T11:22:30Z"
    second_features.modify_date = "2023-07-09T14:35:07Z"
    code_engine.save_result(first_features, second_features, compare_info, "json")
    mock_write_config.assert_called_once()
    assert (
        mock_write_config.call_args[0][1].keys() == WorksReport.__annotations__.keys()
    )


# TODO: simplify it
def test_save_result_to_csv(
    mocker: MockerFixture,
    mock_default_logger: MagicMock,
    first_features: ASTFeatures,
    second_features: ASTFeatures,
):
    parsed_args = {"extension": "py", "root": "check"}
    mock_read_config = mocker.patch("codeplag.utils.read_settings_conf")
    mock_read_config.return_value = Settings(
        reports=Path("./src"),
        reports_extension="csv",
        show_progress=0,
        threshold=65,
        language="en",
    )
    code_engine = CodeplagEngine(mock_default_logger, parsed_args)

    first_features.modify_date = "2023-07-14T11:22:30Z"
    second_features.modify_date = "2023-07-09T14:35:07Z"
    compare_info = compare_works(first_features, second_features)
    assert compare_info.structure is not None

    # First ok test
    code_engine.reports = Path("./src")
    code_engine.save_result(first_features, second_features, compare_info, "csv")
    code_engine._write_df_to_fs()
    assert "Saving" in mock_default_logger.debug.mock_calls[-1].args[0]
    report_path = code_engine.reports / CSV_REPORT_FILENAME
    df = pd.read_csv(report_path, sep=";", index_col=0)
    assert df.shape[0] == 1
    assert tuple(df.columns) == CSV_REPORT_COLUMNS

    # Second ok test
    code_engine.save_result(first_features, second_features, compare_info, "csv")
    code_engine._write_df_to_fs()
    assert "Saving" in mock_default_logger.debug.mock_calls[-1].args[0]
    code_engine._write_df_to_fs()
    assert "Nothing" in mock_default_logger.debug.mock_calls[-1].args[0]
    df = pd.read_csv(report_path, sep=";", index_col=0)
    report_path.unlink()
    assert df.shape[0] == 2
    assert tuple(df.columns) == CSV_REPORT_COLUMNS

    # Check deserialization
    for i in range(df.shape[0]):
        assert df.iloc[i].first_path == str(first_features.filepath)
        assert df.iloc[i].second_path == str(second_features.filepath)
        assert df.iloc[i].first_modify_date == first_features.modify_date
        assert df.iloc[i].second_modify_date == second_features.modify_date
        deser_compare_info = deserialize_compare_result(df.iloc[i])
        assert deser_compare_info.fast == compare_info.fast
        assert deser_compare_info.structure is not None
        assert (
            deser_compare_info.structure.similarity == compare_info.structure.similarity
        )
        assert (
            deser_compare_info.structure.compliance_matrix.tolist()
            == compare_info.structure.compliance_matrix.tolist()
        )


@pytest.mark.parametrize(
    "count, mode, expected",
    [
        (10, "many_to_many", 45),
        (3, "one_to_one", 3),
        (-100, "many_to_many", 0),
        (0, "one_to_one", 0),
        (-10, "bad_mode", 0),
    ],
)
def test_calc_iterations(count: int, mode: Mode, expected: int):
    assert calc_iterations(count, mode) == expected


def test_calc_iterations_bad():
    with pytest.raises(ValueError):
        calc_iterations(100, "bad_mode")  # type: ignore


@pytest.mark.parametrize(
    "str_head_nodes,list_head_nodes",
    [
        (
            "['_GH_URL[23]', 'AsyncGithubParser[26]']",
            ["_GH_URL[23]", "AsyncGithubParser[26]"],
        ),
        (
            "['Expr[1]', 'Expr[14]', 'application[16]']",
            ["Expr[1]", "Expr[14]", "application[16]"],
        ),
    ],
)
def test_deserialize_head_nodes(str_head_nodes: str, list_head_nodes: List[str]):
    assert deserialize_head_nodes(str_head_nodes) == list_head_nodes

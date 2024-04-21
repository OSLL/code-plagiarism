import logging
from pathlib import Path
from unittest.mock import MagicMock, call

import numpy as np
import pandas as pd
import pytest
from codeplag.consts import CSV_REPORT_COLUMNS, CSV_REPORT_FILENAME
from codeplag.handlers.report import deserialize_compare_result
from codeplag.types import (
    ASTFeatures,
    Mode,
    Settings,
    WorksReport,
)
from codeplag.utils import (
    CodeplagEngine,
    calc_iterations,
    compare_works,
    fast_compare,
    get_compliance_matrix_df,
)
from pandas.testing import assert_frame_equal
from pytest_mock import MockerFixture


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
    first_features: ASTFeatures,
    second_features: ASTFeatures,
    third_features: ASTFeatures,
):
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

    compare_info2 = compare_works(first_features, third_features, 60)

    assert compare_info2.fast.jakkar == 0.24
    assert compare_info2.fast.operators == 0.0
    assert compare_info2.fast.keywords == 0.6
    assert compare_info2.fast.literals == 0.0
    assert compare_info2.fast.weighted_average == pytest.approx(0.218, 0.001)
    assert compare_info2.structure is None


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
        workers=1,
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

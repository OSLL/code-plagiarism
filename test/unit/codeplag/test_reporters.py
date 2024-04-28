from pathlib import Path
from unittest.mock import MagicMock, call

import pandas as pd
import pytest
from codeplag.consts import CSV_REPORT_COLUMNS, CSV_REPORT_FILENAME
from codeplag.handlers.report import deserialize_compare_result
from codeplag.reporters import CSVReporter, JSONReporter
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    WorksReport,
)
from pytest_mock import MockerFixture


@pytest.fixture
def mock_default_logger(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.reporters.logger")


@pytest.fixture
def mock_write_config(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.reporters.write_config")


class TestJSONReporter:
    REPORTER = JSONReporter(Path("."))

    def test_save_result_not_occurred_due_absent_dir(
        self,
        mock_default_logger: MagicMock,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: CompareInfo,
    ):
        self.REPORTER.reports = Path("/bad_directory")
        self.REPORTER.save_result(first_features, second_features, first_compare_result)
        assert mock_default_logger.error.call_args == call(
            "The folder for reports isn't exists."
        )

    def test_save_result_not_occurred_due_permission_error(
        self,
        mocker: MockerFixture,
        mock_default_logger: MagicMock,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: CompareInfo,
    ):
        mocker.patch.object(Path, "open", side_effect=PermissionError)
        self.REPORTER.reports = Path("/etc")
        self.REPORTER.save_result(first_features, second_features, first_compare_result)
        Path.open.assert_called_once()
        assert mock_default_logger.error.call_args == call(
            "Not enough rights to write reports to the folder."
        )

    def test_save_result_without_modify_date(
        self,
        mock_write_config: MagicMock,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: CompareInfo,
    ):
        mock_write_config.reset_mock()
        self.REPORTER.reports = Path("./src")
        self.REPORTER.save_result(first_features, second_features, first_compare_result)
        mock_write_config.assert_called_once()
        assert set(mock_write_config.call_args[0][1].keys()) == set(
            WorksReport.__annotations__.keys()
            - ["first_modify_date", "second_modify_date"]
        )

    def test_save_result_with_modify_date(
        self,
        mock_write_config: MagicMock,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: CompareInfo,
    ):
        mock_write_config.reset_mock()
        first_features.modify_date = "2023-07-14T11:22:30Z"
        second_features.modify_date = "2023-07-09T14:35:07Z"
        self.REPORTER.save_result(first_features, second_features, first_compare_result)
        mock_write_config.assert_called_once()
        assert (
            mock_write_config.call_args[0][1].keys()
            == WorksReport.__annotations__.keys()
        )


class TestCSVReporter:
    REPORTER = CSVReporter(Path("./src"))

    def test_save_result_n_write_df_to_fs(
        self,
        mock_default_logger: MagicMock,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: CompareInfo,
    ):
        first_features.modify_date = "2023-07-14T11:22:30Z"
        second_features.modify_date = "2023-07-09T14:35:07Z"

        # First ok test
        self.REPORTER.save_result(first_features, second_features, first_compare_result)
        self.REPORTER._write_df_to_fs()
        assert "Saving" in mock_default_logger.debug.mock_calls[-1].args[0]

        # Second ok test
        self.REPORTER.save_result(first_features, second_features, first_compare_result)
        self.REPORTER._write_df_to_fs()
        assert "Saving" in mock_default_logger.debug.mock_calls[-1].args[0]
        self.REPORTER._write_df_to_fs()
        assert "Nothing" in mock_default_logger.debug.mock_calls[-1].args[0]
        report_path = self.REPORTER.reports / CSV_REPORT_FILENAME
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
            assert deser_compare_info.fast == first_compare_result.fast
            assert deser_compare_info.structure is not None
            assert (
                deser_compare_info.structure.similarity
                == first_compare_result.structure.similarity
            )
            assert (
                deser_compare_info.structure.compliance_matrix.tolist()
                == first_compare_result.structure.compliance_matrix.tolist()
            )

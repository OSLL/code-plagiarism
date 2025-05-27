from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typing_extensions import Self

from codeplag.consts import CSV_REPORT_COLUMNS
from codeplag.reporters import (
    CSVReporter,
    deserialize_compare_result,
    deserialize_compare_result_from_dict,
    read_df,
    serialize_compare_result_to_dict,
)
from codeplag.types import (
    ASTFeatures,
    FullCompareInfo,
)


@pytest.fixture
def mock_default_logger(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.reporters.logger")


@pytest.fixture
def mock_write_config(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.reporters.write_config")


class TestCSVReporter:
    REPORTER = CSVReporter(Path("./src"))

    def test_save_result_n_write_df_to_fs(
        self: Self,
        mock_default_logger: MagicMock,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: FullCompareInfo,
    ) -> None:
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
        df = read_df(self.REPORTER.reports_path)
        self.REPORTER.reports_path.unlink()

        # Check deserialization
        assert df.shape[0] == 1
        assert tuple(df.columns) == CSV_REPORT_COLUMNS
        assert df.iloc[0].first_path == str(first_features.filepath)
        assert df.iloc[0].second_path == str(second_features.filepath)
        assert first_features.modify_date and (
            df.iloc[0].first_modify_date == first_features.modify_date
        )
        assert second_features.modify_date and (
            df.iloc[0].second_modify_date == second_features.modify_date
        )
        deser_compare_info = deserialize_compare_result(df.iloc[0])
        assert deser_compare_info.fast == first_compare_result.fast
        assert deser_compare_info.structure is not None
        assert deser_compare_info.structure.similarity == first_compare_result.structure.similarity
        assert (
            deser_compare_info.structure.compliance_matrix.tolist()
            == first_compare_result.structure.compliance_matrix.tolist()
        )


def test_compare_info_serialize_deserialize(first_compare_result: FullCompareInfo) -> None:
    compare_info_dict = serialize_compare_result_to_dict(first_compare_result)
    deserialize = deserialize_compare_result_from_dict(compare_info_dict)

    assert deserialize.fast == first_compare_result.fast
    assert deserialize.structure is not None
    assert deserialize.structure.similarity == first_compare_result.structure.similarity
    assert (
        deserialize.structure.compliance_matrix.tolist()
        == first_compare_result.structure.compliance_matrix.tolist()
    )

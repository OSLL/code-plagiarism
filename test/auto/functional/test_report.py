from shutil import copy

import pytest
from const import REPORTS_FOLDER
from typing_extensions import Self
from utils import create_report, modify_settings, run_check

from codeplag.consts import (
    CSV_REPORT_FILENAME,
    DEFAULT_GENERAL_REPORT_NAME,
    DEFAULT_SOURCES_REPORT_NAME,
)
from codeplag.types import ReportType, ShortOutput

DEFAULT_REPORT_PATH = REPORTS_FOLDER / CSV_REPORT_FILENAME
CUSTOM_REPORT_PATH = REPORTS_FOLDER / "custom_report.csv"
DEFAULT_GENERAL_REPORT_PATH = REPORTS_FOLDER / DEFAULT_GENERAL_REPORT_NAME
DEFAULT_SOURCES_REPORT_PATH = REPORTS_FOLDER / DEFAULT_SOURCES_REPORT_NAME


@pytest.fixture(scope="module", autouse=True)
def setup(create_reports_folder_module: None):
    modify_settings(
        reports=REPORTS_FOLDER,
        reports_extension="csv",
        short_output=ShortOutput.NO_SHOW,
    ).assert_success()
    run_check(["--directories", "test/unit/codeplag/cplag", "src/"]).assert_found_similarity()
    assert DEFAULT_REPORT_PATH.exists()
    assert len(DEFAULT_REPORT_PATH.read_text().split("\n")) > 1

    yield


@pytest.fixture(scope="function")
def setup_custom_reports():
    copy(DEFAULT_REPORT_PATH, CUSTOM_REPORT_PATH)
    modify_settings(reports=CUSTOM_REPORT_PATH).assert_success()

    yield

    modify_settings(reports=REPORTS_FOLDER).assert_success()
    CUSTOM_REPORT_PATH.unlink()


class TestCreateReport:
    def test_create_general_report(self: Self) -> None:
        create_report(REPORTS_FOLDER, "general").assert_success()
        assert DEFAULT_GENERAL_REPORT_PATH.exists()
        DEFAULT_GENERAL_REPORT_PATH.unlink()

    def test_create_general_report_with_custom_report(
        self: Self, setup_custom_reports: None
    ) -> None:
        create_report(REPORTS_FOLDER, "general").assert_success()
        assert DEFAULT_GENERAL_REPORT_PATH.exists()
        DEFAULT_GENERAL_REPORT_PATH.unlink()

    def test_create_sources_report(self: Self) -> None:
        create_report(REPORTS_FOLDER, "sources").assert_success()
        assert DEFAULT_SOURCES_REPORT_PATH.exists()
        DEFAULT_SOURCES_REPORT_PATH.unlink()

    def test_create_sources_report_with_custom_report(
        self: Self, setup_custom_reports: None
    ) -> None:
        create_report(REPORTS_FOLDER, "sources").assert_success()
        assert DEFAULT_SOURCES_REPORT_PATH.exists()
        DEFAULT_SOURCES_REPORT_PATH.unlink()

    @pytest.mark.parametrize(
        "report_type",
        ["general", "sources"],
    )
    def test_content_same_between_calls(self: Self, report_type: ReportType) -> None:
        first_report_path = REPORTS_FOLDER / "report1.html"
        second_report_path = REPORTS_FOLDER / "report2.html"

        create_report(first_report_path, report_type).assert_success()
        create_report(second_report_path, report_type).assert_success()

        assert first_report_path.read_text() == second_report_path.read_text()

    @pytest.mark.parametrize(
        "report_type",
        ["general", "sources"],
    )
    def test_content_different_between_calls(self: Self, report_type: ReportType) -> None:
        first_report_path = REPORTS_FOLDER / "report1.html"
        second_report_path = REPORTS_FOLDER / "report2.html"

        modify_settings(language="en")
        create_report(first_report_path, report_type).assert_success()
        modify_settings(language="ru")
        create_report(second_report_path, report_type).assert_success()

        assert first_report_path.read_text() != second_report_path.read_text()

    @pytest.mark.parametrize(
        "report_type",
        ["general", "sources"],
    )
    def test_default_report_diff_with_provided_paths(self: Self, report_type: ReportType) -> None:
        first_report_path = REPORTS_FOLDER / "report1.html"
        second_report_path = REPORTS_FOLDER / "report2.html"

        create_report(first_report_path, report_type).assert_success()
        create_report(
            second_report_path,
            report_type,
            first_root_path="/usr/src/codeplag",
            second_root_path="/usr/src/webparsers",
        ).assert_success()
        assert first_report_path.read_text() != second_report_path.read_text()

    @pytest.mark.parametrize(
        "report_type",
        ["general", "sources"],
    )
    def test_provided_only_first_path(self: Self, report_type: ReportType) -> None:
        result = create_report(
            REPORTS_FOLDER / "report.html", report_type, first_root_path="/usr/src"
        )

        result.assert_failed()
        assert result.cmd_res.returncode == 2

    @pytest.mark.parametrize(
        "report_type",
        ["general", "sources"],
    )
    def test_provided_only_second_path(self: Self, report_type: ReportType) -> None:
        result = create_report(
            REPORTS_FOLDER / "report.html", report_type, second_root_path="/usr/src"
        )

        result.assert_failed()
        assert result.cmd_res.returncode == 2

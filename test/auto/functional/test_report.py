from pathlib import Path

import pytest
from const import REPORTS_FOLDER
from typing_extensions import Self
from utils import create_report, modify_settings, run_check

from codeplag.consts import DEFAULT_GENERAL_REPORT_NAME, DEFAULT_SOURCES_REPORT_NAME
from codeplag.types import ReportType


@pytest.fixture(scope="function", autouse=True)
def setup(create_reports_folder: None):
    modify_settings(
        reports=REPORTS_FOLDER, reports_extension="csv", short_output=1
    ).assert_success()
    run_check(["--directories", "test/unit/codeplag/cplag", "src/"]).assert_success()

    yield


class TestCreateReport:
    def test_create_general_report(self: Self) -> None:
        create_report(REPORTS_FOLDER, "general").assert_success()
        assert Path(REPORTS_FOLDER / DEFAULT_GENERAL_REPORT_NAME).exists()

    def test_create_sources_report(self: Self) -> None:
        create_report(REPORTS_FOLDER, "sources").assert_success()
        assert Path(REPORTS_FOLDER / DEFAULT_SOURCES_REPORT_NAME).exists()

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
        create_report(
            REPORTS_FOLDER / "report.html", report_type, first_root_path="/usr/src"
        ).assert_failed()

    @pytest.mark.parametrize(
        "report_type",
        ["general", "sources"],
    )
    def test_provided_only_second_path(self: Self, report_type: ReportType) -> None:
        create_report(
            REPORTS_FOLDER / "report.html", report_type, second_root_path="/usr/src"
        ).assert_failed()

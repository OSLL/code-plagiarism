from shutil import copy

import pytest
from const import REPORTS_FOLDER
from typing_extensions import Self
from utils import create_report, modify_settings, run_check

from codeplag.consts import (
    CONFIG_PATH,
    CSV_REPORT_FILENAME,
    DEFAULT_GENERAL_REPORT_NAME,
    DEFAULT_SOURCES_REPORT_NAME,
)
from codeplag.db.mongo import MongoDBConnection
from codeplag.types import ReportsExtension, ReportType, ShortOutput

DEFAULT_REPORT_PATH = REPORTS_FOLDER / CSV_REPORT_FILENAME
CUSTOM_REPORT_PATH = REPORTS_FOLDER / "custom_report.csv"
DEFAULT_GENERAL_REPORT_PATH = REPORTS_FOLDER / DEFAULT_GENERAL_REPORT_NAME
DEFAULT_SOURCES_REPORT_PATH = REPORTS_FOLDER / DEFAULT_SOURCES_REPORT_NAME


@pytest.fixture(scope="module", autouse=True)
def setup(mongo_connection: MongoDBConnection, create_reports_folder_module: None):
    modify_settings(
        reports=REPORTS_FOLDER,
        reports_extension="mongo",
        short_output=ShortOutput.NO_SHOW,
        mongo_host=mongo_connection.host,
        mongo_port=mongo_connection.port,
        mongo_user=mongo_connection.user,
        mongo_pass=mongo_connection.password,
    ).assert_success()
    run_check(["--directories", "test/unit/codeplag/cplag", "src/"]).assert_found_similarity()
    modify_settings(
        reports=REPORTS_FOLDER,
        reports_extension="csv",
        short_output=ShortOutput.NO_SHOW,
    ).assert_success()
    run_check(["--directories", "test/unit/codeplag/cplag", "src/"]).assert_found_similarity()
    assert DEFAULT_REPORT_PATH.exists()
    assert len(DEFAULT_REPORT_PATH.read_text().split("\n")) > 1

    yield

    CONFIG_PATH.write_text("{}")
    modify_settings(log_level="debug")


@pytest.fixture(scope="function")
def setup_custom_reports():
    copy(DEFAULT_REPORT_PATH, CUSTOM_REPORT_PATH)
    modify_settings(reports=CUSTOM_REPORT_PATH).assert_success()

    yield

    modify_settings(reports=REPORTS_FOLDER).assert_success()
    CUSTOM_REPORT_PATH.unlink()


class TestCreateReport:
    @pytest.mark.parametrize("reports_extension", ["csv", "mongo"])
    def test_create_general_report(self: Self, reports_extension: ReportsExtension) -> None:
        modify_settings(reports_extension=reports_extension)
        create_report(REPORTS_FOLDER, "general").assert_success()
        assert DEFAULT_GENERAL_REPORT_PATH.exists()
        DEFAULT_GENERAL_REPORT_PATH.unlink()

    @pytest.mark.parametrize("reports_extension", ["csv", "mongo"])
    def test_create_general_report_with_custom_report(
        self: Self, setup_custom_reports: None, reports_extension: ReportsExtension
    ) -> None:
        modify_settings(reports_extension=reports_extension)
        create_report(REPORTS_FOLDER, "general").assert_success()
        assert DEFAULT_GENERAL_REPORT_PATH.exists()
        DEFAULT_GENERAL_REPORT_PATH.unlink()

    @pytest.mark.parametrize("reports_extension", ["csv", "mongo"])
    def test_create_sources_report(self: Self, reports_extension: ReportsExtension) -> None:
        modify_settings(reports_extension=reports_extension)
        create_report(REPORTS_FOLDER, "sources").assert_success()
        assert DEFAULT_SOURCES_REPORT_PATH.exists()
        DEFAULT_SOURCES_REPORT_PATH.unlink()

    @pytest.mark.parametrize("reports_extension", ["csv", "mongo"])
    def test_create_sources_report_with_custom_report(
        self: Self, setup_custom_reports: None, reports_extension: ReportsExtension
    ) -> None:
        modify_settings(reports_extension=reports_extension)
        create_report(REPORTS_FOLDER, "sources").assert_success()
        assert DEFAULT_SOURCES_REPORT_PATH.exists()
        DEFAULT_SOURCES_REPORT_PATH.unlink()

    @pytest.mark.parametrize(
        ("report_type", "reports_extension"),
        [
            ("general", "csv"),
            ("sources", "mongo"),
        ],
    )
    def test_content_same_between_calls(
        self: Self, report_type: ReportType, reports_extension: ReportsExtension
    ) -> None:
        first_report_path = REPORTS_FOLDER / "report1.html"
        second_report_path = REPORTS_FOLDER / "report2.html"

        modify_settings(reports_extension=reports_extension)
        create_report(first_report_path, report_type).assert_success()
        create_report(second_report_path, report_type).assert_success()

        assert first_report_path.read_text() == second_report_path.read_text()

    @pytest.mark.parametrize(
        ("report_type", "reports_extension"),
        [
            ("general", "csv"),
            ("sources", "mongo"),
        ],
    )
    def test_content_different_between_calls(
        self: Self, report_type: ReportType, reports_extension: ReportsExtension
    ) -> None:
        first_report_path = REPORTS_FOLDER / "report1.html"
        second_report_path = REPORTS_FOLDER / "report2.html"

        modify_settings(language="en", reports_extension=reports_extension)
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

        modify_settings(reports_extension="csv")
        create_report(first_report_path, report_type).assert_success()
        create_report(
            second_report_path,
            report_type,
            first_root_path="/usr/src/codeplag",
            second_root_path="/usr/src/webparsers",
        ).assert_success()
        assert first_report_path.read_text() != second_report_path.read_text()

    @pytest.mark.parametrize(
        ("report_type", "reports_extension"),
        [
            ("general", "csv"),
            ("sources", "mongo"),
        ],
    )
    def test_provided_only_first_path(
        self: Self, report_type: ReportType, reports_extension: ReportsExtension
    ) -> None:
        modify_settings(reports_extension=reports_extension)
        result = create_report(
            REPORTS_FOLDER / "report.html", report_type, first_root_path="/usr/src"
        )

        result.assert_failed()
        assert result.cmd_res.returncode == 2

    @pytest.mark.parametrize(
        ("report_type", "reports_extension"),
        [
            ("general", "csv"),
            ("sources", "mongo"),
        ],
    )
    def test_provided_only_second_path(
        self: Self, report_type: ReportType, reports_extension: ReportsExtension
    ) -> None:
        modify_settings(reports_extension=reports_extension)
        result = create_report(
            REPORTS_FOLDER / "report.html", report_type, second_root_path="/usr/src"
        )

        result.assert_failed()
        assert result.cmd_res.returncode == 2

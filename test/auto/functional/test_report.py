from pathlib import Path

from codeplag.consts import DEFAULT_GENERAL_REPORT_NAME
from const import REPORTS_FOLDER
from utils import create_report, modify_settings, run_check


def test_create_report(create_reports_folder: None):
    modify_settings(reports=REPORTS_FOLDER, reports_extension="csv").assert_success()
    run_check(["--directories", "test/unit/codeplag/cplag", "src/"]).assert_success()

    # Main checks
    create_report(REPORTS_FOLDER).assert_success()
    REPORT_PATH = Path(REPORTS_FOLDER / DEFAULT_GENERAL_REPORT_NAME)
    assert REPORT_PATH.exists()

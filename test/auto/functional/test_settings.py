import json
import os
from pathlib import Path
from typing import Literal

import pytest
from codeplag.consts import CONFIG_PATH, UTIL_NAME
from codeplag.types import Language, ReportsExtension, Threshold
from utils import modify_settings


@pytest.fixture(scope="module", autouse=True)
def teardown():
    yield

    CONFIG_PATH.write_text("{}")


class TestSettingsModify:
    @pytest.mark.parametrize(
        "env,reports,threshold,show_progress,reports_extension,language,workers",
        [
            (f"src/{UTIL_NAME}/types.py", "src", 83, 0, "json", "en", 1),
            ("setup.py", "test", 67, 1, "csv", "ru", os.cpu_count() or 1),
            (f"src/{UTIL_NAME}/utils.py", "debian", 93, 0, "json", "en", 1),
        ],
    )
    def test_modify_settings(
        self,
        env: str,
        reports: str,
        threshold: Threshold,
        show_progress: Literal[0, 1],
        reports_extension: ReportsExtension,
        language: Language,
        workers: int,
    ):
        result = modify_settings(
            environment=env,
            reports=reports,
            threshold=threshold,
            show_progress=show_progress,
            reports_extension=reports_extension,
            language=language,
            workers=workers,
        )
        result.assert_success()

        assert json.loads(CONFIG_PATH.read_text()) == {
            "environment": Path(env).absolute().__str__(),
            "reports": Path(reports).absolute().__str__(),
            "threshold": threshold,
            "show_progress": show_progress,
            "workers": workers,
            "language": language,
            "reports_extension": reports_extension,
        }

    @pytest.mark.parametrize(
        "env, reports, threshold",
        [
            (".env", "src", 101),
            ("setup.py", "test983hskdfue", 67),
            (f"src/{UTIL_NAME}/utils.pyjlsieuow0", "debian", 93),
        ],
        ids=[
            "Incorrect threshold.",
            "Path to reports doesn't exists.",
            "Path to environment doesn't exists.",
        ],
    )
    def test_modify_settings_with_invalid_arguments(self, env, reports, threshold):
        modify_settings(
            environment=env, reports=reports, threshold=threshold
        ).assert_failed()

    def test_modify_settings_with_no_arguments_failed(self):
        modify_settings().assert_failed()

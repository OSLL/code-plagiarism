import json
import os
from pathlib import Path
from typing import Literal

import pytest
from typing_extensions import Self
from utils import MaxDepth, NgramsLength, modify_settings

from codeplag.consts import CONFIG_PATH, NGRAMS_LENGTH_CHOICE, UTIL_NAME
from codeplag.types import Language, LogLevel, ReportsExtension, Threshold


@pytest.fixture(scope="module", autouse=True)
def teardown():
    yield

    CONFIG_PATH.write_text("{}")
    modify_settings(log_level="debug")


class TestSettingsModify:
    @pytest.mark.parametrize(
        "env,reports,threshold,max_depth,ngrams_length,show_progress,reports_extension,language,log_level,workers",
        [
            (f"src/{UTIL_NAME}/types.py", "src", 83, 6, 2, 0, "csv", "en", "debug", 1),
            ("setup.py", "test", 67, 7, 3, 1, "csv", "ru", "info", os.cpu_count() or 1),
            (f"src/{UTIL_NAME}/utils.py", "debian", 93, 8, 4, 0, "csv", "en", "warning", 1),
        ],
    )
    def test_modify_settings(
        self: Self,
        env: str,
        reports: str,
        threshold: Threshold,
        max_depth: MaxDepth,
        ngrams_length: NgramsLength,
        show_progress: Literal[0, 1],
        reports_extension: ReportsExtension,
        language: Language,
        log_level: LogLevel,
        workers: int,
    ) -> None:
        result = modify_settings(
            environment=env,
            reports=reports,
            threshold=threshold,
            max_depth=max_depth,
            ngrams_length=ngrams_length,
            show_progress=show_progress,
            reports_extension=reports_extension,
            language=language,
            log_level=log_level,
            workers=workers,
        )
        result.assert_success()

        assert json.loads(CONFIG_PATH.read_text()) == {
            "environment": Path(env).resolve().__str__(),
            "reports": Path(reports).resolve().__str__(),
            "threshold": threshold,
            "max_depth": max_depth,
            "ngrams_length": ngrams_length,
            "show_progress": show_progress,
            "workers": workers,
            "language": language,
            "log_level": log_level,
            "reports_extension": reports_extension,
        }

    @pytest.mark.parametrize(
        "env,reports,threshold,log_level",
        [
            (".env", "src", 101, "debug"),
            ("setup.py", "test983hskdfue", 67, "info"),
            (f"src/{UTIL_NAME}/utils.pyjlsieuow0", "debian", 93, "warning"),
            (f"src/{UTIL_NAME}/types.py", "src", 83, "foobar"),
        ],
        ids=[
            "Incorrect threshold.",
            "Path to reports doesn't exists.",
            "Path to environment doesn't exists.",
            "Invalid log level.",
        ],
    )
    def test_modify_settings_with_invalid_arguments(
        self: Self, env: str, reports: str, threshold: Threshold, log_level: LogLevel
    ) -> None:
        modify_settings(
            environment=env, reports=reports, threshold=threshold, log_level=log_level
        ).assert_failed()

    @pytest.mark.parametrize(
        "ngrams_length",
        [NGRAMS_LENGTH_CHOICE[0] - 1, NGRAMS_LENGTH_CHOICE[-1] + 1],
        ids=["Less than minimal value.", "More than minimal value."],
    )
    def test_modify_settings_with_invalid_ngrams_length(
        self: Self, ngrams_length: NgramsLength
    ) -> None:
        modify_settings(ngrams_length=ngrams_length).assert_failed()

    def test_modify_settings_with_no_arguments_failed(self: Self) -> None:
        modify_settings().assert_failed()

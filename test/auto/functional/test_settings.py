import json
import os
from pathlib import Path

import pytest
from typing_extensions import Self
from utils import MaxDepth, NgramsLength, modify_settings

from codeplag.consts import CONFIG_PATH, NGRAMS_LENGTH_CHOICE, UTIL_NAME
from codeplag.types import Flag, Language, LogLevel, ReportsExtension, ShortOutput, Threshold


@pytest.fixture(scope="module", autouse=True)
def teardown():
    yield

    CONFIG_PATH.write_text("{}")
    modify_settings(log_level="debug")


class TestSettingsModify:
    @pytest.mark.parametrize(
        "env,reports,threshold,max_depth,ngrams_length,show_progress,short_output,reports_extension,language,log_level,workers,mongo_host,mongo_port,mongo_user,mongo_pass",
        [
            (
                f"src/{UTIL_NAME}/types.py",
                "src",
                83,
                6,
                2,
                0,
                0,
                "csv",
                "en",
                "debug",
                1,
                "localhost",
                27017,
                "user",
                "password",
            ),
            (
                "setup.py",
                "test",
                67,
                7,
                3,
                1,
                1,
                "csv",
                "ru",
                "info",
                os.cpu_count() or 1,
                "127.0.0.1",
                65355,
                "admin",
                "secret",
            ),
            (
                f"src/{UTIL_NAME}/utils.py",
                "debian",
                93,
                8,
                4,
                0,
                1,
                "mongo",
                "en",
                "warning",
                1,
                "host.docker.internal",
                1,
                "guest",
                "12345",
            ),
        ],
    )
    def test_modify_settings(
        self: Self,
        env: str,
        reports: str,
        threshold: Threshold,
        max_depth: MaxDepth,
        ngrams_length: NgramsLength,
        show_progress: Flag,
        short_output: ShortOutput,
        reports_extension: ReportsExtension,
        language: Language,
        log_level: LogLevel,
        workers: int,
        mongo_host: str,
        mongo_port: int,
        mongo_user: str,
        mongo_pass: str,
    ) -> None:
        result = modify_settings(
            environment=env,
            reports=reports,
            threshold=threshold,
            max_depth=max_depth,
            ngrams_length=ngrams_length,
            show_progress=show_progress,
            short_output=short_output,
            reports_extension=reports_extension,
            language=language,
            log_level=log_level,
            workers=workers,
            mongo_host=mongo_host,
            mongo_port=mongo_port,
            mongo_user=mongo_user,
            mongo_pass=mongo_pass,
        )
        result.assert_success()

        assert json.loads(CONFIG_PATH.read_text()) == {
            "environment": Path(env).resolve().__str__(),
            "reports": Path(reports).resolve().__str__(),
            "threshold": threshold,
            "max_depth": max_depth,
            "ngrams_length": ngrams_length,
            "show_progress": show_progress,
            "short_output": short_output,
            "workers": workers,
            "language": language,
            "log_level": log_level,
            "reports_extension": reports_extension,
            "mongo_host": mongo_host,
            "mongo_port": mongo_port,
            "mongo_user": mongo_user,
            "mongo_pass": mongo_pass,
        }

    @pytest.mark.parametrize(
        "env,reports,threshold,log_level,short_output",
        [
            (".env", "src", 101, "debug", ShortOutput.NO_SHOW),
            (f"src/{UTIL_NAME}/utils.pyjlsieuow0", "debian", 93, "warning", ShortOutput.SHOW_ALL),
            (f"src/{UTIL_NAME}/types.py", "src", 83, "foobar", ShortOutput.SHOW_NEW),
            (f"src/{UTIL_NAME}/types.py", "src", 83, "info", 3),
        ],
        ids=[
            "Incorrect threshold.",
            "Path to environment doesn't exists.",
            "Invalid log level.",
            "Invalid short-output.",
        ],
    )
    def test_modify_settings_with_invalid_arguments(
        self: Self,
        env: str,
        reports: str,
        threshold: Threshold,
        log_level: LogLevel,
        short_output: ShortOutput,
    ) -> None:
        modify_settings(
            environment=env,
            reports=reports,
            threshold=threshold,
            log_level=log_level,
            short_output=short_output,
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

    @pytest.mark.parametrize(
        "mongo_port",
        [0, 65536],
        ids=["Less than minimal value.", "More than minimal value."],
    )
    def test_modify_settings_with_invalid_mongo_port(self: Self, mongo_port: int) -> None:
        modify_settings(mongo_port=mongo_port).assert_failed()

    def test_modify_settings_with_no_arguments_failed(self: Self) -> None:
        modify_settings().assert_failed()

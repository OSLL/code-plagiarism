import json
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from codeplag import config
from codeplag.consts import (
    CONFIG_PATH,
    DEFAULT_LANGUAGE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MONGO_HOST,
    DEFAULT_MONGO_PORT,
    DEFAULT_MONGO_USER,
    DEFAULT_NGRAMS_LENGTH,
    DEFAULT_REPORT_EXTENSION,
    DEFAULT_THRESHOLD,
    UTIL_NAME,
)
from codeplag.types import Settings

config.logger = MagicMock(autospec=logging.Logger(UTIL_NAME))


@pytest.fixture
def mock_json_load(request: pytest.FixtureRequest, mocker: MockerFixture) -> dict:
    mocker.patch.object(json, "load", return_value=request.param)

    return request.param


@pytest.fixture
def mock_json_dump(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(json, "dump")


@pytest.fixture
def path(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(autospec=Path("."))


@pytest.fixture
def settings_config(request: pytest.FixtureRequest, mocker: MockerFixture) -> Settings | None:
    mocker.patch.object(config, "read_config", return_value=request.param)
    return request.param


@pytest.fixture
def mock_write_config(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(config, "write_config")


@pytest.mark.parametrize(
    "mock_json_load",
    [
        {"threshold": 75},
        {"threshold": 97, "reports": "reports", "environment": ".env"},
        {},
    ],
    indirect=True,
)
def test_read_config(path: MagicMock, mock_json_load: dict):
    assert config.read_config(path) == mock_json_load


@pytest.mark.parametrize(
    "except_type",
    [
        json.decoder.JSONDecodeError(
            msg="Json decode error.", doc="This is json decode error.", pos=1
        ),
        FileNotFoundError,
        PermissionError,
    ],
)
def test_read_config_safe(path: MagicMock, except_type: Exception):
    path.open.side_effect = except_type
    assert config.read_config(path, safe=True) is None


@pytest.mark.parametrize("except_type", [FileNotFoundError, PermissionError])
def test_read_config_bad(path: MagicMock, except_type: Exception):
    path.open.side_effect = except_type
    with pytest.raises(except_type):
        config.read_config(path)


@pytest.mark.parametrize(
    "dumped_dict, expected",
    [
        [{}, {}],
        [
            {"field1": 10, "field2": Path("settings.json"), "field3": [1, 2, 3]},
            {"field1": 10, "field2": "settings.json", "field3": [1, 2, 3]},
        ],
    ],
)
def test_write_config(
    path: MagicMock, mock_json_dump: MagicMock, dumped_dict: dict, expected: dict
):
    copy_dumped = dict(dumped_dict)
    config.write_config(path, dumped_dict)
    mock_json_dump.assert_called_once()
    assert mock_json_dump.mock_calls[0].args[0] == expected
    assert copy_dumped == dumped_dict


@pytest.mark.parametrize("settings_config", [None], indirect=True)
def test_read_default_settings_conf(settings_config: Settings | None):
    assert config.read_settings_conf() == config.DefaultSettingsConfig
    config.logger.warning.assert_called_once()
    config.logger.reset_mock()


@pytest.mark.parametrize(
    "settings_config, expected",
    [
        [{}, config.DefaultSettingsConfig],
        [
            {"reports": "/home/bukabyka/reports"},
            {
                "threshold": DEFAULT_THRESHOLD,
                "max_depth": DEFAULT_MAX_DEPTH,
                "ngrams_length": DEFAULT_NGRAMS_LENGTH,
                "reports": Path("/home/bukabyka/reports"),
                "show_progress": 0,
                "short_output": 0,
                "reports_extension": DEFAULT_REPORT_EXTENSION,
                "language": DEFAULT_LANGUAGE,
                "log_level": DEFAULT_LOG_LEVEL,
                "workers": os.cpu_count() or 1,
                "mongo_host": DEFAULT_MONGO_HOST,
                "mongo_port": DEFAULT_MONGO_PORT,
                "mongo_user": DEFAULT_MONGO_USER,
            },
        ],
        [
            {
                "threshold": 99,
                "max_depth": 6,
                "ngrams_length": 5,
                "environment": "/home/bukabyka/.env",
                "show_progress": 1,
                "short_output": 1,
                "reports_extension": "json",
                "language": "ru",
                "log_level": "error",
                "workers": 128,
                "mongo_host": "localhost",
                "mongo_port": 27017,
                "mongo_user": "user",
                "mongo_pass": "password",
            },
            {
                "threshold": 99,
                "max_depth": 6,
                "ngrams_length": 5,
                "environment": Path("/home/bukabyka/.env"),
                "show_progress": 1,
                "short_output": 1,
                "reports_extension": "json",
                "language": "ru",
                "log_level": "error",
                "workers": 128,
                "mongo_host": "localhost",
                "mongo_port": 27017,
                "mongo_user": "user",
                "mongo_pass": "password",
            },
        ],
        [
            {
                "bad_field": "bad_field",
                "reports": "/home/bukabyka/reports",
                "short_output": 2,
            },
            {
                "threshold": DEFAULT_THRESHOLD,
                "max_depth": DEFAULT_MAX_DEPTH,
                "ngrams_length": DEFAULT_NGRAMS_LENGTH,
                "reports": Path("/home/bukabyka/reports"),
                "show_progress": 0,
                "short_output": 2,
                "reports_extension": DEFAULT_REPORT_EXTENSION,
                "language": DEFAULT_LANGUAGE,
                "log_level": DEFAULT_LOG_LEVEL,
                "workers": os.cpu_count() or 1,
                "mongo_host": DEFAULT_MONGO_HOST,
                "mongo_port": DEFAULT_MONGO_PORT,
                "mongo_user": DEFAULT_MONGO_USER,
            },
        ],
    ],
    indirect=["settings_config"],
)
def test_read_settings_conf(settings_config: Settings, expected: Settings):
    assert config.read_settings_conf() == expected
    config.logger.warning.assert_not_called()
    config.logger.reset_mock()


def test_write_settings_conf(mock_write_config: MagicMock):
    config.write_settings_conf(config.DefaultSettingsConfig)
    mock_write_config.assert_called_once_with(CONFIG_PATH, config.DefaultSettingsConfig)

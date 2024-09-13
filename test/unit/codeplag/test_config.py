import json
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from codeplag import config
from codeplag.consts import CONFIG_PATH, UTIL_NAME
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
                "threshold": 65,
                "reports": Path("/home/bukabyka/reports"),
                "show_progress": 0,
                "reports_extension": "csv",
                "language": "en",
                "log_level": "info",
                "workers": os.cpu_count() or 1,
            },
        ],
        [
            {
                "threshold": 99,
                "environment": "/home/bukabyka/.env",
                "show_progress": 1,
                "reports_extension": "json",
                "language": "ru",
                "log_level": "error",
                "workers": 128,
            },
            {
                "threshold": 99,
                "environment": Path("/home/bukabyka/.env"),
                "show_progress": 1,
                "reports_extension": "json",
                "language": "ru",
                "log_level": "error",
                "workers": 128,
            },
        ],
        [
            {"bad_field": "bad_field", "reports": "/home/bukabyka/reports"},
            {
                "threshold": 65,
                "reports": Path("/home/bukabyka/reports"),
                "show_progress": 0,
                "reports_extension": "csv",
                "language": "en",
                "log_level": "info",
                "workers": os.cpu_count() or 1,
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

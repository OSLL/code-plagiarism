import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from codeplag.config import (
    DefaultSettingsConfig,
    read_config,
    read_settings_conf,
    write_config,
    write_settings_conf,
)
from codeplag.consts import CONFIG_PATH
from pytest_mock import MockerFixture


@pytest.fixture
def mock_json_load(request, mocker: MockerFixture) -> dict:
    mocker.patch.object(json, "load", return_value=request.param)

    return request.param


@pytest.fixture
def mock_json_dump(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(json, "dump")


@pytest.fixture
def path(mocker: MockerFixture):
    return mocker.MagicMock(autospec=Path("."))


@pytest.fixture
def settings_config(request, mocker: MockerFixture):
    mocker.patch("codeplag.config.read_config", return_value=request.param)

    return request.param


@pytest.fixture
def mock_write_config(mocker: MockerFixture):
    return mocker.patch("codeplag.config.write_config")


@pytest.mark.parametrize(
    "mock_json_load",
    [
        {"threshold": 75},
        {"threshold": 97, "reports": "reports", "environment": ".env"},
        {},
    ],
    indirect=True,
)
def test_read_config(path, mock_json_load):
    assert read_config(path) == mock_json_load


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
def test_read_config_safe(path, except_type):
    path.open.side_effect = except_type
    assert read_config(path, safe=True) is None


@pytest.mark.parametrize("except_type", [FileNotFoundError, PermissionError])
def test_read_config_bad(path, except_type):
    path.open.side_effect = except_type
    with pytest.raises(except_type):
        read_config(path)


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
def test_write_config(path, mock_json_dump, dumped_dict, expected):
    copy_dumped = dict(dumped_dict)
    write_config(path, dumped_dict)
    mock_json_dump.assert_called_once()
    assert mock_json_dump.mock_calls[0].args[0] == expected
    assert copy_dumped == dumped_dict


@pytest.mark.parametrize("settings_config", [None], indirect=True)
def test_read_default_settings_conf(dummy_logger, settings_config):
    assert read_settings_conf(dummy_logger) == DefaultSettingsConfig
    dummy_logger.warning.assert_called_once()


@pytest.mark.parametrize(
    "settings_config, expected",
    [
        [{}, DefaultSettingsConfig],
        [
            {"reports": "/home/bukabyka/reports"},
            {
                "threshold": 65,
                "reports": Path("/home/bukabyka/reports"),
                "show_progress": 0,
                "reports_extension": "csv",
            },
        ],
        [
            {
                "threshold": 99,
                "environment": "/home/bukabyka/.env",
                "show_progress": 1,
                "reports_extension": "json",
            },
            {
                "threshold": 99,
                "environment": Path("/home/bukabyka/.env"),
                "show_progress": 1,
                "reports_extension": "json",
            },
        ],
        [
            {"bad_field": "bad_field", "reports": "/home/bukabyka/reports"},
            {
                "threshold": 65,
                "reports": Path("/home/bukabyka/reports"),
                "show_progress": 0,
                "reports_extension": "csv",
            },
        ],
    ],
    indirect=["settings_config"],
)
def test_read_settings_conf(dummy_logger, settings_config, expected):
    assert read_settings_conf(dummy_logger) == expected
    dummy_logger.error.assert_not_called()


def test_write_settings_conf(mock_write_config):
    write_settings_conf(DefaultSettingsConfig)
    mock_write_config.assert_called_once_with(CONFIG_PATH, DefaultSettingsConfig)

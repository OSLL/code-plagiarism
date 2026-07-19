from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from codeplag.handlers.settings import settings_modify


@pytest.fixture
def mock_read_settings_conf(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.handlers.settings.read_settings_conf")


@pytest.fixture
def mock_write_settings_conf(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.handlers.settings.write_settings_conf")


@pytest.fixture
def mock_path_resolve(mocker: MockerFixture) -> MagicMock:
    mock_path = mocker.MagicMock(spec=Path)
    mock_path.resolve.return_value = Path("/resolved/path")
    return mock_path


class TestSettingsModify:
    def test_settings_modify_with_none_args(
        self, mock_read_settings_conf: MagicMock, mock_write_settings_conf: MagicMock
    ) -> None:
        mock_read_settings_conf.return_value = {
            "threshold": 75,
            "max_depth": 5,
        }

        settings_modify({})

        mock_read_settings_conf.assert_not_called()
        mock_write_settings_conf.assert_not_called()

    def test_settings_modify_updates_single_field(
        self, mock_read_settings_conf: MagicMock, mock_write_settings_conf: MagicMock
    ) -> None:
        mock_read_settings_conf.return_value = {
            "threshold": 75,
            "max_depth": 5,
        }

        settings_modify({"threshold": 90})

        mock_read_settings_conf.assert_called_once_with()
        mock_write_settings_conf.assert_called_once_with(
            {
                "threshold": 90,
                "max_depth": 5,
            }
        )

    def test_settings_modify_updates_multiple_fields(
        self, mock_read_settings_conf: MagicMock, mock_write_settings_conf: MagicMock
    ) -> None:
        mock_read_settings_conf.return_value = {
            "threshold": 75,
            "max_depth": 5,
            "ngrams_length": 3,
        }

        settings_modify({"threshold": 90, "max_depth": 7, "ngrams_length": 5})

        mock_read_settings_conf.assert_called_once_with()
        mock_write_settings_conf.assert_called_once_with(
            {
                "threshold": 90,
                "max_depth": 7,
                "ngrams_length": 5,
            }
        )

    def test_settings_modify_deletes_field_with_empty_string(
        self, mock_read_settings_conf: MagicMock, mock_write_settings_conf: MagicMock
    ) -> None:
        mock_read_settings_conf.return_value = {
            "threshold": 75,
            "max_depth": 5,
            "reports": Path("reports"),
        }

        settings_modify({"reports": ""})

        mock_read_settings_conf.assert_called_once_with()
        mock_write_settings_conf.assert_called_once_with(
            {
                "threshold": 75,
                "max_depth": 5,
            }
        )

    def test_settings_modify_ignores_unknown_fields(
        self, mock_read_settings_conf: MagicMock, mock_write_settings_conf: MagicMock
    ) -> None:
        mock_read_settings_conf.return_value = {
            "threshold": 75,
            "max_depth": 5,
        }

        settings_modify({"unknown_field": "value"})

        mock_read_settings_conf.assert_called_once_with()
        mock_write_settings_conf.assert_called_once_with(
            {
                "threshold": 75,
                "max_depth": 5,
            }
        )

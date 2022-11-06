import json
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from codeplag.config import read_config


@pytest.fixture
def mock_json_load(request, mocker: MockerFixture) -> dict:
    mocker.patch.object(json, 'load', return_value=request.param)

    return request.param


@pytest.fixture
def path(mocker: MockerFixture):
    return mocker.MagicMock(autospec=Path('.'))


@pytest.mark.parametrize(
    "mock_json_load",
    [
        {'threshold': 75},
        {
            'threshold': 97, 'reports': 'reports', 'environment': '.env'
        },
        {}
    ],
    indirect=True,
)
def test_read_config(path, mock_json_load):
    assert read_config(path) == mock_json_load


@pytest.mark.parametrize(
    "except_type",
    [
        json.decoder.JSONDecodeError(
            msg="Json decode error.",
            doc="This is json decode error.",
            pos=1
        ),
        FileNotFoundError,
        PermissionError
    ]
)
def test_read_config_safe(path, except_type):
    path.open.side_effect = except_type
    assert read_config(path, safe=True) is None


@pytest.mark.parametrize(
    "except_type",
    [
        FileNotFoundError,
        PermissionError
    ]
)
def test_read_config_bad(path, except_type):
    path.open.side_effect = except_type
    with pytest.raises(except_type):
        read_config(path)

import logging

import pytest
from codeplag.consts import UTIL_NAME
from pytest_mock import MockerFixture


@pytest.fixture
def dummy_logger(mocker: MockerFixture):
    return mocker.MagicMock(autospec=logging.Logger(UTIL_NAME))

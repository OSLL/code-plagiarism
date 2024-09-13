import logging

import pytest
from pytest_mock import MockerFixture

from codeplag.consts import UTIL_NAME


@pytest.fixture
def dummy_logger(mocker: MockerFixture):
    return mocker.MagicMock(autospec=logging.Logger(UTIL_NAME))

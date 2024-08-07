import os
import shutil
from contextlib import suppress

import pytest
from const import REPORTS_FOLDER
from utils import modify_settings


@pytest.fixture
def create_reports_folder():
    with suppress(Exception):
        os.mkdir(REPORTS_FOLDER)
    assert os.path.exists(REPORTS_FOLDER)

    yield

    shutil.rmtree(REPORTS_FOLDER)


@pytest.fixture(scope="session", autouse=True)
def set_logging_level():
    modify_settings(log_level="debug")

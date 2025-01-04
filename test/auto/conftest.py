import os
import shutil
from contextlib import suppress

import pytest
from const import REPORTS_FOLDER
from utils import modify_settings


@pytest.fixture
def create_reports_folder():
    __create_reports_folder()

    yield

    __remove_reports_folder()


@pytest.fixture(scope="module")
def create_reports_folder_module():
    __create_reports_folder()

    yield

    __remove_reports_folder()


@pytest.fixture(scope="session", autouse=True)
def set_logging_level():
    modify_settings(log_level="debug")


def __create_reports_folder() -> None:
    with suppress(Exception):
        os.mkdir(REPORTS_FOLDER)
    assert os.path.exists(REPORTS_FOLDER)


def __remove_reports_folder() -> None:
    shutil.rmtree(REPORTS_FOLDER)

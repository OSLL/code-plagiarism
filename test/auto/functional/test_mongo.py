"""MIT License.

Written 2025 by Daniil Lokosov
"""

import os
import time
from typing import Tuple

import pytest
from testcontainers.mongodb import MongoDbContainer
from utils import modify_settings, run_check

from codeplag.consts import CONFIG_PATH, DEFAULT_MONGO_PASS, DEFAULT_MONGO_USER
from codeplag.db.mongo import FeaturesRepository, MongoDBConnection, ReportRepository
from codeplag.types import ASTFeatures

CWD = os.getcwd()

PY_SIM_FILES = f"{CWD}/test/unit/codeplag/data/test1.py", f"{CWD}/test/unit/codeplag/data/test2.py"
PY_FILES = f"{CWD}/test/unit/codeplag/data/test1.py", f"{CWD}/test/unit/codeplag/data/test3.py"
CPP_SIM_FILES = (
    f"{CWD}/test/unit/codeplag/cplag/data/sample3.cpp",
    f"{CWD}/test/unit/codeplag/cplag/data/sample4.cpp",
)
CPP_FILES = (
    f"{CWD}/test/unit/codeplag/cplag/data/sample1.cpp",
    f"{CWD}/test/unit/codeplag/cplag/data/sample2.cpp",
)


@pytest.fixture(scope="module")
def mongo_container() -> MongoDbContainer:
    with MongoDbContainer(
        "mongo:6.0", username=DEFAULT_MONGO_USER, password=DEFAULT_MONGO_PASS
    ) as mongo:
        mongo.start()
        time.sleep(8)
        yield mongo


@pytest.fixture(scope="module")
def mongo_connection(mongo_container: MongoDbContainer) -> MongoDBConnection:
    host = mongo_container.get_container_host_ip()
    port = int(mongo_container.get_exposed_port(27017))
    user = mongo_container.username
    password = mongo_container.password

    conn = MongoDBConnection(
        host=host,
        port=port,
        user=user,
        password=password,
    )
    yield conn


@pytest.fixture(scope="module", autouse=True)
def setup_module(mongo_connection: MongoDBConnection) -> None:
    modify_settings(
        log_level="trace",
        reports_extension="mongo",
        mongo_host=mongo_connection.host,
        mongo_port=mongo_connection.port,
        mongo_user=mongo_connection.user,
        mongo_pass=mongo_connection.password,
    ).assert_success()

    yield

    CONFIG_PATH.write_text("{}")
    modify_settings(log_level="debug")


@pytest.fixture(autouse=True)
def clear_db(mongo_connection: MongoDBConnection) -> None:
    mongo_connection.clear_db()

    yield


@pytest.mark.parametrize(
    "extension, files, found_plag",
    [
        ("py", PY_FILES, False),
        ("py", PY_SIM_FILES, True),
        ("cpp", CPP_FILES, False),
        ("cpp", CPP_SIM_FILES, True),
    ],
)
def test_correct_mongo_connection(extension: str, files: Tuple[str, str], found_plag: bool):
    result = run_check(["--files", *files], extension=extension)

    if found_plag:
        result.assert_found_similarity()
    else:
        result.assert_success()
    assert b"Successfully connected to MongoDB!" in result.cmd_res.stdout


@pytest.mark.parametrize(
    "extension, files, found_plag",
    [
        ("py", PY_FILES, False),
        ("py", PY_SIM_FILES, True),
        ("cpp", CPP_FILES, False),
        ("cpp", CPP_SIM_FILES, True),
    ],
)
def test_saving_metadata_and_reports(
    extension: str, files: Tuple[str, str], found_plag: bool, mongo_connection: MongoDBConnection
):
    features_repo = FeaturesRepository(mongo_connection)
    compare_info_repo = ReportRepository(mongo_connection)

    run_check(["--files", *files], extension=extension)

    for file in files:
        assert features_repo.get_features(ASTFeatures(file)) is not None
    compare_info = compare_info_repo.get_compare_info(ASTFeatures(files[0]), ASTFeatures(files[1]))

    if found_plag:
        assert compare_info is not None
    else:
        assert compare_info is None


@pytest.mark.parametrize(
    "extension, files, found_plag",
    [
        ("py", PY_FILES, False),
        ("py", PY_SIM_FILES, True),
        ("cpp", CPP_FILES, False),
        ("cpp", CPP_SIM_FILES, True),
    ],
)
def test_reading_metadata_and_reports_after_saving(
    extension: str, files: Tuple[str, str], found_plag: bool, mongo_connection: MongoDBConnection
):
    run_check(["--files", *files], extension=extension)
    result = run_check(["--files", *files], extension=extension)
    logs = result.cmd_res.stdout

    found_cmp = (
        f"Compare_info found for file path: ({files[0]}, {files[1]})".encode("utf-8") in logs
        or f"Compare_info found for file path: ({files[1]}, {files[0]})".encode("utf-8") in logs
    )
    not_found_cmp = (
        f"No compare_info found for file path: ({files[0]}, {files[1]})".encode("utf-8") in logs
        or f"No compare_info found for file path: ({files[1]}, {files[0]})".encode("utf-8") in logs
    )

    for file in files:
        assert f"Features found for file path: {file}".encode("utf-8") in logs
    if found_plag:
        assert found_cmp and not not_found_cmp
    else:
        assert not_found_cmp and not found_cmp


@pytest.mark.parametrize(
    "extension, files, found_plag",
    [
        ("py", PY_FILES, False),
        ("py", PY_SIM_FILES, True),
        ("cpp", CPP_FILES, False),
        ("cpp", CPP_SIM_FILES, True),
    ],
)
def test_saving_after_file_small_change(
    extension: str, files: Tuple[str, str], found_plag: bool, mongo_connection: MongoDBConnection
):
    run_check(["--files", *files], extension=extension)

    with open(files[0], "w") as f:
        f.write("\n")

    result = run_check(["--files", *files], extension=extension)
    logs = result.cmd_res.stdout

    found_cmp = (
        f"Compare_info found for file path: ({files[0]}, {files[1]})".encode("utf-8") in logs
        or f"Compare_info found for file path: ({files[1]}, {files[0]})".encode("utf-8") in logs
    )

    try:
        assert f"No features found for file path: {files[0]}".encode("utf-8") in logs
        if found_plag:
            assert found_cmp
    finally:
        with open(files[0], "r+") as f:
            lines = f.readlines()
            f.seek(0)
            f.writelines(lines[:-1])

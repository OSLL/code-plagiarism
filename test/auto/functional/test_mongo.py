"""MIT License.

Written 2025 by Daniil Lokosov, Semidolin Artyom.
"""

import os
from pathlib import Path
from typing import Generator, Tuple

import pytest
from utils import modify_settings, run_check

from codeplag.consts import CONFIG_PATH, DEFAULT_MONGO_PORT, DEFAULT_MONGO_USER
from codeplag.db.mongo import FeaturesRepository, MongoDBConnection, ReportRepository
from codeplag.types import ASTFeatures

CWD = Path.cwd()

PY_SIM_FILES = (
    CWD / "test/unit/codeplag/data/test1.py",
    CWD / "test/unit/codeplag/data/test2.py",
)
PY_FILES = (
    CWD / "test/unit/codeplag/data/test1.py",
    CWD / "test/unit/codeplag/data/test3.py",
)
CPP_SIM_FILES = (
    CWD / "test/unit/codeplag/cplag/data/sample4.cpp",
    CWD / "test/unit/codeplag/cplag/data/sample3.cpp",
)
CPP_FILES = (
    CWD / "test/unit/codeplag/cplag/data/sample1.cpp",
    CWD / "test/unit/codeplag/cplag/data/sample2.cpp",
)

REPO_URL = "https://github.com/OSLL/code-plagiarism"
PY_GITHUB_FILES = (
    f"{REPO_URL}/blob/main/test/unit/codeplag/data/test1.py",
    f"{REPO_URL}/blob/main/test/unit/codeplag/data/test3.py",
)
CPP_GITHUB_SIM_FILES = (
    f"{REPO_URL}/blob/main/test/unit/codeplag/cplag/data/sample3.cpp",
    f"{REPO_URL}/blob/main/test/unit/codeplag/cplag/data/sample4.cpp",
)


def save_and_append_to_file(file: Path, content: str) -> str:
    with file.open("r") as f:
        data = f.read()
    with file.open("a") as f:
        f.write(content)
    return data


def recover_file(file: Path, old_content: str) -> None:
    with file.open("w") as f:
        f.write(old_content)


@pytest.fixture(scope="module")
def mongo_host() -> str:
    host = os.environ.get("MONGO_HOST")
    assert host, f"Invalid MONGO_HOST environment '{host}'."
    return host


@pytest.fixture(scope="module")
def mongo_connection(mongo_host: str) -> Generator[MongoDBConnection, None, None]:
    conn = MongoDBConnection(
        host=mongo_host,
        port=DEFAULT_MONGO_PORT,
        user=DEFAULT_MONGO_USER,
        password=DEFAULT_MONGO_USER,
    )
    yield conn


@pytest.fixture(scope="module", autouse=True)
def setup_module(mongo_connection: MongoDBConnection) -> Generator[None, None, None]:
    modify_settings(
        log_level="trace",
        reports_extension="mongo",
        mongo_host=mongo_connection.host,
        mongo_port=mongo_connection.port,
        mongo_user=mongo_connection.user,
        mongo_pass=mongo_connection.password,
    ).assert_success()
    first_cond = not modify_settings(environment=".env").cmd_res.returncode
    second_cond = os.environ.get("ACCESS_TOKEN", "") != ""

    assert first_cond or second_cond

    yield

    CONFIG_PATH.write_text("{}")
    modify_settings(log_level="debug")


@pytest.fixture(autouse=True)
def clear_db(mongo_connection: MongoDBConnection) -> Generator[None, None, None]:
    mongo_connection.clear_db()

    yield


@pytest.mark.parametrize(
    "cmd, files, extension, found_plag",
    [
        ("--files", PY_FILES, "py", False),
        ("--files", PY_SIM_FILES, "py", True),
        ("--files", CPP_FILES, "cpp", False),
        ("--files", CPP_SIM_FILES, "cpp", True),
        ("--github-files", PY_GITHUB_FILES, "py", False),
        ("--github-files", CPP_GITHUB_SIM_FILES, "cpp", True),
    ],
)
def test_correct_mongo_connection(
    cmd: str, files: Tuple[Path, Path], extension: str, found_plag: bool
):
    result = run_check([cmd, *files], extension=extension)

    if found_plag:
        result.assert_found_similarity()
    else:
        result.assert_success()
    assert b"Successfully connected to MongoDB!" in result.cmd_res.stdout


@pytest.mark.parametrize(
    "cmd, files, extension, found_plag",
    [
        ("--files", PY_FILES, "py", False),
        ("--files", PY_SIM_FILES, "py", True),
        ("--files", CPP_FILES, "cpp", False),
        ("--files", CPP_SIM_FILES, "cpp", True),
        ("--github-files", PY_GITHUB_FILES, "py", False),
        ("--github-files", CPP_GITHUB_SIM_FILES, "cpp", True),
    ],
)
def test_saving_metadata_and_reports(
    cmd: str,
    files: Tuple[Path, Path],
    extension: str,
    found_plag: bool,
    mongo_connection: MongoDBConnection,
):
    features_repo = FeaturesRepository(mongo_connection)
    compare_info_repo = ReportRepository(mongo_connection)

    run_check([cmd, *files], extension=extension)

    for file in files:
        assert features_repo.get_features(ASTFeatures(file)) is not None
    compare_info = compare_info_repo.get_compare_info(ASTFeatures(files[0]), ASTFeatures(files[1]))

    if found_plag:
        assert compare_info is not None
    else:
        assert compare_info is None


@pytest.mark.parametrize(
    "cmd, files, extension, found_plag",
    [
        ("--files", PY_FILES, "py", False),
        ("--files", PY_SIM_FILES, "py", True),
        ("--files", CPP_FILES, "cpp", False),
        ("--files", CPP_SIM_FILES, "cpp", True),
        ("--github-files", PY_GITHUB_FILES, "py", False),
        ("--github-files", CPP_GITHUB_SIM_FILES, "cpp", True),
    ],
)
def test_reading_metadata_and_reports_after_saving(
    cmd: str, files: Tuple[Path, Path], extension: str, found_plag: bool
):
    run_check([cmd, *files], extension=extension)
    result = run_check([cmd, *files], extension=extension)
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
    "extension, files",
    [
        ("py", PY_FILES),
        ("py", PY_SIM_FILES),
        ("cpp", CPP_FILES),
        ("cpp", CPP_SIM_FILES),
    ],
)
def test_saving_after_file_minor_change(extension: str, files: Tuple[Path, Path]):
    run_check(["--files", *files], extension=extension)

    old = save_and_append_to_file(files[0], "\n")

    result = run_check(["--files", *files], extension=extension)
    recover_file(files[0], old)
    logs = result.cmd_res.stdout

    write_cmp = (
        f"Document for ({files[0]}, {files[1]}) successfully inserted/updated.".encode("utf-8")
        in logs
        or f"Document for ({files[1]}, {files[0]}) successfully inserted/updated.".encode("utf-8")
        in logs
    )

    assert f"Document for path {files[0]} successfully inserted/updated.".encode("utf-8") in logs
    assert not write_cmp


@pytest.mark.parametrize(
    "extension, files, found_plag",
    [
        ("py", PY_FILES, False),
        ("py", PY_SIM_FILES, True),
        ("cpp", CPP_FILES, False),
        ("cpp", CPP_SIM_FILES, True),
    ],
)
def test_saving_after_file_significant_change(
    extension: str, files: Tuple[Path, Path], found_plag: bool
):
    run_check(["--files", *files], extension=extension)

    old = save_and_append_to_file(
        files[0], "\ndef foo(): return 1" if extension == "py" else "\nint foo() { return 2; }"
    )

    result = run_check(["--files", *files], extension=extension)
    recover_file(files[0], old)
    logs = result.cmd_res.stdout

    write_cmp = (
        f"Document for ({files[0]}, {files[1]}) successfully inserted/updated.".encode("utf-8")
        in logs
        or f"Document for ({files[1]}, {files[0]}) successfully inserted/updated.".encode("utf-8")
        in logs
    )

    assert f"Document for path {files[0]} successfully inserted/updated.".encode("utf-8") in logs
    if found_plag:
        assert write_cmp
    else:
        assert not write_cmp

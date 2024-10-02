from __future__ import annotations

import os

import pytest
from utils import modify_settings, run_check, run_util

from codeplag.consts import CONFIG_PATH, UTIL_NAME, UTIL_VERSION

CWD = os.getcwd()
CPP_FILES = [
    "test/unit/codeplag/cplag/data/sample1.cpp",
    "test/unit/codeplag/cplag/data/sample2.cpp",
]
PY_FILES = ["src/codeplag/pyplag/astwalkers.py", "setup.py"]
CPP_DIR = "test/unit/codeplag/cplag/data"
PY_DIRS = ["test/unit/codeplag/cplag", "test/unit"]
REPO_URL = "https://github.com/OSLL/code-plagiarism"
CPP_GITHUB_FILES = [
    f"{REPO_URL}/blob/main/test/unit/codeplag/cplag/data/sample3.cpp",
    f"{REPO_URL}/blob/main/test/unit/codeplag/cplag/data/sample4.cpp",
]
PY_GITHUB_FILES = [
    f"{REPO_URL}/blob/main/src/codeplag/pyplag/utils.py",
    f"{REPO_URL}/blob/main/setup.py",
]
CPP_GITHUB_DIR = f"{REPO_URL}/tree/main/test"
PY_GITHUB_DIR = f"{REPO_URL}/blob/main/src/codeplag/pyplag"


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    first_cond = not modify_settings(environment=".env").cmd_res.returncode
    second_cond = os.environ.get("ACCESS_TOKEN", "") != ""

    assert first_cond or second_cond

    yield

    CONFIG_PATH.write_text("{}")


def test_check_util_version():
    result = run_util(["--version"])

    result.assert_success()
    assert f"{UTIL_NAME} {UTIL_VERSION}" in result.cmd_res.stdout.decode("utf-8")


@pytest.mark.parametrize(
    "cmd, out",
    [
        (["--files", *CPP_FILES], b"Getting works features from files"),
        (
            ["--directories", CPP_DIR],
            f"Getting works features from {CWD}/{CPP_DIR}".encode("utf-8"),
        ),
        (
            ["--github-files", *CPP_GITHUB_FILES],
            b"Getting works features from GitHub urls",
        ),
        (
            ["--github-project-folders", CPP_GITHUB_DIR],
            f"Getting works features from {CPP_GITHUB_DIR}".encode("utf-8"),
        ),
        (
            ["--github-user", "OSLL", "--repo-regexp", "code-plag"],
            f"Getting works features from {REPO_URL}".encode("utf-8"),
        ),
    ],
)
def test_compare_cpp_files(cmd: list[str], out: bytes):
    result = run_check(cmd, extension="cpp")

    result.assert_success()
    assert out in result.cmd_res.stdout


@pytest.mark.parametrize(
    "cmd, out",
    [
        (["--files", *PY_FILES], b"Getting works features from files"),
        (
            ["--directories", *PY_DIRS],
            f"Getting works features from {CWD}/{PY_DIRS[0]}".encode("utf-8"),
        ),
        (
            ["--github-files", *PY_GITHUB_FILES],
            b"Getting works features from GitHub urls",
        ),
        (
            ["--github-project-folders", PY_GITHUB_DIR],
            f"Getting works features from {PY_GITHUB_DIR}".encode("utf-8"),
        ),
        (
            ["--github-user", "OSLL", "--repo-regexp", "code-plag"],
            f"Getting works features from {REPO_URL}".encode("utf-8"),
        ),
        (
            ["--directories", *PY_DIRS, "--mode", "one_to_one"],
            f"Getting works features from {CWD}/{PY_DIRS[0]}".encode("utf-8"),
        ),
    ],
)
def test_compare_py_files(cmd: list[str], out: bytes):
    result = run_check(cmd)

    result.assert_success()
    assert out in result.cmd_res.stdout


@pytest.mark.parametrize(
    "cmd",
    [
        ["--files", *PY_FILES],
        ["--github-files", *PY_GITHUB_FILES],
        ["--directories", *PY_DIRS],
        ["--github-project-folders", PY_GITHUB_DIR],
    ],
)
def test_check_failed_when_repo_regexp_provided_without_required_args(
    cmd: list[str],
):
    result = run_check(cmd + ["--repo-regexp", "something"])

    result.assert_failed()
    assert result.cmd_res.returncode == 2


@pytest.mark.parametrize(
    "cmd",
    [
        ["--files", *PY_FILES],
        ["--github-files", *PY_GITHUB_FILES],
    ],
)
def test_check_failed_when_path_regexp_provided_without_required_args(
    cmd: list[str],
):
    result = run_check(cmd + ["--path-regexp", "something"])

    result.assert_failed()
    assert result.cmd_res.returncode == 2

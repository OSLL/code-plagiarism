from __future__ import annotations

import os

import pytest
from const import REPORTS_FOLDER
from utils import modify_settings, run_check, run_util

from codeplag.consts import CONFIG_PATH, UTIL_NAME, UTIL_VERSION
from codeplag.types import ShortOutput

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
def setup_module(create_reports_folder_module: None):
    modify_settings(reports=REPORTS_FOLDER).assert_success()
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
    "cmd, out, found_plag",
    [
        (["--files", *CPP_FILES], b"Getting works features from files", False),
        (
            ["--directories", CPP_DIR],
            f"Getting works features from {CWD}/{CPP_DIR}".encode("utf-8"),
            True,
        ),
        (
            ["--github-urls", *CPP_GITHUB_FILES, CPP_GITHUB_DIR],
            b"Getting works features from GitHub urls",
            True,
        ),
        (
            ["--github-user", "OSLL", "--repo-regexp", "code-plag"],
            f"Getting works features from {REPO_URL}".encode("utf-8"),
            True,
        ),
    ],
)
def test_compare_cpp_files(cmd: list[str], out: bytes, found_plag: bool):
    result = run_check(cmd, extension="cpp")

    if found_plag:
        result.assert_found_similarity()
    else:
        result.assert_success()
    assert out in result.cmd_res.stdout


@pytest.mark.parametrize(
    "cmd, out, found_plag",
    [
        (["--files", *PY_FILES], b"Getting works features from files", False),
        (
            ["--directories", *PY_DIRS],
            f"Getting works features from {CWD}/{PY_DIRS[0]}".encode("utf-8"),
            True,
        ),
        (
            ["--github-urls", *PY_GITHUB_FILES, PY_GITHUB_DIR],
            b"Getting works features from GitHub urls",
            False,
        ),
        (
            ["--github-user", "OSLL", "--repo-regexp", "code-plag"],
            f"Getting works features from {REPO_URL}".encode("utf-8"),
            True,
        ),
        (
            ["--directories", *PY_DIRS, "--mode", "one_to_one"],
            f"Getting works features from {CWD}/{PY_DIRS[0]}".encode("utf-8"),
            False,
        ),
    ],
)
def test_compare_py_files(cmd: list[str], out: bytes, found_plag: bool):
    result = run_check(cmd)

    if found_plag:
        result.assert_found_similarity()
    else:
        result.assert_success()
    assert out in result.cmd_res.stdout


def test_check_short_output() -> None:
    cmd = ["--directories", CPP_DIR]
    if len(list(REPORTS_FOLDER.iterdir())):
        next(REPORTS_FOLDER.glob("*")).unlink()
    modify_settings(short_output=ShortOutput.SHOW_ALL).assert_success()
    result = run_check(cmd, extension="cpp")
    result.assert_found_similarity()
    first_check_stdout_lines = result.cmd_res.stdout.decode("utf-8").split("\n")

    modify_settings(short_output=ShortOutput.SHOW_NEW).assert_success()
    result = run_check(cmd, extension="cpp")
    result.assert_found_similarity()
    assert len(first_check_stdout_lines) != len(result.cmd_res.stdout.decode("utf-8").split("\n"))
    modify_settings(short_output=ShortOutput.SHOW_ALL).assert_success()


@pytest.mark.parametrize(
    "cmd",
    [
        ["--files", *PY_FILES],
        ["--github-urls", *PY_GITHUB_FILES, PY_GITHUB_DIR],
        ["--directories", *PY_DIRS],
    ],
)
def test_check_failed_when_repo_regexp_provided_without_required_args(
    cmd: list[str],
):
    result = run_check(cmd + ["--repo-regexp", "something"])

    result.assert_argparse_error()


@pytest.mark.parametrize(
    "cmd",
    [
        ["--files", *PY_FILES],
        ["--github-urls", *PY_GITHUB_FILES],
    ],
)
def test_check_failed_when_path_regexp_provided_without_required_args(
    cmd: list[str],
):
    result = run_check(cmd + ["--path-regexp", "something"])

    result.assert_argparse_error()

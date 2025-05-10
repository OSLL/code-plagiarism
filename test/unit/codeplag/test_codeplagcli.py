import argparse
import builtins
import os
from pathlib import Path
from typing import Final

import pytest

from codeplag.codeplagcli import CodeplagCLI, DirPath, FilePath

CWD: Final[Path] = Path(os.getcwd())


@pytest.fixture(scope="module", autouse=True)
def setup():
    builtins.__dict__["_"] = str

    yield


@pytest.mark.parametrize(
    "path, expected",
    [
        ("./src", CWD / "src"),
        ("./src/codeplag", CWD / "src/codeplag"),
        ("src/codeplag", CWD / "src/codeplag"),
    ],
)
def test_dir_path(path: str, expected: Path):
    assert DirPath(path) == expected


@pytest.mark.parametrize("path", ["bad_dirpath", "Makefile"])
def test_dir_path_bad(path: str):
    with pytest.raises(argparse.ArgumentTypeError):
        DirPath(path)


@pytest.mark.parametrize(
    "path, expected", [("Makefile", CWD / "Makefile"), ("./LICENSE", CWD / "LICENSE")]
)
def test_file_path(path: str, expected: Path):
    assert FilePath(path) == expected


@pytest.mark.parametrize(
    "path",
    [
        "./src",
        "./profile.d",
        "bad_filepath",
    ],
)
def test_file_path_bad(path: str):
    with pytest.raises(argparse.ArgumentTypeError):
        FilePath(path)


@pytest.mark.parametrize(
    "args",
    [
        ["check", "--extension", "py", "--directories", "src/", "src/"],
        [
            "check",
            "--extension",
            "py",
            "--github-project-folders",
            "https://github.com/OSLL/code-plagiarism/tree/main/src",
            "https://github.com/OSLL/code-plagiarism/tree/main/src",
        ],
        [
            "check",
            "--extension",
            "py",
            "--github-files",
            "https://github.com/OSLL/code-plagiarism/blob/main/setup.py",
            "https://github.com/OSLL/code-plagiarism/blob/main/setup.py",
        ],
        ["check", "--extension", "py", "--files", "setup.py", "setup.py"],
        ["check", "--extension", "pypy"],
    ],
    ids=[
        "Twice repeated directory.",
        "Twice repeated GitHub project folder.",
        "Twice repeated GitHub file.",
        "Twice repeated file.",
        "Invalid extension.",
    ],
)
def test_get_parsed_args_failed(args: list[str]):
    codeplagcli = CodeplagCLI()
    with pytest.raises(SystemExit):
        codeplagcli.parse_args(args=args)


@pytest.mark.parametrize(
    "args,expected",
    [
        (["check", "--extension", "cpp"], {"extension": "cpp", "root": "check"}),
        (
            ["check", "--extension", "py", "--files", "setup.py"],
            {"extension": "py", "root": "check", "files": [Path("setup.py").absolute()]},
        ),
        (
            ["report", "create", "--path", "./", "--type", "general"],
            {
                "root": "report",
                "report": "create",
                "type": "general",
                "path": Path("./"),
                "first_root_path": None,
                "second_root_path": None,
            },
        ),
        (
            [
                "report",
                "create",
                "--path",
                "./",
                "--type",
                "general",
                "--first-root-path",
                "codeplag",
                "--second-root-path",
                "webparsers",
            ],
            {
                "root": "report",
                "report": "create",
                "type": "general",
                "path": Path("./"),
                "first_root_path": "codeplag",
                "second_root_path": "webparsers",
            },
        ),
    ],
    ids=[
        "Only extension provided.",
        "Extension and one file provided.",
        "Create general report from all records.",
        "Create general report from selected records.",
    ],
)
def test_get_parsed_args(args: list[str], expected: argparse.Namespace):
    codeplagcli = CodeplagCLI()
    namespace = codeplagcli.parse_args(args=args)
    for key, value in expected.items():
        assert getattr(namespace, key) == value

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
        ("./src"),
        ("./profile.d"),
        ("bad_filepath"),
    ],
)
def test_file_path_bad(path: str):
    with pytest.raises(argparse.ArgumentTypeError):
        FilePath(path)


@pytest.mark.parametrize(
    "args",
    [
        (["--extension", "py", "--directories", "src/", "src/"],),
        (
            [
                "--extension",
                "py",
                "--github-project-folders",
                "https://github.com/OSLL/code-plagiarism/tree/main/src",
                "https://github.com/OSLL/code-plagiarism/tree/main/src",
            ],
        ),
        (
            [
                "--extension",
                "py",
                "--github-files",
                "https://github.com/OSLL/code-plagiarism/blob/main/setup.py",
                "https://github.com/OSLL/code-plagiarism/blob/main/setup.py",
            ],
        ),
        (["--extension", "py", "--files", "setup.py", "setup.py"],),
    ],
)
def test_get_parsed_args(args: list[str]):
    codeplagcli = CodeplagCLI()
    with pytest.raises(SystemExit):
        codeplagcli.parse_args(args=args)

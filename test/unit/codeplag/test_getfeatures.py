import re
from pathlib import Path

import pytest
from codeplag.getfeatures import get_files_path_from_directory
from pytest_mock import MockerFixture


@pytest.fixture
def os_walk(request, mocker: MockerFixture):
    return mocker.patch("os.walk", return_value=request.param)


@pytest.mark.parametrize(
    "os_walk, extensions, path_regexp, expected",
    [
        [
            [
                ("dir1", [], ["test_utils.py", "some.cpp", "compiled.pyc"]),
                ("dir2", [], ["test1.py", "test2.py", "Readme.md"]),
            ],
            (re.compile("[.]py$"),),
            None,
            [Path("dir1/test_utils.py"), Path("dir2/test1.py"), Path("dir2/test2.py")],
        ],
        [
            [
                ("dir1", [], ["test_utils.py", "some.cpp", "compiled.pyc"]),
                ("dir2", [], ["test1.py", "test2.py", "Readme.md"]),
            ],
            None,
            None,
            [
                Path("dir1/test_utils.py"),
                Path("dir1/some.cpp"),
                Path("dir1/compiled.pyc"),
                Path("dir2/test1.py"),
                Path("dir2/test2.py"),
                Path("dir2/Readme.md"),
            ],
        ],
        [
            [
                ("dir1", [], ["test_utils.py", "some.cpp", "compiled.pyc"]),
                ("dir2", [], ["test1.py", "test2.py", "Readme.md"]),
            ],
            (re.compile("[.]py$"),),
            re.compile("test\\d"),
            [Path("dir2/test1.py"), Path("dir2/test2.py")],
        ],
    ],
    indirect=["os_walk"],
)
def test_get_files_path_from_directory(os_walk, extensions, path_regexp, expected):
    files = get_files_path_from_directory(
        Path("./"), path_regexp=path_regexp, extensions=extensions
    )
    os_walk.assert_called()

    assert files == expected

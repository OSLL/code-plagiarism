import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from codeplag.getfeatures import get_files_path_from_directory, set_sha256
from codeplag.types import ASTFeatures, Extensions


@pytest.fixture
def os_walk(request: pytest.FixtureRequest, mocker: MockerFixture) -> MagicMock:
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
def test_get_files_path_from_directory(
    os_walk: MagicMock,
    extensions: Extensions | None,
    path_regexp: re.Pattern | None,
    expected: list[Path],
):
    files = get_files_path_from_directory(
        Path("./"), path_regexp=path_regexp, extensions=extensions
    )
    os_walk.assert_called()

    assert files == expected


class TestASTFeatures:
    def test_astfeatures_equal(self) -> None:
        assert ASTFeatures("foo/bar") == ASTFeatures("foo/bar")

    def test_astfeatures_different(self) -> None:
        assert ASTFeatures("foo/bar") != ASTFeatures("foo/bar2")

    def test_astfeatures_less(self) -> None:
        assert ASTFeatures("foo/bar") < ASTFeatures("foo/bbr")

    def test_astfeatures_invalid_compares(self) -> None:
        with pytest.raises(NotImplementedError):
            assert ASTFeatures("foo/bar") == 1
        with pytest.raises(NotImplementedError):
            assert ASTFeatures("foo/bar") < 1

    def test_set_sha256(self, tmp_path: Path) -> None:
        filepath = tmp_path / "foo_bar"
        filepath.touch()
        features = ASTFeatures(filepath)
        features.tokens = [1, 2, 3, 4, 5]
        features = set_sha256(lambda: features)()

        assert (
            features.sha256 == "0c049903ce2330190375d4c1f2e489888c9ebe39daf75b2564e591e8bc1afe72"
        )
        assert features.modify_date

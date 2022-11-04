import argparse

import pytest

from codeplag.codeplagcli import CodeplagCLI, DirPath, FilePath


@pytest.mark.parametrize(
    "path, out",
    [
        ('./src', 'src'),
        ('./src/codeplag', 'src/codeplag'),
        ('src/codeplag', 'src/codeplag')
    ]
)
def test_dir_path(path, out):
    assert DirPath(path).__str__() == out


@pytest.mark.parametrize(
    "path",
    [
        ('bad_dirpath'),
        ('Makefile')
    ]
)
def test_dir_path_bad(path):
    with pytest.raises(argparse.ArgumentTypeError):
        DirPath(path)


@pytest.mark.parametrize(
    "path, out",
    [
        ('Makefile', 'Makefile'),
        ('./LICENSE', 'LICENSE')
    ]
)
def test_file_path(path, out):
    assert FilePath(path).__str__() == out


@pytest.mark.parametrize(
    "path",
    [
        ('./src'),
        ('./profile.d'),
        ('bad_filepath'),
    ]
)
def test_file_path_bad(path):
    with pytest.raises(argparse.ArgumentTypeError):
        FilePath(path)


@pytest.mark.parametrize(
    'args, raises',
    [
        (
            ['--extension', 'py', '--directories', 'src/', 'src/'],
            pytest.raises(SystemExit)
        ),
        (
            [
                '--extension', 'py', '--github-project-folders',
                'https://github.com/OSLL/code-plagiarism/tree/main/src',
                'https://github.com/OSLL/code-plagiarism/tree/main/src'
            ],
            pytest.raises(SystemExit)
        ),
        (
            [
                '--extension', 'py', '--github-files',
                'https://github.com/OSLL/code-plagiarism/blob/main/setup.py',
                'https://github.com/OSLL/code-plagiarism/blob/main/setup.py'
            ],
            pytest.raises(SystemExit)
        ),
        (
            ['--extension', 'py', '--files', 'setup.py', 'setup.py'],
            pytest.raises(SystemExit)
        ),
    ]
)
def test_get_parsed_args(args, raises):
    codeplagcli = CodeplagCLI()
    with raises:
        codeplagcli.parse_args(args=args)

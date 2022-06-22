import argparse

import pytest

from codeplag.codeplagcli import (dir_path, env_path, file_path,
                                  get_parsed_args, github_url)


@pytest.mark.parametrize(
    "path, out",
    [
        ('./src', 'src'),
        ('./profile.d', 'profile.d'),
        ('profile.d', 'profile.d')
    ]
)
def test_dir_path(path, out):
    assert dir_path(path) == out


@pytest.mark.parametrize(
    "path",
    [
        ('bad_dirpath'),
        ('Makefile')
    ]
)
def test_dir_path_bad(path):
    with pytest.raises(argparse.ArgumentTypeError):
        dir_path(path)


@pytest.mark.parametrize(
    "path, out",
    [
        ('Makefile', 'Makefile'),
        ('./LICENSE', 'LICENSE')
    ]
)
def test_file_path(path, out):
    assert file_path(path) == out


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
        file_path(path)


@pytest.mark.parametrize(
    'filepath, out',
    [
        ('Makefile', 'Makefile'),
        ('./LICENSE', 'LICENSE'),
        ('./src', ''),
        ('./profile.d', ''),
        ('bad_filepath', '')
    ]
)
def test_env_path(filepath, out):
    assert env_path(filepath) == out


def test_github_url():
    assert github_url(
        'https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/logger.py'
    ) == 'https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/logger.py'

    with pytest.raises(argparse.ArgumentTypeError):
        github_url("bad_link")


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
    with raises:
        get_parsed_args(args)

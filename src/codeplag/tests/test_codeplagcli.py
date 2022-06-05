import argparse
import pytest

from codeplag.codeplagcli import (
    dir_path, file_path, env_path, github_url
)


def test_dir_path():
    assert dir_path('./src') == './src'
    assert dir_path('./profile.d') == './profile.d'
    assert dir_path('profile.d') == 'profile.d'

    with pytest.raises(argparse.ArgumentTypeError):
        dir_path('bad_dirpath')
    with pytest.raises(argparse.ArgumentTypeError):
        dir_path('Makefile')


def test_file_path():
    assert file_path('Makefile') == 'Makefile'
    assert file_path('./LICENSE') == './LICENSE'

    with pytest.raises(argparse.ArgumentTypeError):
        file_path('./src')
    with pytest.raises(argparse.ArgumentTypeError):
        file_path('./profile.d')
    with pytest.raises(argparse.ArgumentTypeError):
        file_path('bad_filepath')


def test_env_path():
    assert env_path('Makefile') == 'Makefile'
    assert env_path('./LICENSE') == './LICENSE'

    assert env_path('./src') == ""
    assert env_path('./profile.d') == ""
    assert env_path('bad_filepath') == ""


def test_github_url():
    assert github_url(
        'https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/logger.py'
    ) == 'https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/logger.py'

    with pytest.raises(argparse.ArgumentTypeError):
        github_url("bad_link")

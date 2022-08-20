import subprocess

from codeplag.consts import UTIL_NAME

SUCCESS_CODE = 0


def run_util(cmd, ext='py'):
    return subprocess.run(
        [UTIL_NAME] + ['--extension', ext] + cmd,
        stdout=subprocess.PIPE
    )

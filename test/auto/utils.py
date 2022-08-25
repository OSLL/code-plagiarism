import subprocess

from codeplag.consts import UTIL_NAME

SUCCESS_CODE = 0


def run_cmd(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE)


def run_util(cmd, ext='py'):
    return run_cmd([UTIL_NAME] + ['--extension', ext] + cmd)

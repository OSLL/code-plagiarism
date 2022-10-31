import subprocess
from pathlib import Path
from typing import List, Literal, Optional, Union

from codeplag.consts import UTIL_NAME

SUCCESS_CODE = 0


def run_cmd(cmd: List[Union[str, Path]]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE)


def run_util(
    cmd: List[Union[str, Path]],
    root: Optional[Literal["check", "settings"]] = None
) -> subprocess.CompletedProcess:
    command = [] if root is None else [root]
    return run_cmd([UTIL_NAME] + command + cmd)


def run_check(cmd: List[Union[str, Path]], extension: str = 'py') -> subprocess.CompletedProcess:
    return run_util(['--extension', extension] + cmd, root="check")


def modify_settings(reports: Union[Path, str]) -> subprocess.CompletedProcess:
    return run_util(['modify', '--reports', reports], root='settings')

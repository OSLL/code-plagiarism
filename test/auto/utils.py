import subprocess
from pathlib import Path
from typing import List, Literal, Optional, Union

from codeplag.consts import UTIL_NAME
from codeplag.types import Flag, Language, ReportsExtension


class CmdResult:
    def __init__(self, cmd_res: subprocess.CompletedProcess):
        self.cmd_res = cmd_res

    def assert_success(self) -> None:
        assert not self.cmd_res.returncode

    def assert_failed(self) -> None:
        assert self.cmd_res.returncode


def run_cmd(cmd: List[str]) -> CmdResult:
    return CmdResult(
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    )


def run_util(
    cmd: List[str],
    root: Optional[Literal["check", "settings", "report"]] = None,
    verbose: bool = True,
) -> CmdResult:
    verbose_opt = ["--verbose"] if verbose else []
    root_cmd = [] if root is None else [root]

    return run_cmd([UTIL_NAME] + verbose_opt + root_cmd + cmd)


def run_check(cmd: List[str], extension: str = "py", verbose: bool = True) -> CmdResult:
    return run_util(["--extension", extension] + cmd, root="check", verbose=verbose)


def create_report(path: Path) -> CmdResult:
    return run_util(["create", "--path", str(path)], root="report")


def modify_settings(
    reports: Optional[Union[Path, str]] = None,
    environment: Optional[Union[Path, str]] = None,
    threshold: Optional[int] = None,
    show_progress: Optional[Flag] = None,
    reports_extension: Optional[ReportsExtension] = None,
    language: Optional[Language] = None,
) -> CmdResult:
    reports_opt = ["--reports", str(reports)] if reports else []
    environment_opt = ["--environment", str(environment)] if environment else []
    threshold_opt = ["--threshold", str(threshold)] if threshold else []
    show_progress_opt = ["--show_progress", str(show_progress)] if show_progress else []
    reports_extension_opt = (
        ["--reports_extension", reports_extension] if reports_extension else []
    )
    language_opt = ["--language", language] if language else []

    return run_util(
        ["modify"]
        + reports_opt
        + environment_opt
        + threshold_opt
        + show_progress_opt
        + reports_extension_opt
        + language_opt,
        root="settings",
    )


def show_settings() -> CmdResult:
    return run_util(["show"], root="settings")

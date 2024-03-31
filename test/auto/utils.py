import subprocess
from pathlib import Path
from typing import Any, List, Literal, Optional, Union

from codeplag.consts import UTIL_NAME
from codeplag.types import Flag, Language, ReportsExtension, Threshold


class CmdResult:
    def __init__(self, cmd_res: subprocess.CompletedProcess):
        self.cmd_res = cmd_res

    def assert_success(self) -> None:
        assert not self.cmd_res.returncode, str(self.cmd_res)

    def assert_failed(self) -> None:
        assert self.cmd_res.returncode, str(self.cmd_res)


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
    threshold: Optional[Threshold] = None,
    show_progress: Optional[Flag] = None,
    reports_extension: Optional[ReportsExtension] = None,
    language: Optional[Language] = None,
    workers: Optional[int] = None,
) -> CmdResult:
    def create_opt(key: str, value: Optional[Any]) -> List[str]:
        return [f"--{key}", str(value)] if value is not None else []

    return run_util(
        ["modify"]
        + create_opt("reports", reports)
        + create_opt("environment", environment)
        + create_opt("threshold", threshold)
        + create_opt("show_progress", show_progress)
        + create_opt("reports_extension", reports_extension)
        + create_opt("language", language)
        + create_opt("workers", workers),
        root="settings",
    )


def show_settings() -> CmdResult:
    return run_util(["show"], root="settings")

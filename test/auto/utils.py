import subprocess
from pathlib import Path
from typing import Any, Literal

from codeplag.consts import UTIL_NAME
from codeplag.types import (
    Flag,
    Language,
    LogLevel,
    ReportsExtension,
    ReportType,
    Threshold,
)


class CmdResult:
    def __init__(self, cmd_res: subprocess.CompletedProcess):
        self.cmd_res = cmd_res

    def assert_success(self) -> None:
        assert not self.cmd_res.returncode, str(self.cmd_res)

    def assert_failed(self) -> None:
        assert self.cmd_res.returncode, str(self.cmd_res)


def run_cmd(cmd: list[str]) -> CmdResult:
    return CmdResult(
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    )


def run_util(
    cmd: list[str],
    root: Literal["check", "settings", "report"] | None = None,
) -> CmdResult:
    root_cmd = [] if root is None else [root]

    return run_cmd([UTIL_NAME] + root_cmd + cmd)


def run_check(cmd: list[str], extension: str = "py") -> CmdResult:
    return run_util(["--extension", extension] + cmd, root="check")


def create_report(path: Path, report_type: ReportType) -> CmdResult:
    return run_util(
        ["create", "--path", str(path), "--type", report_type], root="report"
    )


def modify_settings(
    reports: Path | str | None = None,
    environment: Path | str | None = None,
    threshold: Threshold | None = None,
    show_progress: Flag | None = None,
    reports_extension: ReportsExtension | None = None,
    language: Language | None = None,
    log_level: LogLevel | None = None,
    workers: int | None = None,
) -> CmdResult:
    def create_opt(key: str, value: Any | None) -> list[str]:
        return [f"--{key}", str(value)] if value is not None else []

    return run_util(
        ["modify"]
        + create_opt("reports", reports)
        + create_opt("environment", environment)
        + create_opt("threshold", threshold)
        + create_opt("show_progress", show_progress)
        + create_opt("reports_extension", reports_extension)
        + create_opt("language", language)
        + create_opt("log-level", log_level)
        + create_opt("workers", workers),
        root="settings",
    )


def show_settings() -> CmdResult:
    return run_util(["show"], root="settings")

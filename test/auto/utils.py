import subprocess
from pathlib import Path
from typing import Any, Literal

from typing_extensions import Self

from codeplag.consts import UTIL_NAME
from codeplag.types import (
    ExitCode,
    Flag,
    Language,
    LogLevel,
    MaxDepth,
    NgramsLength,
    ReportsExtension,
    ReportType,
    Threshold,
)


class CmdResult:
    def __init__(self: Self, cmd_res: subprocess.CompletedProcess) -> None:
        self.cmd_res = cmd_res

    def assert_success(self: Self) -> None:
        assert not self.cmd_res.returncode, str(self.cmd_res)

    def assert_failed(self: Self) -> None:
        assert self.cmd_res.returncode, str(self.cmd_res)

    def assert_found_plagiarism(self: Self) -> None:
        assert self.cmd_res.returncode == ExitCode.EXIT_FOUND_SIM, str(self.cmd_res)


def run_cmd(cmd: list[str]) -> CmdResult:
    return CmdResult(subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE))


def run_util(
    cmd: list[str],
    root: Literal["check", "settings", "report"] | None = None,
) -> CmdResult:
    root_cmd = [] if root is None else [root]

    return run_cmd([UTIL_NAME] + root_cmd + cmd)


def run_check(cmd: list[str], extension: str = "py") -> CmdResult:
    return run_util(["--extension", extension] + cmd, root="check")


def create_opt(key: str, value: Any | None) -> list[str]:
    return [f"--{key}", str(value)] if value is not None else []


def create_report(
    path: Path,
    report_type: ReportType,
    first_root_path: str | None = None,
    second_root_path: str | None = None,
) -> CmdResult:
    return run_util(
        ["create", "--path", str(path), "--type", report_type]
        + create_opt("first-root-path", first_root_path)
        + create_opt("second-root-path", second_root_path),
        root="report",
    )


def modify_settings(
    reports: Path | str | None = None,
    environment: Path | str | None = None,
    threshold: Threshold | None = None,
    max_depth: MaxDepth | None = None,
    ngrams_length: NgramsLength | None = None,
    show_progress: Flag | None = None,
    short_output: Flag | None = None,
    reports_extension: ReportsExtension | None = None,
    language: Language | None = None,
    log_level: LogLevel | None = None,
    workers: int | None = None,
) -> CmdResult:
    return run_util(
        ["modify"]
        + create_opt("reports", reports)
        + create_opt("environment", environment)
        + create_opt("threshold", threshold)
        + create_opt("max-depth", max_depth)
        + create_opt("ngrams-length", ngrams_length)
        + create_opt("show_progress", show_progress)
        + create_opt("short-output", short_output)
        + create_opt("reports_extension", reports_extension)
        + create_opt("language", language)
        + create_opt("log-level", log_level)
        + create_opt("workers", workers),
        root="settings",
    )


def show_settings() -> CmdResult:
    return run_util(["show"], root="settings")

import subprocess
from enum import Enum
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
    ShortOutput,
    Threshold,
)


class CmdResult:
    def __init__(self: Self, cmd_res: subprocess.CompletedProcess) -> None:
        self.cmd_res = cmd_res

    def assert_success(self: Self) -> None:
        assert not self.cmd_res.returncode, str(self.cmd_res)

    def assert_failed(self: Self) -> None:
        assert self.cmd_res.returncode, str(self.cmd_res)

    def assert_argparse_error(self: Self) -> None:
        assert self.cmd_res.returncode == ExitCode.EXIT_PARSER, str(self.cmd_res)

    def assert_found_similarity(self: Self) -> None:
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
    if value is None:
        return []
    if isinstance(value, Enum):
        return [f"--{key}", str(value.value)]
    return [f"--{key}", str(value)]


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
    short_output: ShortOutput | None = None,
    reports_extension: ReportsExtension | None = None,
    language: Language | None = None,
    log_level: LogLevel | None = None,
    workers: int | None = None,
    mongo_host: str | None = None,
    mongo_port: int | None = None,
    mongo_user: str | None = None,
    mongo_pass: str | None = None,
) -> CmdResult:
    cmd = ["modify"]
    cmd += create_opt("reports", reports)
    cmd += create_opt("environment", environment)
    cmd += create_opt("threshold", threshold)
    cmd += create_opt("max-depth", max_depth)
    cmd += create_opt("ngrams-length", ngrams_length)
    cmd += create_opt("show_progress", show_progress)
    cmd += create_opt("short-output", short_output)
    cmd += create_opt("reports_extension", reports_extension)
    cmd += create_opt("language", language)
    cmd += create_opt("log-level", log_level)
    cmd += create_opt("workers", workers)
    if mongo_host is not None:
        cmd += ["--mongo-host", str(mongo_host)]
    if mongo_port is not None:
        cmd += ["--mongo-port", str(mongo_port)]
    if mongo_user is not None:
        cmd += ["--mongo-user", str(mongo_user)]
    if mongo_pass is not None:
        cmd += ["--mongo-pass", str(mongo_pass)]

    return run_util(cmd, root="settings")


def show_settings() -> CmdResult:
    return run_util(["show"], root="settings")

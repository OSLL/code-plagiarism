from pathlib import Path
from typing import Any

from typing_extensions import Self

from codeplag.consts import (
    DEFAULT_MODE,
    UTIL_NAME,
    UTIL_VERSION,
)
from codeplag.handlers.check import IgnoreThresholdWorksComparator, WorksComparator
from codeplag.handlers.report import (
    html_report_create,
)
from codeplag.handlers.settings import settings_modify, settings_show
from codeplag.logger import codeplag_logger as logger
from codeplag.types import ExitCode, ReportType


class CodeplagEngine:
    def __init__(self: Self, parsed_args: dict[str, Any]) -> None:
        self.root: str = parsed_args.pop("root")
        self.command: str | None = None
        # TODO: tmp
        if self.root == "settings":
            self.command = parsed_args.pop(self.root)
            if self.command == "show":
                return

            self.parsed_args = parsed_args
        elif self.root == "report":
            self.path: Path = parsed_args.pop("path")
            self.report_type: ReportType = parsed_args.pop("type")
            self.first_root_path = parsed_args.pop("first_root_path", None)
            self.second_root_path = parsed_args.pop("second_root_path", None)
        else:
            self.github_files: list[str] = parsed_args.pop("github_files", [])
            self.github_project_folders: list[str] = parsed_args.pop("github_project_folders", [])
            self.github_user: str = parsed_args.pop("github_user", "") or ""
            ignore_threshold: bool = parsed_args.pop("ignore_threshold")
            if ignore_threshold:
                comparator_class = IgnoreThresholdWorksComparator
            else:
                comparator_class = WorksComparator
            self.comparator: WorksComparator = comparator_class(
                extension=parsed_args.pop("extension"),
                repo_regexp=parsed_args.pop("repo_regexp", None),
                path_regexp=parsed_args.pop("path_regexp", None),
                mode=parsed_args.pop("mode", DEFAULT_MODE),
                set_github_parser=bool(
                    self.github_files or self.github_project_folders or self.github_user
                ),
                all_branches=parsed_args.pop("all_branches", False),
            )

            self.files: list[Path] = parsed_args.pop("files", [])
            self.directories: list[Path] = parsed_args.pop("directories", [])

    def run(self: Self) -> ExitCode:
        logger.info("Starting %s util (%s) ...", UTIL_NAME, UTIL_VERSION)

        if self.root == "settings":
            if self.command == "show":
                settings_show()
            elif self.command == "modify":
                settings_modify(self.parsed_args)
                settings_show()
        elif self.root == "report":
            return html_report_create(
                self.path, self.report_type, self.first_root_path, self.second_root_path
            )
        else:
            return self.comparator.check(
                self.files,
                self.directories,
                self.github_files,
                self.github_project_folders,
                self.github_user,
            )
        return ExitCode.EXIT_SUCCESS

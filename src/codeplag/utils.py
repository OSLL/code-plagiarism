from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from codeplag.consts import (
    DEFAULT_MODE,
)
from codeplag.handlers.check import WorksComparator
from codeplag.handlers.report import (
    html_report_create,
)
from codeplag.handlers.settings import settings_modify, settings_show
from codeplag.logger import codeplag_logger as logger


class CodeplagEngine:
    def __init__(self, parsed_args: Dict[str, Any]) -> None:
        self.root: str = parsed_args.pop("root")
        self.command: Optional[str] = None
        # TODO: tmp
        if self.root == "settings":
            self.command = parsed_args.pop(self.root)
            if self.command == "show":
                return

            self.parsed_args = parsed_args
        elif self.root == "report":
            self.path: Path = parsed_args.pop("path")
        else:
            self.github_files: List[str] = parsed_args.pop("github_files", [])
            self.github_project_folders: List[str] = parsed_args.pop(
                "github_project_folders", []
            )
            self.github_user: str = parsed_args.pop("github_user", "") or ""
            self.comparator = WorksComparator(
                extension=parsed_args.pop("extension"),
                repo_regexp=parsed_args.pop("repo_regexp", None),
                path_regexp=parsed_args.pop("path_regexp", None),
                mode=parsed_args.pop("mode", DEFAULT_MODE),
                set_github_parser=bool(
                    self.github_files or self.github_project_folders or self.github_user
                ),
                all_branches=parsed_args.pop("all_branches", False),
            )

            self.files: List[Path] = parsed_args.pop("files", [])
            self.directories: List[Path] = parsed_args.pop("directories", [])

    def run(self) -> Literal[0, 1]:
        logger.debug("Starting codeplag util ...")

        if self.root == "settings":
            if self.command == "show":
                settings_show()
            elif self.command == "modify":
                settings_modify(self.parsed_args)
                settings_show()
        elif self.root == "report":
            return html_report_create(self.path)
        else:
            self.comparator.check(
                self.files,
                self.directories,
                self.github_files,
                self.github_project_folders,
                self.github_user,
            )
        return 0

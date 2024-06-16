import logging
import os
import re
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, overload

from webparsers.github_parser import GitHubParser
from webparsers.types import WorkInfo

from codeplag.consts import (
    ALL_EXTENSIONS,
    GET_FRAZE,
    UTIL_NAME,
)
from codeplag.types import ASTFeatures, Extension, Extensions


def get_files_path_from_directory(
    directory: Path,
    extensions: Extensions | None = None,
    path_regexp: re.Pattern | None = None,
) -> list[Path]:
    """Recursive gets file paths from provided directory.

    Args:
    ----
        directory: Root directory for getting paths.
        extensions: Available extensions for filtering.
        path_regexp: Provided regular expression for filtering file paths.

    Returns:
    -------
        Paths to all files in the directory and its subdirectories.

    """
    if extensions is None:
        extensions = ALL_EXTENSIONS

    allowed_files = []
    for current_dir, _, filenames in os.walk(directory):
        for filename in filenames:
            allowed = any(ext.search(filename) for ext in extensions)
            if not allowed:
                continue

            path_to_file = Path(current_dir, filename)
            if path_regexp is None:
                allowed_files.append(path_to_file)
                continue

            if path_regexp.search(path_to_file.__str__()):
                allowed_files.append(path_to_file)

    return allowed_files


class AbstractGetter(ABC):
    def __init__(
        self,
        extension: Extension,
        logger: logging.Logger | None = None,
        repo_regexp: str | None = None,
        path_regexp: str | None = None,
    ):
        self.logger = logger if logger is not None else logging.getLogger(UTIL_NAME)
        self.extension: Extension = extension
        self.github_parser: GitHubParser | None = None

        try:
            if repo_regexp is not None:
                self.repo_regexp = re.compile(repo_regexp)
            else:
                self.repo_regexp = repo_regexp
        except re.error as regexp_err:
            self.logger.error(
                "Error while compiling regular expression '%s': '%s'.",
                repo_regexp,
                regexp_err,
            )
            sys.exit(1)
        try:
            if path_regexp is not None:
                self.path_regexp = re.compile(path_regexp)
            else:
                self.path_regexp = path_regexp
        except re.error as regexp_err:
            self.logger.error(
                "Error while compiling regular expression '%s': '%s'.",
                path_regexp,
                regexp_err,
            )
            sys.exit(1)

    def check_github_parser_provided(self) -> None:
        if not isinstance(self.github_parser, GitHubParser):
            raise TypeError(
                "GitHubParser is not provided, or the provided object "
                "is not a GitHubParser instance."
            )

    def set_github_parser(self, github_parser: GitHubParser) -> None:
        if self.github_parser:
            self.github_parser.close_session()
        self.github_parser = github_parser

    @abstractmethod
    def get_from_content(self, work_info: WorkInfo) -> ASTFeatures | None:
        ...

    @abstractmethod
    def get_from_files(self, files: list[Path]) -> list[ASTFeatures]:
        ...

    @overload
    def get_from_dirs(
        self, directories: list[Path], independent: Literal[False] = False
    ) -> list[ASTFeatures]:
        ...

    @overload
    def get_from_dirs(
        self, directories: list[Path], independent: Literal[True]
    ) -> list[list[ASTFeatures]]:
        ...

    @overload
    def get_from_dirs(
        self, directories: list[Path], independent: bool = False
    ) -> list[ASTFeatures] | list[list[ASTFeatures]]:
        ...

    def get_from_dirs(
        self, directories: list[Path], independent: bool = False
    ) -> list[ASTFeatures] | list[list[ASTFeatures]]:
        works = []
        for directory in directories:
            self.logger.debug(f"{GET_FRAZE} {directory}")
            new_works = self.get_works_from_dir(directory)
            if independent:
                works.append(new_works)
            else:
                works.extend(new_works)

        return works

    @abstractmethod
    def get_works_from_dir(self, directory: Path) -> list[ASTFeatures]:
        ...

    def get_from_github_files(self, github_files: list[str]) -> list[ASTFeatures]:
        works: list[ASTFeatures] = []
        if not github_files:
            return works
        self.check_github_parser_provided()
        assert self.github_parser

        self.logger.debug(f"{GET_FRAZE} GitHub urls")
        for github_file in github_files:
            work_info = self.github_parser.get_file_from_url(github_file)
            features = self.get_from_content(work_info)
            if features:
                works.append(features)

        return works

    @overload
    def get_from_github_project_folders(
        self, github_project_folders: list[str], independent: Literal[False] = False
    ) -> list[ASTFeatures]:
        ...

    @overload
    def get_from_github_project_folders(
        self, github_project_folders: list[str], independent: Literal[True]
    ) -> list[list[ASTFeatures]]:
        ...

    @overload
    def get_from_github_project_folders(
        self, github_project_folders: list[str], independent: bool = False
    ) -> list[ASTFeatures] | list[list[ASTFeatures]]:
        ...

    def get_from_github_project_folders(
        self, github_project_folders: list[str], independent: bool = False
    ) -> list[ASTFeatures] | list[list[ASTFeatures]]:
        works = []
        if not github_project_folders:
            return works
        self.check_github_parser_provided()
        assert self.github_parser

        for github_project in github_project_folders:
            nested_works: list[ASTFeatures] = []
            self.logger.debug(f"{GET_FRAZE} {github_project}")
            gh_prj_files = self.github_parser.get_files_generator_from_dir_url(
                github_project, path_regexp=self.path_regexp
            )
            for work_info in gh_prj_files:
                features = self.get_from_content(work_info)
                if features is None:
                    continue

                if independent:
                    nested_works.append(features)
                else:
                    works.append(features)

            if independent:
                works.append(nested_works)

        return works

    @overload
    def get_from_users_repos(
        self, github_user: str, independent: Literal[False] = False
    ) -> list[ASTFeatures]:
        ...

    @overload
    def get_from_users_repos(
        self, github_user: str, independent: Literal[True]
    ) -> list[list[ASTFeatures]]:
        ...

    @overload
    def get_from_users_repos(
        self, github_user: str, independent: bool = False
    ) -> list[ASTFeatures] | list[list[ASTFeatures]]:
        ...

    def get_from_users_repos(
        self, github_user: str, independent: bool = False
    ) -> list[ASTFeatures] | list[list[ASTFeatures]]:
        works = []
        if not github_user:
            return works
        self.check_github_parser_provided()
        assert self.github_parser

        repos = self.github_parser.get_list_of_repos(
            owner=github_user, reg_exp=self.repo_regexp
        )
        for repo in repos:
            nested_works: list[ASTFeatures] = []

            self.logger.debug(f"{GET_FRAZE} {repo.html_url}")
            files = self.github_parser.get_files_generator_from_repo_url(
                repo.html_url, path_regexp=self.path_regexp
            )
            for work_info in files:
                features = self.get_from_content(work_info)
                if features is None:
                    continue

                if independent:
                    nested_works.append(features)
                else:
                    works.append(features)

            if independent:
                works.append(nested_works)

        return works

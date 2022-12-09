import logging
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Literal, Optional, Union, overload

from decouple import Config, RepositoryEnv

from codeplag.consts import (
    ALL_EXTENSIONS,
    GET_FRAZE,
    LOG_PATH,
    SUPPORTED_EXTENSIONS,
    UTIL_NAME,
)
from codeplag.logger import get_logger
from codeplag.types import ASTFeatures, Extension, Extensions
from webparsers.github_parser import GitHubParser


def get_files_path_from_directory(
    directory: Path,
    extensions: Optional[Extensions] = None,
    path_regexp: Optional[re.Pattern] = None
) -> List[Path]:
    """Recursive gets file paths from provided directory.

    Args:
        directory: Root directory for getting paths.
        extensions: Available extensions for filtering.
        path_regexp: Provided regular expression for filtering file paths.

    Returns:
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
        environment: Optional[Path] = None,
        all_branches: bool = False,
        logger: Optional[logging.Logger] = None,
        repo_regexp: Optional[str] = None,
        path_regexp: Optional[str] = None
    ):
        self.logger = logger if logger is not None else logging.getLogger(UTIL_NAME)
        self.extension: Extension = extension
        self.repo_regexp = re.compile(repo_regexp) if repo_regexp is not None else repo_regexp
        self.path_regexp = re.compile(path_regexp) if path_regexp is not None else path_regexp
        self._set_access_token(environment)
        self._set_github_parser(all_branches)

    def _set_access_token(self, env_path: Optional[Path]) -> None:
        # TODO: Set only if defined GitHub options
        if not env_path:
            self.logger.warning(
                "Env file not found or not a file. "
                "Trying to get token from environment."
            )
            self._access_token: str = os.environ.get('ACCESS_TOKEN', '')
        else:
            env_config = Config(RepositoryEnv(env_path))
            self._access_token: str = env_config.get('ACCESS_TOKEN', default='')

        if not self._access_token:
            self.logger.warning('GitHub access token is not defined.')

    def _set_github_parser(self, branch_policy: bool) -> None:
        self.github_parser = GitHubParser(
            file_extensions=SUPPORTED_EXTENSIONS[self.extension],
            check_all=branch_policy,
            access_token=self._access_token,
            logger=get_logger('webparsers', LOG_PATH)
        )

    @abstractmethod
    def get_from_content(self, file_content: str, url_to_file: str) -> Optional[ASTFeatures]:
        ...

    @abstractmethod
    def get_from_files(self, files: List[Path]) -> List[ASTFeatures]:
        ...

    @overload
    def get_from_dirs(
        self, directories: List[Path], independent: Literal[False] = False
    ) -> List[ASTFeatures]:
        ...

    @overload
    def get_from_dirs(
        self, directories: List[Path], independent: Literal[True]
    ) -> List[List[ASTFeatures]]:
        ...

    @overload
    def get_from_dirs(
        self, directories: List[Path], independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        ...

    def get_from_dirs(
        self, directories: List[Path], independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        works = []
        for directory in directories:
            self.logger.info(f'{GET_FRAZE} {directory}')
            new_works = self.get_works_from_dir(directory)
            if independent:
                works.append(new_works)
            else:
                works.extend(new_works)

        return works

    @abstractmethod
    def get_works_from_dir(self, directory: Path) -> List[ASTFeatures]:
        ...

    def get_from_github_files(self, github_files: List[str]) -> List[ASTFeatures]:
        works: List[ASTFeatures] = []
        if not github_files:
            return works

        self.logger.info(f"{GET_FRAZE} GitHub urls")
        for github_file in github_files:
            file_content = self.github_parser.get_file_from_url(github_file)[0]
            features = self.get_from_content(file_content, github_file)
            if features:
                works.append(features)

        return works

    @overload
    def get_from_github_project_folders(
        self, github_project_folders: List[str], independent: Literal[False] = False
    ) -> List[ASTFeatures]:
        ...

    @overload
    def get_from_github_project_folders(
        self, github_project_folders: List[str], independent: Literal[True]
    ) -> List[List[ASTFeatures]]:
        ...

    @overload
    def get_from_github_project_folders(
        self, github_project_folders: List[str], independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        ...

    def get_from_github_project_folders(
        self, github_project_folders: List[str], independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        works = []
        for github_project in github_project_folders:
            nested_works: List[ASTFeatures] = []
            self.logger.info(f'{GET_FRAZE} {github_project}')
            gh_prj_files = self.github_parser.get_files_generator_from_dir_url(
                github_project
            )
            for file_content, url_file in gh_prj_files:
                features = self.get_from_content(file_content, url_file)
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
    ) -> List[ASTFeatures]:
        ...

    @overload
    def get_from_users_repos(
        self, github_user: str, independent: Literal[True]
    ) -> List[List[ASTFeatures]]:
        ...

    @overload
    def get_from_users_repos(
        self, github_user: str, independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        ...

    def get_from_users_repos(
        self, github_user: str, independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        works = []
        if not github_user:
            return works

        repos = self.github_parser.get_list_of_repos(
            owner=github_user,
            reg_exp=self.repo_regexp
        )
        for repo in repos:
            nested_works: List[ASTFeatures] = []

            self.logger.info(f'{GET_FRAZE} {repo.html_url}')
            files = self.github_parser.get_files_generator_from_repo_url(
                repo.html_url
            )
            for file_content, url_file in files:
                features = self.get_from_content(file_content, url_file)
                if features is None:
                    continue

                if independent:
                    nested_works.append(features)
                else:
                    works.append(features)

            if independent:
                works.append(nested_works)

        return works

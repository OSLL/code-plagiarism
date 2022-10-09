import logging
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Literal, Optional, Union, overload

from decouple import Config, RepositoryEnv

from codeplag.consts import GET_FRAZE, LOG_PATH, SUPPORTED_EXTENSIONS, UTIL_NAME
from codeplag.logger import get_logger
from codeplag.types import ASTFeatures, Extensions
from webparsers.github_parser import GitHubParser


def get_files_path_from_directory(
    directory: Path,
    extensions: Optional[Extensions] = None
) -> List[Path]:
    '''
        The function returns paths to all files in the directory
        and its subdirectories which have the extension transmitted
        in arguments
    '''

    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS['default']

    allowed_files = []
    for current_dir, _, files in os.walk(directory):
        for file in files:
            allowed = False
            for extension in extensions:
                if re.search(extension, file):
                    allowed = True

                    break
            if allowed:
                allowed_files.append(Path(current_dir, file))

    return allowed_files


class AbstractGetter(ABC):

    def __init__(
        self,
        extension: str,
        environment: Optional[Path] = None,
        all_branches: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        self.logger = logger if logger is not None else logging.getLogger(UTIL_NAME)
        self.extension = extension
        self._set_access_token(environment)
        self._set_github_parser(all_branches)

    def _set_access_token(self, env_path: Optional[Path]) -> None:
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
            file_extensions=SUPPORTED_EXTENSIONS[
                self.extension
            ],
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
    @abstractmethod
    def get_from_dirs(
        self, directories: List[Path], independent: Literal[False] = False
    ) -> List[ASTFeatures]:
        ...

    @overload
    @abstractmethod
    def get_from_dirs(
        self, directories: List[Path], independent: Literal[True]
    ) -> List[List[ASTFeatures]]:
        ...

    @overload
    @abstractmethod
    def get_from_dirs(
        self, directories: List[Path], independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        ...

    @abstractmethod
    def get_from_dirs(
        self, directories: List[Path], independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
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
        self, github_user: str, regexp: str, independent: Literal[False] = False
    ) -> List[ASTFeatures]:
        ...

    @overload
    def get_from_users_repos(
        self, github_user: str, regexp: str, independent: Literal[True]
    ) -> List[List[ASTFeatures]]:
        ...

    @overload
    def get_from_users_repos(
        self, github_user: str, regexp: str, independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        ...

    def get_from_users_repos(
        self, github_user: str, regexp: str, independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        works = []
        if not github_user:
            return works

        repos = self.github_parser.get_list_of_repos(
            owner=github_user,
            reg_exp=regexp
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

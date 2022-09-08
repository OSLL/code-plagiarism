import logging
import os
import re
from pathlib import Path
from typing import List, Optional, Pattern, Tuple

from decouple import Config, RepositoryEnv

from codeplag.consts import (FILE_DOWNLOAD_PATH, GET_FRAZE, LOG_PATH,
                             SUPPORTED_EXTENSIONS)
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features as get_features_cpp
from codeplag.cplag.util import \
    get_cursor_from_file as get_cursor_from_file_cpp
from codeplag.cplag.util import \
    get_works_from_filepaths as get_works_from_filepaths_cpp
from codeplag.logger import get_logger
from codeplag.pyplag.utils import \
    get_ast_from_content as get_ast_from_content_py
from codeplag.pyplag.utils import \
    get_features_from_ast as get_features_from_ast_py
from codeplag.pyplag.utils import \
    get_works_from_filepaths as get_works_from_filepaths_py
from codeplag.types import ASTFeatures
from webparsers.github_parser import GitHubParser


def get_files_path_from_directory(
    directory: Path,
    extensions: Tuple[Pattern, ...] = None
) -> List[Path]:
    '''
        The function returns paths to all files in the directory
        and its subdirectories which have the extension transmitted
        in arguments
    '''
    if not extensions:
        extensions = SUPPORTED_EXTENSIONS['default']

    allowed_files = []
    for current_dir, _folders, files in os.walk(directory):
        for file in files:
            allowed = False
            for extension in extensions:
                if re.search(extension, file):
                    allowed = True

                    break
            if allowed:
                allowed_files.append(Path(current_dir, file))

    return allowed_files


# TODO: Create abstract class
class FeaturesGetter:

    def __init__(
        self,
        extension: str,
        environment: Optional[str] = None,
        all_branches: bool = False,
        logger: logging.Logger = logging.Logger
    ):
        self.logger = logger
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
            check_policy=branch_policy,
            access_token=self._access_token,
            logger=get_logger('webparsers', LOG_PATH)
        )

    def get_features_from_content(self,
                                  file_content: str,
                                  url_to_file: str) -> ASTFeatures:
        if self.extension == 'py':
            tree = get_ast_from_content_py(file_content, url_to_file)
            features = get_features_from_ast_py(tree, url_to_file)

            return features
        if self.extension == 'cpp':
            with open(FILE_DOWNLOAD_PATH, 'w', encoding='utf-8') as out_file:
                out_file.write(file_content)
            cursor = get_cursor_from_file_cpp(FILE_DOWNLOAD_PATH, COMPILE_ARGS)
            features = get_features_cpp(cursor, FILE_DOWNLOAD_PATH)
            os.remove(FILE_DOWNLOAD_PATH)
            features.filepath = url_to_file

            return features

    def get_features_from_files(self,
                                files: List[Path]) -> List[ASTFeatures]:
        if not files:
            return []

        self.logger.info(f'{GET_FRAZE} files')
        if self.extension == 'py':
            return get_works_from_filepaths_py(files)
        if self.extension == 'cpp':
            return get_works_from_filepaths_cpp(
                files,
                COMPILE_ARGS
            )

    def get_works_from_dirs(
        self, directories: List[Path], independent: bool = False
    ) -> List[ASTFeatures]:
        works: List[ASTFeatures] = []
        for directory in directories:
            self.logger.info(f'{GET_FRAZE} {directory}')
            filepaths = get_files_path_from_directory(
                directory,
                extensions=SUPPORTED_EXTENSIONS[self.extension]
            )
            if self.extension == 'py':
                if independent:
                    works.append(get_works_from_filepaths_py(filepaths))
                else:
                    works.extend(get_works_from_filepaths_py(filepaths))
            if self.extension == 'cpp':
                if independent:
                    works.append(
                        get_works_from_filepaths_cpp(
                            filepaths,
                            COMPILE_ARGS
                        )
                    )
                else:
                    works.extend(
                        get_works_from_filepaths_cpp(
                            filepaths,
                            COMPILE_ARGS
                        )
                    )

        return works

    def get_works_from_github_files(
        self, github_files: List[str]
    ) -> List[ASTFeatures]:
        works: List[ASTFeatures] = []
        if not github_files:
            return works

        self.logger.info(f"{GET_FRAZE} GitHub urls")
        for github_file in github_files:
            file_content = self.github_parser.get_file_from_url(github_file)[0]
            works.append(
                self.get_features_from_content(file_content, github_file)
            )

        return works

    def get_works_from_github_project_folders(
        self, github_project_folders: List[str], independent: bool = False
    ) -> List[ASTFeatures]:
        works: List[ASTFeatures] = []
        for github_project in github_project_folders:
            if independent:
                nested_works: List[ASTFeatures] = []

            self.logger.info(f'{GET_FRAZE} {github_project}')
            gh_prj_files = self.github_parser.get_files_generator_from_dir_url(
                github_project
            )
            for file_content, url_file in gh_prj_files:
                if independent:
                    nested_works.append(
                        self.get_features_from_content(
                            file_content, url_file
                        )
                    )
                else:
                    works.append(
                        self.get_features_from_content(
                            file_content, url_file
                        )
                    )

            if independent:
                works.append(nested_works)

        return works

    def get_works_from_users_repos(
        self, github_user: str, regexp: str, independent: bool = False
    ) -> List[ASTFeatures]:
        works: List[ASTFeatures] = []
        if not github_user:
            return works

        repos = self.github_parser.get_list_of_repos(
            owner=github_user,
            reg_exp=regexp
        )
        for repo in repos:
            if independent:
                nested_works: List[ASTFeatures] = []

            self.logger.info(f'{GET_FRAZE} {repo.html_url}')
            files = self.github_parser.get_files_generator_from_repo_url(
                repo.html_url
            )
            for file_content, url_file in files:
                if independent:
                    nested_works.append(
                        self.get_features_from_content(
                            file_content, url_file
                        )
                    )
                else:
                    works.append(
                        self.get_features_from_content(
                            file_content, url_file
                        )
                    )

            if independent:
                works.append(nested_works)

        return works

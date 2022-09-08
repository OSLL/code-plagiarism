import logging
import os
import re
from pathlib import Path
from typing import List, Pattern, Tuple

from codeplag.consts import FILE_DOWNLOAD_PATH, GET_FRAZE, SUPPORTED_EXTENSIONS
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features as get_features_cpp
from codeplag.cplag.util import \
    get_cursor_from_file as get_cursor_from_file_cpp
from codeplag.cplag.util import \
    get_works_from_filepaths as get_works_from_filepaths_cpp
from codeplag.pyplag.utils import \
    get_ast_from_content as get_ast_from_content_py
from codeplag.pyplag.utils import \
    get_features_from_ast as get_features_from_ast_py
from codeplag.pyplag.utils import \
    get_works_from_filepaths as get_works_from_filepaths_py
from codeplag.types import ASTFeatures


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


class FeaturesGetter:

    def __init__(
        self,
        extension: str,
        logger: logging.Logger = logging.Logger
    ):
        self.logger = logger
        self.extension = extension

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

    def get_works_from_dirs(self, directories: List[Path]) -> List[ASTFeatures]:
        works = []
        for directory in directories:
            self.logger.info(f'{GET_FRAZE} {directory}')
            filepaths = get_files_path_from_directory(
                directory,
                extensions=SUPPORTED_EXTENSIONS[self.extension]
            )
            if self.extension == 'py':
                works.extend(get_works_from_filepaths_py(filepaths))
            if self.extension == 'cpp':
                works.extend(
                    get_works_from_filepaths_cpp(
                        filepaths,
                        COMPILE_ARGS
                    )
                )

        return works

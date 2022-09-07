import os

from codeplag.consts import FILE_DOWNLOAD_PATH
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features as get_features_cpp
from codeplag.cplag.util import \
    get_cursor_from_file as get_cursor_from_file_cpp
from codeplag.pyplag.utils import \
    get_ast_from_content as get_ast_from_content_py
from codeplag.pyplag.utils import \
    get_features_from_ast as get_features_from_ast_py
from codeplag.types import ASTFeatures


def get_work_features(file_content: str,
                      url_to_file: str,
                      extension: str) -> ASTFeatures:
    if extension == 'py':
        tree = get_ast_from_content_py(file_content, url_to_file)
        features = get_features_from_ast_py(tree, url_to_file)

        return features
    if extension == 'cpp':
        with open(FILE_DOWNLOAD_PATH, 'w', encoding='utf-8') as out_file:
            out_file.write(file_content)
        cursor = get_cursor_from_file_cpp(FILE_DOWNLOAD_PATH, COMPILE_ARGS)
        features = get_features_cpp(cursor, FILE_DOWNLOAD_PATH)
        os.remove(FILE_DOWNLOAD_PATH)
        features.filepath = url_to_file

        return features

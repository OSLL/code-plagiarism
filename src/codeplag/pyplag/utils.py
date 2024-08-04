import ast
import logging
from pathlib import Path

from webparsers.types import WorkInfo

from codeplag.consts import GET_FRAZE, SUPPORTED_EXTENSIONS
from codeplag.display import red_bold
from codeplag.getfeatures import (
    AbstractGetter,
    get_files_path_from_directory,
    set_sha256,
)
from codeplag.logger import codeplag_logger as logger
from codeplag.logger import log_err
from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.types import ASTFeatures


def get_ast_from_content(code: str, path: Path | str) -> ast.Module | None:
    tree = None
    try:
        tree = ast.parse(code)
    except TabError as err:
        log_err(
            "-" * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(f"TabError: {err.args[0]}"),
            red_bold(f"In line {str(err.args[1][1])}"),
            "-" * 40,
        )
    except IndentationError as err:
        log_err(
            "-" * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(f"IdentationError: {err.args[0]}"),
            red_bold(f"In line {str(err.args[1][1])}"),
            "-" * 40,
        )
    except SyntaxError as err:
        log_err(
            "-" * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(f"SyntaxError: {err.args[0]}"),
            red_bold(f"In line {str(err.args[1][1])}"),
            red_bold(f"In column {str(err.args[1][2])}"),
            "-" * 40,
        )
    except Exception as err:
        log_err(
            "-" * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(err.__class__.__name__),
        )
        for element in err.args:
            log_err(red_bold(element))
        log_err("-" * 40)

    return tree


def get_ast_from_filename(filepath: Path) -> ast.Module | None:
    """Function return ast which has type ast.Module.

    Args:
    ----
        filename - full path to file with code which will have analyzed

    """
    if not filepath.is_file():
        log_err(f"'{filepath}' is not a file or doesn't exist.")
        return None
    if filepath.stat().st_size == 0:
        logger.debug(f"The file '{filepath}' is empty; there is nothing to get.")
        return None

    tree = None
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            tree = get_ast_from_content(file.read(), filepath)
    except UnicodeDecodeError:
        # TODO: Process this such as in the GitHubParser
        log_err(f"Can't decode file '{filepath}'.")
        return None
    except PermissionError:
        log_err(f"Can't access to the file '{filepath}'.")
        return None

    return tree


@set_sha256
def get_features_from_ast(tree: ast.Module, filepath: Path | str) -> ASTFeatures:
    features = ASTFeatures(filepath)
    walker = ASTWalker(features)
    walker.visit(tree)

    return features


def _get_works_from_filepaths(filenames: list[Path]) -> list[ASTFeatures]:
    if not filenames:
        return []

    works = []
    for filename in filenames:
        tree = get_ast_from_filename(filename)
        if not tree:
            continue

        features = get_features_from_ast(tree, filename)
        works.append(features)

    return works


class PyFeaturesGetter(AbstractGetter):
    def __init__(
        self,
        logger: logging.Logger | None = None,
        repo_regexp: str | None = None,
        path_regexp: str | None = None,
    ):
        super().__init__(
            extension="py",
            logger=logger,
            repo_regexp=repo_regexp,
            path_regexp=path_regexp,
        )

    def get_from_content(self, work_info: WorkInfo) -> ASTFeatures | None:
        tree = get_ast_from_content(work_info.code, work_info.link)
        if tree is not None:
            features = get_features_from_ast(tree, work_info.link)
            features.modify_date = work_info.commit.date
            return features

        self.logger.error(
            "Unsuccessfully attempt to get AST from the file %s.", work_info.link
        )

    def get_from_files(self, files: list[Path]) -> list[ASTFeatures]:
        if not files:
            return []

        self.logger.debug(f"{GET_FRAZE} files")
        return _get_works_from_filepaths(files)

    def get_works_from_dir(self, directory: Path) -> list[ASTFeatures]:
        filepaths = get_files_path_from_directory(
            directory,
            extensions=SUPPORTED_EXTENSIONS[self.extension],
            path_regexp=self.path_regexp,
        )

        return _get_works_from_filepaths(filepaths)

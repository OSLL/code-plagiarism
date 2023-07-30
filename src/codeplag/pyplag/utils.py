import ast
import logging
from pathlib import Path
from typing import List, Optional, Union

from codeplag.consts import GET_FRAZE, LOG_PATH, SUPPORTED_EXTENSIONS
from codeplag.display import eprint, red_bold
from codeplag.getfeatures import AbstractGetter, get_files_path_from_directory
from codeplag.logger import get_logger
from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.types import ASTFeatures
from webparsers.types import WorkInfo

# TODO: Remove from globals
logger = get_logger(__name__, LOG_PATH)


def get_ast_from_content(code: str, path: Union[Path, str]) -> Optional[ast.Module]:
    tree = None

    # TODO: Add logging and check for correct colored output
    try:
        tree = ast.parse(code)
    except TabError as err:
        eprint(
            '-' * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(f'TabError: {err.args[0]}'),
            red_bold(f'In line {str(err.args[1][1])}'),
            '-' * 40,
            sep='\n'
        )
    except IndentationError as err:
        eprint(
            '-' * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(f'IdentationError: {err.args[0]}'),
            red_bold(f'In line {str(err.args[1][1])}'),
            '-' * 40,
            sep='\n'
        )
    except SyntaxError as err:
        eprint(
            '-' * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(f'SyntaxError: {err.args[0]}'),
            red_bold(f'In line {str(err.args[1][1])}'),
            red_bold(f'In column {str(err.args[1][2])}'),
            '-' * 40,
            sep='\n'
        )
    except Exception as err:
        eprint(
            '-' * 40,
            red_bold(f"'{path}' not parsed."),
            red_bold(err.__class__.__name__),
            sep='\n'
        )
        for element in err.args:
            eprint(red_bold(element))
        eprint('-' * 40)

    return tree


def get_ast_from_filename(filepath: Path) -> Optional[ast.Module]:
    '''
        Function return ast which has type ast.Module
        @param filename - full path to file with code which will have
        analyzed
    '''
    if not filepath.is_file():
        logger.error("'%s' is not a file / doesn't exist.", filepath)
        return None

    tree = None
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            tree = get_ast_from_content(file.read(), filepath)
    except UnicodeDecodeError:
        # TODO: Process this such as in the GitHubParser
        logger.error("Can't decode file '%s'.", filepath)
        return None
    except PermissionError:
        logger.error("Can't access to the file '%s'.", filepath)
        return None

    return tree


def get_features_from_ast(tree: ast.Module, filepath: Union[Path, str]) -> ASTFeatures:
    features = ASTFeatures(filepath)
    walker = ASTWalker(features)
    walker.visit(tree)

    return features


def _get_works_from_filepaths(filenames: List[Path]) -> List[ASTFeatures]:
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
        environment: Optional[Path] = None,
        all_branches: bool = False,
        logger: Optional[logging.Logger] = None,
        repo_regexp: str = '',
        path_regexp: str = ''
    ):
        super().__init__(
            extension='py',
            environment=environment,
            all_branches=all_branches,
            logger=logger,
            repo_regexp=repo_regexp,
            path_regexp=path_regexp
        )

    def get_from_content(self, work_info: WorkInfo) -> Optional[ASTFeatures]:
        tree = get_ast_from_content(work_info.code, work_info.link)
        if tree is not None:
            features = get_features_from_ast(tree, work_info.link)
            features.modify_date = work_info.commit.date
            return features

        self.logger.error(
            "Unsuccessfully attempt to get AST from the file %s.", work_info.link
        )

    def get_from_files(self, files: List[Path]) -> List[ASTFeatures]:
        if not files:
            return []

        self.logger.debug(f'{GET_FRAZE} files')
        return _get_works_from_filepaths(files)

    def get_works_from_dir(self, directory: Path) -> List[ASTFeatures]:
        filepaths = get_files_path_from_directory(
            directory,
            extensions=SUPPORTED_EXTENSIONS[self.extension],
            path_regexp=self.path_regexp
        )

        return _get_works_from_filepaths(filepaths)

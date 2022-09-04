import ast
from pathlib import Path
from typing import List, Optional

from codeplag.astfeatures import ASTFeatures
from codeplag.consts import LOG_PATH
from codeplag.display import red_bold
from codeplag.logger import get_logger
from codeplag.pyplag.astwalkers import ASTWalker

# TODO: Remove from globals
logger = get_logger(__name__, LOG_PATH)


def get_ast_from_content(code: str, path: str) -> Optional[ast.Module]:
    tree = None

    # TODO: Add logging and check for correct colored output
    try:
        tree = ast.parse(code)
    except TabError as err:
        print('-' * 40)
        print(red_bold(f"'{path}' not parsed."))
        print(red_bold(f'TabError: {err.args[0]}'))
        print(red_bold(f'In line {str(err.args[1][1])}'))
        print('-' * 40)
    except IndentationError as err:
        print('-' * 40)
        print(red_bold(f"'{path}' not parsed."))
        print(red_bold(f'IdentationError: {err.args[0]}'))
        print(red_bold(f'In line {str(err.args[1][1])}'))
        print('-' * 40)
    except SyntaxError as err:
        print('-' * 40)
        print(red_bold(f"'{path}' not parsed."))
        print(red_bold(f'SyntaxError: {err.args[0]}'))
        print(red_bold(f'In line {str(err.args[1][1])}'))
        print(red_bold(f'In column {str(err.args[1][2])}'))
        print('-' * 40)
    except Exception as err:
        print('-' * 40)
        print(red_bold(f"'{path}' not parsed."))
        print(red_bold(err.__class__.__name__))
        for element in err.args:
            print(red_bold(element))
        print('-' * 40)

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


def get_features_from_ast(tree: ast.Module, filepath: Path) -> ASTFeatures:
    features = ASTFeatures(filepath)
    walker = ASTWalker(features)
    walker.visit(tree)

    return features


def get_works_from_filepaths(filenames: List[Path]) -> List[ASTFeatures]:
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

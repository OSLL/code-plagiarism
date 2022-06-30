import ast
import os

from termcolor import colored

from codeplag.astfeatures import ASTFeatures
from codeplag.consts import LOG_PATH
from codeplag.logger import get_logger
from codeplag.pyplag.astwalkers import ASTWalker

logger = get_logger(__name__, LOG_PATH)


def get_ast_from_content(code, path):
    tree = None

    try:
        tree = ast.parse(code)
    except IndentationError as err:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored('IdentationError: ' + err.args[0], 'red'))
        print(colored('In line ' + str(err.args[1][1]), 'red'))
        print('-' * 40)
    except SyntaxError as err:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored('SyntaxError: ' + err.args[0], 'red'))
        print(colored('In line ' + str(err.args[1][1]), 'red'))
        print(colored('In column ' + str(err.args[1][2]), 'red'))
        print('-' * 40)
    except TabError as err:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored('TabError: ' + err.args[0], 'red'))
        print(colored('In line ' + str(err.args[1][1]), 'red'))
        print('-' * 40)
    except Exception as e:
        print('-' * 40)
        print(colored('Not compiled: ' + path, 'red'))
        print(colored(e.__class__.__name__, 'red'))
        for el in e.args:
            print(colored(el, 'red'))
        print('-' * 40)

    return tree


def get_ast_from_filename(filename):
    '''
        Function return ast which has type ast.Module
        @param filename - full path to file with code which will have
        analyzed
    '''
    if type(filename) is not str:
        logger.error("Filename is not a string type.")
        raise TypeError

    if not os.path.isfile(filename):
        logger.error(f"{filename} is not a file / doesn't exist.")
        return None

    tree = None
    try:
        with open(filename) as f:
            tree = get_ast_from_content(f.read(), filename)
    except UnicodeDecodeError:
        # TODO: Process this such as in the GitHubParser
        logger.error("Can't decode file {}.".format(filename))
        return None
    except PermissionError:
        logger.error(f"Can't access to the file {filename}.")
        return None

    return tree


def get_features_from_ast(tree, filepath=''):
    features = ASTFeatures(filepath)
    walker = ASTWalker(features)
    walker.visit(tree)

    return features


def get_works_from_filepaths(filenames):
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

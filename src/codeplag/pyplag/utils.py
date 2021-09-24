import os
import ast

from termcolor import colored
from codeplag.astfeatures import ASTFeatures
from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.utils import print_compare_res


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
        return TypeError

    if not os.path.isfile(filename):
        print(filename, "Is not a file / doesn't exist")
        return None

    tree = None
    try:
        with open(filename) as f:
            tree = get_ast_from_content(f.read(), filename)
    except PermissionError:
        print("File denied.")
    except FileNotFoundError:
        print("File not found")

    return tree


def get_features_from_ast(tree, filepath=''):
    features = ASTFeatures(filepath)
    walker = ASTWalker(features)
    walker.visit(tree)

    return features


def compare_file_pair(filename1, filename2, threshold):
    '''
        Function compares 2 files
        filename1 - path to the first file (dir/file1.py)
        filename2 - path the second file (dir/file2.py)
    '''
    tree1 = get_ast_from_filename(filename1)
    tree2 = get_ast_from_filename(filename2)

    if tree1 is None:
        return
    if tree2 is None:
        return

    features1 = get_features_from_ast(tree1, filename1)
    features2 = get_features_from_ast(tree2, filename2)
    print_compare_res(features1, features2, threshold)

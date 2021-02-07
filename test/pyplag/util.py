import ast
import os
import warnings

def prepare_trees(file1, file2):
    # warnings.simplefilter("ignore", ResourceWarning)
    directory = 'py/tests/'
    files = list(filter(lambda x: (x.endswith('.py')),
                    os.listdir(directory)))

    if(len(files) < 2):
        raise FileNotFoundError('At least 2 files in /tests folder are needed') 
    else:
        if(file1 == ""):
            filename = directory + 'rw1.py'
        else:
            filename = directory + file1

        if(file2 == ""):
            filename2 = directory + 'rw2.py'
        else:
            filename2 = directory + file2

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename + ' not exists.')

    if not os.path.isfile(filename2):
        raise FileNotFoundError(filename2 + ' not exists.')

    with open(filename) as f:
        tree = ast.parse(f.read())

    with open(filename2) as f:
        tree2 = ast.parse(f.read())

    return (tree, tree2)
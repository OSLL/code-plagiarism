# import numpy as np
import ast

# ast.Add - +
# ast.Mult - *
# ast.Assign - =
IGNORE = ['lineno', 'end_lineno', 'col_offset', 'end_col_offset']


def get_node_value(node):
    if isinstance(node, ast.AST):
        value = str(type(node))[1:-1]
        value = value.split(' ')[1]
        return value
    elif isinstance(node, list):
        return ' '

    return node


def travesrse_ast(tree, depth=0):
    if isinstance(tree, ast.AST):
        # The vars() function returns the __dict__ attribute
        # of the given object.
        for k, v in vars(tree).items():
            if k not in IGNORE:
                print(depth * '-', k, get_node_value(v))
                travesrse_ast(v, depth + 1)

    if isinstance(tree, list):
        for el in tree:
            print(depth * '-', get_node_value(el))
            travesrse_ast(el, depth + 1)


with open('./py/brut_forse.py') as f:
    tree = ast.parse(f.read())
    travesrse_ast(tree)

# my_tree = ast.parse("import numpy as np\nx = 3 + 4*x\nprint(10)")
# print(ast.dump(my_tree))
# print()
# travesrse_ast(my_tree)

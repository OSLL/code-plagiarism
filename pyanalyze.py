# import numpy as np
import ast

IGNORE = ['lineno', 'end_lineno', 'col_offset',
          'end_col_offset', 'kind', 'ctx']
IGNORE_NODES = ['Import']
OPERATORS = ['UAdd', 'USub', 'Not', 'Invert', 'Add', 'Sub',
             'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift',
             'RShift', 'BitOr', 'BitXor', 'BitAnd', 'MatMult',
             'And', 'Or', 'AugAssign', 'Assign', 'Eq', 'NotEq',
             'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn']


class OperatorsCounter(ast.NodeVisitor):
    def __init__(self):
        self.operators = {}

    def generic_visit(self, node):
        type_name = type(node).__name__
        if type_name in OPERATORS:
            if type_name not in self.operators.keys():
                self.operators[type_name] = 1
            else:
                self.operators[type_name] += 1
        ast.NodeVisitor.generic_visit(self, node)


class Visitor(ast.NodeVisitor):
    depth = 0

    def generic_visit(self, node):
        print('-' * self.depth + type(node).__name__)
        self.depth += 1
        ast.NodeVisitor.generic_visit(self, node)
        self.depth -= 1


def op_metric(res1, res2):
    percent_of_same = [0, 0]
    for key in res1.keys():
        if key not in res2.keys():
            percent_of_same[1] += res1[key]
            continue
        percent_of_same[0] += min(res1[key],
                                  res2[key])
        percent_of_same[1] += max(res1[key],
                                  res2[key])
    for key in res2.keys():
        if key not in res1.keys():
            percent_of_same[1] += res2[key]
            continue

    if percent_of_same[1] == 0:
        return 0.0

    return percent_of_same[0] / percent_of_same[1]


def get_node_value(node):
    if isinstance(node, ast.AST):
        value = str(type(node))[1:-1]
        value = value.split(' ')[1]
        return value
    elif isinstance(node, list):
        return ' '

    return node


def allowed_class(node):
    if isinstance(node, ast.Import):
        return False

    return True


def travesrse_ast(tree, depth=0):
    if isinstance(tree, ast.AST):
        # The vars() function returns the __dict__ attribute
        # of the given object.
        for k, v in vars(tree).items():
            if k not in IGNORE and allowed_class(v):
                print(depth * '-', k, get_node_value(v))
                travesrse_ast(v, depth + 1)

    if isinstance(tree, list):
        for el in tree:
            if allowed_class(el):
                print(depth * '-', get_node_value(el))
                travesrse_ast(el, depth + 1)


if __name__ == '__main__':
    tmp1 = OperatorsCounter()
    tmp2 = OperatorsCounter()

    with open('./py/brut_forse.py') as f:
        tree = ast.parse(f.read())
        # travesrse_ast(tree)
        # print(ast.dump(tree))
        # temp = Visitor()
        # temp.visit(tree)

        tmp1.visit(tree)

    with open('./py/Threads.py') as f2:
        tree2 = ast.parse(f2.read())
        tmp2.visit(tree2)

    print(op_metric(tmp1.operators, tmp2.operators))

# my_tree = ast.parse("import numpy as np\nx = 3 + 4*x\nprint(10)")
# print(ast.dump(my_tree))
# print()
# travesrse_ast(my_tree)

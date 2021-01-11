import numpy as np
import pandas as pd
import ast
import os
import sys

from time import perf_counter

IGNORE = ['lineno', 'end_lineno', 'col_offset',
          'end_col_offset', 'kind', 'ctx']
IGNORE_NODES = ['Import', 'ImportFrom']
OPERATORS = ['UAdd', 'USub', 'Not', 'Invert', 'Add', 'Sub',
             'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift',
             'RShift', 'BitOr', 'BitXor', 'BitAnd', 'MatMult',
             'And', 'Or', 'AugAssign', 'Assign', 'Eq', 'NotEq',
             'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn']
KEYWORDS = ['Return', 'Yield', 'YieldFrom', 'Global', 'Lambda',
            'FunctionDef', 'Continue', 'Try', 'With', 'IfExp', 'For',
            'While', 'Break', 'Pass', 'Raise', 'Assert', 'Delete', 'If']
LITERALS = ['Constant', 'FormattedValue', 'JoinedStr', 'List',
            'Tuple', 'Set', 'Dict',
            # If use python version less than 3.8
            'Num', 'Str', 'Bytes', 'NameConstant', 'Ellipsis']


class OpKwCounter(ast.NodeVisitor):
    def __init__(self):
        self.seq_ops = []
        self.operators = {}
        self.keywords = {}
        self.literals = {}

    def generic_visit(self, node):
        '''
            Function for traverse, counting operators, keywords, literals
            and save sequence of operators
            @param node - current node
        '''
        type_name = type(node).__name__
        if type_name in OPERATORS:
            if type_name not in self.operators.keys():
                self.operators[type_name] = 1
            else:
                self.operators[type_name] += 1
            self.seq_ops.append(type_name)
        elif type_name in KEYWORDS:
            if type_name not in self.keywords.keys():
                self.keywords[type_name] = 1
            else:
                self.keywords[type_name] += 1
        elif type_name in LITERALS:
            if type_name not in self.literals.keys():
                self.literals[type_name] = 1
            else:
                self.literals[type_name] += 1
        ast.NodeVisitor.generic_visit(self, node)


class Visitor(ast.NodeVisitor):
    def __init__(self, write_tree=False):
        self.depth = 0
        self.count_of_nodes = 0
        self.write_tree = write_tree

    def generic_visit(self, node):
        '''
            Function for traverse tree and print it in console
            @param node - current node
        '''
        type_node = (type(node).__name__)
        if type_node not in IGNORE_NODES:
            if self.depth != 0:
                self.count_of_nodes += 1
            if self.write_tree:
                print('-' * self.depth + type(node).__name__,
                      self.count_of_nodes)
            self.depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1


class NodeGetter(ast.NodeVisitor):
    def __init__(self):
        self.depth = 0
        self.nodes = []

    def visit(self, node):
        '''
            Function for visiting node's children
            @param node - current node
        '''
        if self.depth > 1:
            return
        self.generic_visit(node)

    def generic_visit(self, node):
        '''
            Function for traverse and print in console names of all
            node's children
            @param node - current node
        '''
        type_node = (type(node).__name__)
        if type_node not in IGNORE_NODES:
            if self.depth == 1:
                self.nodes.append(node)

            self.depth += 1
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1


def get_AST(filename):
    '''
        Function return ast which has type ast.Module
        @param filename - full path to file with code which will have
        analyzed
    '''
    if not os.path.isfile(filename):
        print(filename, "Is not a file / doesn't exist")
        return 0

    tree = None
    with open(filename) as f:
        tree = ast.parse(f.read())

    return tree


def nodes_metric(res1, res2):
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


def get_nodes(tree):
    traverser = NodeGetter()
    traverser.visit(tree)
    return traverser.nodes


def get_count_of_nodes(tree):
    traverser = Visitor()
    traverser.visit(tree)
    return traverser.count_of_nodes


def find_max_index(array, len1, len2):
    '''
        Function for finding index of max element in matrix
        @param array - matrix of compliance
        @param len1 - number of nodes in children1
        @param len2 - number of nodes in children2
    '''
    maximum = 0
    index = (0, 0)
    for i in range(len1):
        for j in range(len2):
            if array[i][j][1] == 0:
                continue
            value = array[i][j][0] / array[i][j][1]
            if value > maximum:
                maximum = value
                index = (i, j)

    return index


def getn_count_nodes(len_min, len_max, indexes, axis, children):
    '''
        Function return count of not accounted nodes
        @param len_min - length of less node
        @param len_max - length of longer node
        @param indexes - indexes of metrics taken into account list of tuples
        @param axis - if 0 then iteration on row
        if 1 then iteration on column
        @param children - list of nodes of type clang.cindex.Cursor object
    '''
    add = [indexes[i][axis] for i in range(len_min)]

    count = 0
    for i in range(len_max):
        if i not in add:
            count += get_count_of_nodes(children[i]) + 1

    return count


def calculate_metric(children1, children2, len1, len2, array):
    same_struct_metric = [0, 0]
    indexes = []
    for i in range(min(len1, len2)):
        ind = find_max_index(array, len1, len2)
        indexes.append(ind)
        same_struct_metric[0] += array[ind][0]
        same_struct_metric[1] += array[ind][1]
        # same_struct_metric = [same_struct_metric[0] +
        #                       array[ind][0],
        #                       same_struct_metric[1] +
        #                       array[ind][1]]
        for i in range(len2):
            array[ind[0]][i] = [0, 0]
        for j in range(len1):
            array[j][ind[1]] = [0, 0]

    same_struct_metric[0] += 1
    same_struct_metric[1] += 1
    # same_struct_metric = [same_struct_metric[0] + 1,
    #                       same_struct_metric[1] + 1]

    not_count = 0
    if len1 > len2:
        not_count = getn_count_nodes(len2, len1, indexes, 0, children1)
    elif len2 > len1:
        not_count = getn_count_nodes(len1, len2, indexes, 1, children2)

    same_struct_metric[1] += not_count
    # same_struct_metric = [same_struct_metric[0],
    #                       same_struct_metric[1] + not_count]

    return same_struct_metric


def struct_compare(tree1, tree2, output=False):
    parsed_nodes1 = get_nodes(tree1)
    parsed_nodes2 = get_nodes(tree2)
    len1 = len(parsed_nodes1)
    len2 = len(parsed_nodes2)

    if (len1 == 0 and len2 == 0):
        return [1, 1]
    elif (len1 == 0):
        return [1, (get_count_of_nodes(tree2) + 1)]
    elif (len2 == 0):
        return [1, (get_count_of_nodes(tree1) + 1)]

    array = np.zeros((len1, len2), dtype=object)
    if output:
        indexes = []
        columns = []

    for i in range(len1):
        if output:
            indexes.append(type(parsed_nodes1[i]).__name__)
        for j in range(len2):
            array[i][j] = struct_compare(parsed_nodes1[i],
                                         parsed_nodes2[j])

    if output:
        for j in range(len2):
            columns.append(type(parsed_nodes2[j]).__name__)
        table = pd.DataFrame(array, index=indexes, columns=columns)
        print()
        print(table)

    same_struct_metric = calculate_metric(parsed_nodes1,
                                          parsed_nodes2,
                                          len1,
                                          len2,
                                          array)

    if output:
        print()
        print('Structure is same by {:.2%}'.format(same_struct_metric[0] /
                                                   same_struct_metric[1]))
    return same_struct_metric


def op_shift_metric(ops1, ops2):
    x = []
    y = []

    count_el_f = len(ops1)
    count_el_s = len(ops2)
    if count_el_f > count_el_s:
        tmp = ops1
        ops1 = ops2
        ops2 = tmp
        count_el_f = len(ops1)
        count_el_s = len(ops2)
        del tmp

    shift = 0
    while shift < count_el_s:
        counter = 0
        first_ind = 0
        second_ind = shift
        while first_ind < count_el_f and second_ind < count_el_s:
            if ops1[first_ind] == ops2[second_ind]:
                counter += 1
            first_ind += 1
            second_ind += 1
        x.append(shift)
        count_all = count_el_f + count_el_s - counter
        if count_all == 0:
            y.append(0)
        else:
            y.append(counter / count_all)
        shift += 1

    max_shift = 0
    for index in range(1, len(y)):
        if y[index] > y[max_shift]:
            max_shift = index

    return max_shift, y[max_shift]


if __name__ == '__main__':
    directory = 'py/'
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    if not os.path.exists(directory):
        print('Directory isn\'t exist')
        exit()

    files = os.listdir(directory)
    files = list(filter(lambda x: (x.endswith('.py')), files))

    count_files = len(files)
    # matrix_compliance = np.zeros((count_files, count_files))
    # indexes_py = []
    # columns_py = []
    start_eval = perf_counter()
    for row in range(count_files):
        if directory[-1] != '/':
            directory += '/'
        filename = directory + files[row]
        # indexes_py.append(filename.split('/')[-1])
        for col in range(count_files):
            filename2 = directory + files[col]
            # if row == 1:
            #     columns_cpp.append(filename2.split('/')[-1])
            if row == col:
                # matrix_compliance[row - 1][col - 1] = 1.0
                continue
            if row > col:
                continue

            tree1 = get_AST(filename)
            tree2 = get_AST(filename2)
            res = struct_compare(tree1, tree2)
            struct_res = round(res[0] / res[1], 3)
            counter1 = OpKwCounter()
            counter2 = OpKwCounter()
            counter1.visit(tree1)
            counter2.visit(tree2)
            operators_res = nodes_metric(counter1.operators,
                                         counter2.operators)
            keywords_res = nodes_metric(counter1.keywords, counter2.keywords)
            literals_res = nodes_metric(counter1.literals, counter2.literals)
            b_sh, sh_res = op_shift_metric(counter1.seq_ops,
                                           counter2.seq_ops)
            # keywords_res = get_kw_freq_percent(ck)
            # matrix_compliance[row - 1][col - 1] = struct_res
            # matrix_compliance[col - 1][row - 1] = struct_res

            summ = (struct_res * 1.2 + operators_res * 0.8 + keywords_res * 0.8
                    + literals_res * 0.5 + sh_res * 0.3)

            # max * 0.75
            if summ > 2.7:
                print()
                print('+' * 40)
                print('May be similar:', filename.split('/')[-1],
                      filename2.split('/')[-1])
                struct_compare(tree1, tree2, True)
                text = 'Operators match percentage:'
                print(text, '{:.2%}'.format(operators_res))
                text = 'Keywords match percentage:'
                print(text, '{:.2%}'.format(keywords_res))
                text = 'Literals match percentage:'
                print(text, '{:.2%}'.format(literals_res))

                print('---')
                print('Op shift metric.')
                print('Best op shift:', b_sh)
                print('Persent same: {:.2%}'.format(sh_res))
                print('---')
                print('+' * 40)

    print()
    print('Time for all {:.2f}'.format(perf_counter() - start_eval))
    # same_cpp = pd.DataFrame(matrix_compliance, index=indexes_cpp,
    #                         columns=columns_cpp)
    # same_cpp.to_csv('same_structure.csv', sep=';')

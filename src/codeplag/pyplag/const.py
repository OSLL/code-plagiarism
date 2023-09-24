# fmt: off
IGNORE = ('lineno', 'end_lineno', 'col_offset',
          'end_col_offset', 'kind', 'ctx')
IGNORE_NODES = ('Import', 'ImportFrom')
OPERATORS = ('UAdd', 'USub', 'Not', 'Invert', 'Add', 'Sub',
             'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift',
             'RShift', 'BitOr', 'BitXor', 'BitAnd', 'MatMult',
             'And', 'Or', 'Assign', 'AnnAssign', 'AugAssign', 'Eq', 'NotEq',
             'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn')
KEYWORDS = ('Return', 'Yield', 'YieldFrom', 'Global', 'Lambda',
            'FunctionDef', 'Continue', 'Try', 'With', 'IfExp', 'For',
            'While', 'Break', 'Pass', 'Raise', 'Assert', 'Delete', 'If')
LITERALS = ('Constant', 'FormattedValue', 'JoinedStr', 'List',
            'Tuple', 'Set', 'Dict',
            # If use python version less than 3.8
            'Num', 'Str', 'Bytes', 'NameConstant', 'Ellipsis')
NAMES = ('name', 'arg', 'id')


# 0 - UnaryOp
# 1 - BinOp
# 2 - BoolOp
# 3 - Compare
# 4 - Assign
# 5 - Loop
# 6 - Condition
# 11 - Handling errors
# 12 - Imports
# 13 - Loop's statements
# 26 - Containers
TO_TOKEN = {'UAdd': 0, 'USub': 0, 'Not': 0, 'Invert': 0,
            'Add': 1, 'Sub': 1, 'Mult': 1, 'Div': 1, 'FloorDiv': 1,
            'Mod': 1, 'Pow': 1, 'LShift': 1, 'RShift': 1,
            'BitOr': 1, 'BitXor': 1, 'BitAnd': 1, 'MatMult': 1,
            'And': 2, 'Or': 2,
            'Eq': 3, 'NotEq': 3, 'Lt': 3,
            'LtE': 3, 'Gt': 3, 'GtE': 3, 'Is': 3, 'IsNot': 3,
            'In': 3, 'NotIn': 3,
            'Assign': 4, 'AnnAssign': 4, 'AugAssign': 4,
            'For': 5, 'AsyncFor': 5, 'While': 5,
            'If': 6, 'IfExp': 6,
            'FunctionDef': 7, 'AsyncFunctionDef': 7, 'ClassDef': 8,
            'Return': 9, 'Yield': 10, 'YieldFrom': 10,
            'Raise': 11, 'Try': 11, 'Assert': 11,
            'Import': 12, 'ImportFrom': 12,
            'Pass': 13, 'Break': 13, 'Continue': 13,
            'Delete': 14, 'With': 15, 'AsyncWith': 15,
            'Global': 16, 'Nonlocal': 17, 'Exp': 18,
            'Lambda': 19, 'alias': 20, 'ExceptHandler': 21,
            'withitem': 22, 'arguments': 23, 'arg': 24,
            'Await': 25,
            'Tuple': 26, 'Set': 26, 'Dict': 26, 'List': 26,
            'Constant': 27, 'FormattedValue': 28, 'JoinedStr': 29, 'Num': 30,
            'Str': 31, 'Bytes': 32, 'NameConstant': 33, 'Ellipsis': 34,
            'Name': 35
            }

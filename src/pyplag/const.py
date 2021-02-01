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
NAMES = ['name', 'arg', 'id']

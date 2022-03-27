import ccsyspath

from clang.cindex import CursorKind


def get_compile_args():
    syspath = ccsyspath.system_include_paths('clang++')
    incargs = [b'-I' + inc for inc in syspath]

    return ['-x', 'c++', '--std=c++11'] + incargs


COMPILE_ARGS = get_compile_args()
IGNORE = [
    CursorKind.PREPROCESSING_DIRECTIVE,
    # CursorKind.MACRO_DEFINITION,
    CursorKind.MACRO_INSTANTIATION,
    CursorKind.INCLUSION_DIRECTIVE,
    CursorKind.USING_DIRECTIVE,
    CursorKind.NAMESPACE
]
OPERATORS = (
    '+', '-', '*', '/', '%',               # Arithmetic Operators
    '+=', '-=', '*=', '/=', '%=', '=',     # Assignment Operators
    '!', '&&', '||',                       # Logical Operators
    '!=', '==', '<=', '>=', '<', '>',      # Relational Operators
    '^', '&', '|', '<<', '>>', '~'         # Bitwise Operators
)

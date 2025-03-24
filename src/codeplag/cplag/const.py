import ccsyspath
from clang.cindex import CursorKind


def get_compile_args() -> list[str]:
    syspath = ccsyspath.system_include_paths("clang++")
    incargs = [b"-I" + inc for inc in syspath]

    return ["-x", "c++", "--std=c++11"] + incargs


COMPILE_ARGS = get_compile_args()
IGNORE = [
    CursorKind.PREPROCESSING_DIRECTIVE,  # type: ignore
    # CursorKind.MACRO_DEFINITION,
    CursorKind.MACRO_INSTANTIATION,  # type: ignore
    CursorKind.INCLUSION_DIRECTIVE,  # type: ignore
    CursorKind.USING_DIRECTIVE,  # type: ignore
    CursorKind.NAMESPACE,  # type: ignore
]
# fmt: off
OPERATORS = (
    '+', '-', '*', '/', '%',               # Arithmetic Operators
    '+=', '-=', '*=', '/=', '%=', '=',     # Assignment Operators
    '!', '&&', '||',                       # Logical Operators
    '!=', '==', '<=', '>=', '<', '>',      # Relational Operators
    '^', '&', '|', '<<', '>>', '~'         # Bitwise Operators
)
# fmt: on

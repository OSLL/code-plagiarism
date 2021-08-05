from clang.cindex import CursorKind

IGNORE = [CursorKind.PREPROCESSING_DIRECTIVE,
          # CursorKind.MACRO_DEFINITION,
          CursorKind.MACRO_INSTANTIATION,
          CursorKind.INCLUSION_DIRECTIVE,
          CursorKind.USING_DIRECTIVE,
          CursorKind.NAMESPACE]

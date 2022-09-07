from pathlib import Path
from typing import List, Optional

from clang.cindex import Cursor, Index, TranslationUnit

from codeplag.cplag.tree import get_features
from codeplag.types import ASTFeatures


def get_cursor_from_file(filepath: Path,
                         args: Optional[List[str]] = None) -> Optional[Cursor]:
    '''
        Returns clang.cindex.Cursor object or None if file is undefined
        @param filename - full path to source file
        @param args - list of arguments for clang.cindex.Index.parse() method
    '''

    if args is None:
        args = []

    if not filepath.is_file():
        print(filepath, "Is not a file / doesn't exist")
        return

    index = Index.create()
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    file_obj = index.parse(filepath, args=args, options=options) or 0

    return file_obj.cursor


def get_works_from_filepaths(
    filepaths: List[Path],
    compile_args: List[str]
) -> List[ASTFeatures]:
    if not filepaths:
        return []

    works = []
    for filepath in filepaths:
        cursor = get_cursor_from_file(filepath, compile_args)
        features = get_features(cursor, filepath)
        works.append(features)

    return works

import os
from typing import List, Optional

from clang.cindex import Cursor, Index, TranslationUnit

from codeplag.astfeatures import ASTFeatures
from codeplag.cplag.tree import get_features


def get_cursor_from_file(filename: str,
                         args: Optional[List[str]] = None) -> Optional[Cursor]:
    '''
        Returns clang.cindex.Cursor object or None if file is undefined
        @param filename - full path to source file
        @param args - list of arguments for clang.cindex.Index.parse() method
    '''

    if args is None:
        args = []

    if not os.path.isfile(filename):
        print(filename, "Is not a file / doesn't exist")
        return

    index = Index.create()
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    file_obj = index.parse(filename, args=args, options=options) or 0

    return file_obj.cursor


def get_works_from_filepaths(
    filenames: str,
    compile_args: List[str]
) -> List[ASTFeatures]:
    if not filenames:
        return []

    works = []
    for filename in filenames:
        cursor = get_cursor_from_file(filename, compile_args)
        features = get_features(cursor, filename)
        works.append(features)

    return works

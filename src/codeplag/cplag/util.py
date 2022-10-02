import os
from pathlib import Path
from typing import List, Optional, Union

from clang.cindex import Cursor, Index, TranslationUnit

from codeplag.consts import FILE_DOWNLOAD_PATH, GET_FRAZE, SUPPORTED_EXTENSIONS
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features
from codeplag.getfeatures import AbstractGetter, get_files_path_from_directory
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


class CFeaturesGetter(AbstractGetter):

    def get_from_content(self, file_content: str, url_to_file: str) -> Optional[ASTFeatures]:
        with open(FILE_DOWNLOAD_PATH, 'w', encoding='utf-8') as out_file:
            out_file.write(file_content)
        cursor = get_cursor_from_file(FILE_DOWNLOAD_PATH, COMPILE_ARGS)
        if not cursor:
            self.logger.warning(
                "Unsuccessfully attempt to get AST from the file %s.", url_to_file
            )
            return

        # hook for correct filtering info while parsing source code
        features = get_features(cursor, FILE_DOWNLOAD_PATH)
        os.remove(FILE_DOWNLOAD_PATH)
        features.filepath = url_to_file

        return features

    def get_from_files(self, files: List[Path]) -> List[ASTFeatures]:
        if not files:
            return []

        self.logger.info(f'{GET_FRAZE} files')
        return get_works_from_filepaths(files, COMPILE_ARGS)

    def get_from_dirs(
        self, directories: List[Path], independent: bool = False
    ) -> Union[List[ASTFeatures], List[List[ASTFeatures]]]:
        works = []
        for directory in directories:
            self.logger.info(f'{GET_FRAZE} {directory}')
            filepaths = get_files_path_from_directory(
                directory,
                extensions=SUPPORTED_EXTENSIONS[self.extension]
            )
            if independent:
                works.append(
                    get_works_from_filepaths(
                        filepaths,
                        COMPILE_ARGS
                    )
                )
            else:
                works.extend(
                    get_works_from_filepaths(
                        filepaths,
                        COMPILE_ARGS
                    )
                )

        return works

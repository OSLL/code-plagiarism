import logging
import os
from pathlib import Path
from typing import List, Optional

from clang.cindex import Cursor, Index, TranslationUnit
from webparsers.types import WorkInfo

from codeplag.consts import FILE_DOWNLOAD_PATH, GET_FRAZE, SUPPORTED_EXTENSIONS
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features
from codeplag.display import eprint
from codeplag.getfeatures import AbstractGetter, get_files_path_from_directory
from codeplag.types import ASTFeatures


def get_cursor_from_file(
    filepath: Path, args: Optional[List[str]] = None
) -> Optional[Cursor]:
    """Returns clang.cindex.Cursor object or None if file is undefined.

    Args:
        filename - full path to source file
        args - list of arguments for clang.cindex.Index.parse() method
    """

    if args is None:
        args = COMPILE_ARGS

    if not filepath.is_file():
        # TODO: print to log
        eprint(filepath, "Is not a file / does not exist")
        return

    index = Index.create()
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    source_code = filepath.read_text(encoding="utf-8", errors="ignore")
    file_obj = index.parse(
        path=None,
        unsaved_files=[(filepath.name, source_code)],
        args=args + [filepath.name],
        options=options,
    )

    return file_obj.cursor


def _get_works_from_filepaths(
    filepaths: List[Path], compile_args: List[str]
) -> List[ASTFeatures]:
    if not filepaths:
        return []

    works = []
    for filepath in filepaths:
        cursor = get_cursor_from_file(filepath, compile_args)
        if cursor is None:
            # TODO: print to log
            eprint(f"{filepath} does not parsed")
            continue

        features = get_features(cursor, filepath)
        works.append(features)

    return works


class CFeaturesGetter(AbstractGetter):
    def __init__(
        self,
        environment: Optional[Path] = None,
        all_branches: bool = False,
        logger: Optional[logging.Logger] = None,
        repo_regexp: str = "",
        path_regexp: str = "",
    ):
        super().__init__(
            extension="cpp",
            environment=environment,
            all_branches=all_branches,
            logger=logger,
            repo_regexp=repo_regexp,
            path_regexp=path_regexp,
        )

    def get_from_content(self, work_info: WorkInfo) -> Optional[ASTFeatures]:
        with open(FILE_DOWNLOAD_PATH, "w", encoding="utf-8") as out_file:
            out_file.write(work_info.code)
        cursor = get_cursor_from_file(FILE_DOWNLOAD_PATH, COMPILE_ARGS)
        if cursor is None:
            self.logger.error(
                "Unsuccessfully attempt to get AST from the file %s.", work_info.link
            )
            return

        # hook for correct filtering info while parsing source code
        features = get_features(cursor, FILE_DOWNLOAD_PATH)
        os.remove(FILE_DOWNLOAD_PATH)
        features.filepath = work_info.link
        features.modify_date = work_info.commit.date

        return features

    def get_from_files(self, files: List[Path]) -> List[ASTFeatures]:
        if not files:
            return []

        self.logger.debug(f"{GET_FRAZE} files")
        return _get_works_from_filepaths(files, COMPILE_ARGS)

    def get_works_from_dir(self, directory: Path) -> List[ASTFeatures]:
        filepaths = get_files_path_from_directory(
            directory,
            extensions=SUPPORTED_EXTENSIONS[self.extension],
            path_regexp=self.path_regexp,
        )

        return _get_works_from_filepaths(filepaths, COMPILE_ARGS)

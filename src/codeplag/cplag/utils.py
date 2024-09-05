import logging
import os
from pathlib import Path
from typing import Final

from clang.cindex import Config, Cursor, Index, TranslationUnit
from webparsers.types import WorkInfo

from codeplag.consts import FILE_DOWNLOAD_PATH, GET_FRAZE, SUPPORTED_EXTENSIONS
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features
from codeplag.getfeatures import AbstractGetter, get_files_path_from_directory
from codeplag.logger import log_err
from codeplag.types import ASTFeatures

# FIXME: Dirty hook for finding libclang so file
LIBCLANG_SO_FILE_PATH: Final[Path] = Path("/usr/lib/llvm-14/lib/libclang-14.so.1")
Config.set_library_file(LIBCLANG_SO_FILE_PATH)


def get_cursor_from_file(filepath: Path, args: list[str] | None = None) -> Cursor | None:
    """Returns clang.cindex.Cursor object or None if file is undefined.

    Args:
    ----
        filepath (Path): full path to source file.
        args (list[str]): list of arguments for clang.cindex.Index.parse() method.

    """
    if args is None:
        args = COMPILE_ARGS

    if not filepath.is_file():
        log_err(f"'{filepath}' is not a file or does not exist.")
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


def _get_works_from_filepaths(filepaths: list[Path], compile_args: list[str]) -> list[ASTFeatures]:
    if not filepaths:
        return []

    works = []
    for filepath in filepaths:
        cursor = get_cursor_from_file(filepath, compile_args)
        if cursor is None:
            log_err(f"'{filepath}' does not parsed.")
            continue

        features = get_features(cursor, filepath)
        works.append(features)

    return works


class CFeaturesGetter(AbstractGetter):
    def __init__(
        self,
        logger: logging.Logger | None = None,
        repo_regexp: str | None = None,
        path_regexp: str | None = None,
    ):
        super().__init__(
            extension="cpp",
            logger=logger,
            repo_regexp=repo_regexp,
            path_regexp=path_regexp,
        )

    def get_from_content(self, work_info: WorkInfo) -> ASTFeatures | None:
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

    def get_from_files(self, files: list[Path]) -> list[ASTFeatures]:
        if not files:
            return []

        self.logger.debug(f"{GET_FRAZE} files")
        return _get_works_from_filepaths(files, COMPILE_ARGS)

    def get_works_from_dir(self, directory: Path) -> list[ASTFeatures]:
        filepaths = get_files_path_from_directory(
            directory,
            extensions=SUPPORTED_EXTENSIONS[self.extension],
            path_regexp=self.path_regexp,
        )

        return _get_works_from_filepaths(filepaths, COMPILE_ARGS)

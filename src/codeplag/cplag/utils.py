import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final

from clang.cindex import Config, Cursor, Index, TranslationUnit
from typing_extensions import Self

from codeplag.consts import GET_FRAZE, SUPPORTED_EXTENSIONS
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features
from codeplag.featurescache import AbstractFeaturesCache
from codeplag.getfeatures import AbstractGetter, get_files_path_from_directory
from codeplag.logger import log_err
from codeplag.types import ASTFeatures
from webparsers.types import WorkInfo

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


def _get_works_from_filepaths(
    filepaths: list[Path], features_cache: AbstractFeaturesCache | None, compile_args: list[str]
) -> list[ASTFeatures]:
    if not filepaths:
        return []

    works = []
    for filepath in filepaths:
        features = None

        if features_cache is not None:
            features = features_cache.get_features_from_filepath(filepath)

        if features is None:
            cursor = get_cursor_from_file(filepath, compile_args)
            if cursor is None:
                log_err(f"'{filepath}' does not parsed.")
                continue

            features = get_features(cursor, filepath)
            if features_cache is not None:
                features_cache.save_features(features)
        works.append(features)

    return works


class CFeaturesGetter(AbstractGetter):
    def __init__(
        self: Self,
        logger: logging.Logger | None = None,
        repo_regexp: str | None = None,
        path_regexp: str | None = None,
        features_cache: AbstractFeaturesCache | None = None,
    ) -> None:
        super().__init__(
            extension="cpp",
            logger=logger,
            repo_regexp=repo_regexp,
            path_regexp=path_regexp,
            features_cache=features_cache,
        )

    def get_from_content(self: Self, work_info: WorkInfo) -> ASTFeatures | None:
        features = None

        if self.features_cache is not None:
            features = self.features_cache.get_features_from_work_info(work_info)

        if features is None:
            with NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".out", delete=False) as tf:
                tf.write(work_info.code)
                tf_path = Path(tf.name)
            cursor = get_cursor_from_file(tf_path, COMPILE_ARGS)
            if cursor is None:
                self.logger.error(
                    "Unsuccessfully attempt to get AST from the file %s.", work_info.link
                )
                return

            # hook for correct filtering info while parsing source code
            features = get_features(cursor, tf_path)
            tf_path.unlink()
            features.filepath = work_info.link
            features.modify_date = work_info.commit.date
            if self.features_cache is not None:
                self.features_cache.save_features(features)

        return features

    def get_from_files(self: Self, files: list[Path]) -> list[ASTFeatures]:
        if not files:
            return []

        self.logger.debug(f"{GET_FRAZE} files")
        return _get_works_from_filepaths(files, self.features_cache, COMPILE_ARGS)

    def get_works_from_dir(self: Self, directory: Path) -> list[ASTFeatures]:
        filepaths = get_files_path_from_directory(
            directory,
            extensions=SUPPORTED_EXTENSIONS[self.extension],
            path_regexp=self.path_regexp,
        )

        return _get_works_from_filepaths(filepaths, self.features_cache, COMPILE_ARGS)

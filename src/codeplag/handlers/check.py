"""This module contains handlers for the check command of the CLI."""

import logging
import math
import os
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from datetime import timedelta
from itertools import combinations
from pathlib import Path
from time import monotonic

import numpy as np
import pandas as pd
from decouple import Config, RepositoryEnv
from numpy.typing import NDArray
from requests import Session
from typing_extensions import Self

from codeplag.algorithms.compare import compare_works
from codeplag.config import read_settings_conf
from codeplag.consts import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_MODE,
    DEFAULT_MONGO_HOST,
    DEFAULT_MONGO_PORT,
    DEFAULT_MONGO_USER,
    DEFAULT_NGRAMS_LENGTH,
    SUPPORTED_EXTENSIONS,
)
from codeplag.cplag.utils import CFeaturesGetter
from codeplag.db.mongo import (
    FeaturesRepository,
    MongoDBConnection,
    MongoFeaturesCache,
    MongoReporter,
    ReportRepository,
)
from codeplag.display import (
    ComplexProgress,
    Progress,
    print_compare_result,
    print_pretty_progress,
)
from codeplag.featurescache import AbstractFeaturesCache
from codeplag.getfeatures import AbstractGetter
from codeplag.logger import codeplag_logger as logger
from codeplag.pyplag.utils import PyFeaturesGetter
from codeplag.reporters import AbstractReporter, CSVReporter
from codeplag.types import (
    ASTFeatures,
    ExitCode,
    Extension,
    FastCompareInfo,
    Flag,
    FullCompareInfo,
    MaxDepth,
    Mode,
    NgramsLength,
    ProcessingWorks,
    ShortOutput,
    Threshold,
)
from webparsers.github_parser import GitHubParser


class WorksComparator:
    def __init__(
        self: Self,
        extension: Extension,
        repo_regexp: str | None = None,
        path_regexp: str | None = None,
        mode: Mode = DEFAULT_MODE,
        set_github_parser: bool = False,
        all_branches: bool = False,
    ) -> None:
        """Initializes a `FeaturesGetter` and sets settings from the settings config file.

        Args:
        ----
            extension (Extension): The extension of the checked works.
            repo_regexp (str | None, optional): Regular expression for filtering GitHub
              repositories.
            path_regexp (str | None, optional): Regular expression for filtering local files.
            mode (Mode): Mode of searching plagiarism.
            set_github_parser (bool): When True sets GithubParser for search in the GitHub.
            all_branches (bool): When True and the `set_github` option was set,
              searches on all branches of the repository.

        """
        if extension == "py":
            FeaturesGetter = PyFeaturesGetter
        elif extension == "cpp":
            FeaturesGetter = CFeaturesGetter
        else:
            raise Exception(f"Unsupported extension '{extension}'.")

        self.mode: Mode = mode
        self.progress: Progress | None = None

        settings_conf = read_settings_conf()
        self.show_progress: Flag = settings_conf["show_progress"]
        self.short_output = ShortOutput(settings_conf["short_output"])
        self.threshold: Threshold | None = settings_conf["threshold"]
        self.workers: int = settings_conf["workers"]
        self.ngrams_length: NgramsLength = settings_conf.get(
            "ngrams_length", DEFAULT_NGRAMS_LENGTH
        )
        self.max_depth: MaxDepth = settings_conf.get(
            "max_depth",
            DEFAULT_MAX_DEPTH,
        )
        reports = settings_conf.get("reports")
        reports_extension = settings_conf["reports_extension"]
        self.reporter: AbstractReporter | None = None
        features_cache: AbstractFeaturesCache | None = None
        if reports_extension == "mongo":
            host = settings_conf.get("mongo_host", DEFAULT_MONGO_HOST)
            port = settings_conf.get("mongo_port", DEFAULT_MONGO_PORT)
            user = settings_conf.get("mongo_user", DEFAULT_MONGO_USER)
            password = settings_conf.get("mongo_pass")

            if password is None:
                raise Exception("'mongo' reports_exception provided, but mongo-pass is missing")

            connection = MongoDBConnection(host=host, port=port, user=user, password=password)

            features_cache_repo = FeaturesRepository(connection)
            compare_info_repo = ReportRepository(connection)

            features_cache = MongoFeaturesCache(features_cache_repo)
            self.reporter = MongoReporter(compare_info_repo)
        elif reports is not None:
            if reports_extension == "csv":
                Reporter = CSVReporter
            else:
                raise ValueError(f"Unsupported reports extension '{reports_extension}'.")
            self.reporter = Reporter(reports)
        else:
            self.reporter = None

        self.features_getter: AbstractGetter = FeaturesGetter(
            logger=logger,
            repo_regexp=repo_regexp,
            path_regexp=path_regexp,
            features_cache=features_cache,
        )

        if set_github_parser:
            self.set_github_parser(all_branches, settings_conf.get("environment"))

    def set_github_parser(self: Self, all_branches: bool, environment: Path | None = None) -> None:
        """Sets a GitHubParser object for getting works information from GitHub.

        Args:
        ----
            all_branches (bool): Searching in all branches.
            environment (Path | None, optional): Path to the environment file
              with GitHub access token. Defaults to None.

        """
        if not environment:
            logger.warning(
                "Env file not found or not a file. Trying to get token from environment."
            )
            access_token: str = os.environ.get("ACCESS_TOKEN", "")
        else:
            env_config = Config(RepositoryEnv(environment))
            access_token: str = env_config.get("ACCESS_TOKEN", default="")  # type: ignore
        if not access_token:
            logger.warning("GitHub access token is not defined.")
        self.features_getter.set_github_parser(
            GitHubParser(
                file_extensions=SUPPORTED_EXTENSIONS[self.features_getter.extension],
                check_all=all_branches,
                access_token=access_token,
                logger=logging.getLogger(f"{logger.name}.webparsers"),
                session=Session(),
            )
        )

    def check(
        self: Self,
        files: list[Path] | None = None,
        directories: list[Path] | None = None,
        github_files: list[str] | None = None,
        github_project_folders: list[str] | None = None,
        github_user: str = "",
    ) -> ExitCode:
        if files is None:
            files = []
        if directories is None:
            directories = []
        if github_files is None:
            github_files = []
        if github_project_folders is None:
            github_project_folders = []

        logger.debug("Mode: %s; Extension: %s.", self.mode, self.features_getter.extension)
        begin_time = monotonic()
        features_from_files = self.features_getter.get_from_files(files)
        features_from_gh_files = self.features_getter.get_from_github_files(github_files)

        logger.info("Starting searching for plagiarism ...")
        exit_code = ExitCode.EXIT_SUCCESS
        if self.mode == "many_to_many":
            exit_code = self.__many_to_many_check(
                features_from_files,
                directories,
                features_from_gh_files,
                github_project_folders,
                github_user,
            )
        elif self.mode == "one_to_one":
            exit_code = self.__one_to_one_check(
                features_from_files,
                directories,
                features_from_gh_files,
                github_project_folders,
                github_user,
            )
        logger.debug("Time for all %s.", timedelta(seconds=monotonic() - begin_time))
        logger.info("Ending searching for plagiarism ...")
        if isinstance(self.reporter, CSVReporter):
            self.reporter._write_df_to_fs()
        return exit_code

    def __many_to_many_check(
        self: Self,
        features_from_files: list[ASTFeatures],
        directories: list[Path],
        features_from_gh_files: list[ASTFeatures],
        github_project_folders: list[str],
        github_user: str,
    ) -> ExitCode:
        works: list[ASTFeatures] = []
        works.extend(features_from_files)
        works.extend(self.features_getter.get_from_dirs(directories))
        works.extend(features_from_gh_files)
        works.extend(self.features_getter.get_from_github_project_folders(github_project_folders))
        works.extend(self.features_getter.get_from_users_repos(github_user))

        if self.show_progress:
            count_works = len(works)
            iterations = _calc_iterations(count_works)
            logger.info(
                "Works to be checked: %s; Number of checks: %s.",
                count_works,
                iterations,
            )
            self.progress = Progress(iterations)
        exit_code = ExitCode.EXIT_SUCCESS
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            processing: list[ProcessingWorks] = []
            futures: set[Future] = set()
            for i, work1 in enumerate(works):
                for j, work2 in enumerate(works):
                    if i <= j:
                        continue
                    exit_code = ExitCode(
                        exit_code | self._do_step(executor, processing, futures, work1, work2)
                    )
            exit_code = ExitCode(exit_code | self._handle_completed_futures(processing, futures))
        return exit_code

    def __one_to_one_check(
        self: Self,
        features_from_files: list[ASTFeatures],
        directories: list[Path],
        features_from_gh_files: list[ASTFeatures],
        github_project_folders: list[str],
        github_user: str,
    ) -> ExitCode:
        combined_elements = filter(
            bool,
            (
                features_from_files,
                *self.features_getter.get_from_dirs(directories, independent=True),
                features_from_gh_files,
                *self.features_getter.get_from_github_project_folders(
                    github_project_folders, independent=True
                ),
                *self.features_getter.get_from_users_repos(github_user, independent=True),
            ),
        )
        if self.show_progress:
            combined_elements = list(combined_elements)
            count_sequences = len(combined_elements)
            iterations = _calc_iterations(count_sequences, self.mode)
            logger.info(
                "Work sequences to check: %s; Number of external checks: %s.",
                count_sequences,
                iterations,
            )
            self.progress = ComplexProgress(iterations)
        cases = combinations(combined_elements, r=2)
        exit_code = ExitCode.EXIT_SUCCESS
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            processing: list[ProcessingWorks] = []
            futures: set[Future] = set()
            for internal_iteration, case in enumerate(cases, start=1):
                first_sequence, second_sequence = case
                if self.progress is not None:
                    assert isinstance(self.progress, ComplexProgress)
                    internal_iterations = len(first_sequence) * len(second_sequence)
                    logger.debug(
                        "Internal iteration: %s; Number of internal checks: %s.",
                        internal_iteration,
                        internal_iterations,
                    )
                    self.progress.add_internal_progress(internal_iterations)
                for work1 in first_sequence:
                    for work2 in second_sequence:
                        exit_code = ExitCode(
                            exit_code | self._do_step(executor, processing, futures, work1, work2)
                        )
            exit_code = ExitCode(exit_code | self._handle_completed_futures(processing, futures))
        return exit_code

    def _do_step(
        self: Self,
        executor: ProcessPoolExecutor,
        processing: list[ProcessingWorks],
        futures: set[Future],
        work1: ASTFeatures,
        work2: ASTFeatures,
    ) -> ExitCode:
        if work1 == work2:
            _print_pretty_progress_if_need_and_increase(self.progress, self.workers)
            return ExitCode.EXIT_SUCCESS

        work1, work2 = sorted([work1, work2])
        metrics = None
        if self.reporter is not None:
            metrics = self.reporter.get_result(work1, work2)
        if metrics is None:
            future = self._create_future_compare(executor, work1, work2)
            future.id = len(processing)  # type: ignore
            futures.add(future)
            processing.append(ProcessingWorks(work1, work2))
            return ExitCode.EXIT_SUCCESS
        if self.short_output is ShortOutput.SHOW_ALL:
            self._handle_compare_result(work1, work2, metrics)
        _print_pretty_progress_if_need_and_increase(self.progress, self.workers)
        return ExitCode.EXIT_FOUND_SIM

    def _handle_compare_result(
        self: Self,
        work1: ASTFeatures,
        work2: ASTFeatures,
        metrics: FullCompareInfo | FastCompareInfo,
        save: bool = False,
    ) -> ExitCode:
        logger.trace(  # type: ignore
            "Compare '%s' with '%s' finished.", work1.filepath, work2.filepath
        )
        if isinstance(metrics, FastCompareInfo):
            return ExitCode.EXIT_SUCCESS
        logger.trace(  # type: ignore
            "Found similarity '%s' with '%s'.", work1.filepath, work2.filepath
        )
        if self.reporter and save:
            self.reporter.save_result(work1, work2, metrics)
        if self.short_output is ShortOutput.NO_SHOW:
            return ExitCode.EXIT_FOUND_SIM

        if self.threshold and (metrics.structure.similarity * 100) <= self.threshold:
            print_compare_result(work1, work2, metrics)
        else:
            print_compare_result(
                work1,
                work2,
                metrics,
                compliance_matrix_to_df(
                    metrics.structure.compliance_matrix,
                    work1.head_nodes,
                    work2.head_nodes,
                ),
            )
        return ExitCode.EXIT_FOUND_SIM

    def _handle_completed_futures(
        self: Self,
        processing: list[ProcessingWorks],
        futures: set[Future],
    ) -> ExitCode:
        exit_code = ExitCode.EXIT_SUCCESS
        for future in as_completed(futures):
            metrics: FullCompareInfo | FastCompareInfo = future.result()
            proc_works_info = processing[future.id]  # type: ignore
            exit_code = ExitCode(
                exit_code
                | self._handle_compare_result(
                    proc_works_info.work1, proc_works_info.work2, metrics, save=True
                )
            )
            _print_pretty_progress_if_need_and_increase(self.progress, self.workers)
        return exit_code

    def _create_future_compare(
        self: Self,
        executor: ProcessPoolExecutor,
        work1: ASTFeatures,
        work2: ASTFeatures,
    ) -> Future:
        logger.trace("Creating future compare '%s' with '%s'.", work1.filepath, work2.filepath)  # type: ignore
        return executor.submit(
            compare_works, work1, work2, self.ngrams_length, self.max_depth, self.threshold
        )


class IgnoreThresholdWorksComparator(WorksComparator):
    def __init__(
        self: Self,
        extension: Extension,
        repo_regexp: str | None = None,
        path_regexp: str | None = None,
        mode: Mode = DEFAULT_MODE,
        set_github_parser: bool = False,
        all_branches: bool = False,
    ) -> None:
        super().__init__(
            extension, repo_regexp, path_regexp, mode, set_github_parser, all_branches
        )
        self.threshold = None


def compliance_matrix_to_df(
    compliance_matrix: NDArray,
    head_nodes1: list[str],
    head_nodes2: list[str],
) -> pd.DataFrame:
    data = np.empty(
        (
            compliance_matrix.shape[0],
            compliance_matrix.shape[1],
        ),
        dtype=np.float64,
    )
    for row in range(compliance_matrix.shape[0]):
        for col in range(compliance_matrix.shape[1]):
            data[row][col] = compliance_matrix[row][col][0] / compliance_matrix[row][col][1]
    compliance_matrix_df = pd.DataFrame(
        data=data, index=np.array(head_nodes1), columns=np.array(head_nodes2)
    )
    return compliance_matrix_df


def _calc_iterations(count: int, mode: Mode = DEFAULT_MODE) -> int:
    """Calculates the required number of iterations for all checks."""
    if count <= 1:
        return 0

    if mode == "many_to_many":
        return (count * (count - 1)) // 2
    if mode == "one_to_one":
        return math.factorial(count) // 2 * math.factorial(count - 2)
    else:
        raise ValueError(f"The provided mode '{mode}' is invalid.")


def _print_pretty_progress_if_need_and_increase(progress: Progress | None, workers: int) -> None:
    if progress is None:
        return
    print_pretty_progress(progress, workers)
    next(progress)

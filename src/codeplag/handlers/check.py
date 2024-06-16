"""This module contains handlers for the check command of the CLI."""

import logging
import math
import os
from concurrent.futures import Future, ProcessPoolExecutor
from itertools import combinations
from pathlib import Path
from time import monotonic
from typing import Optional

import numpy as np
import pandas as pd
from decouple import Config, RepositoryEnv
from numpy.typing import NDArray
from requests import Session
from webparsers.github_parser import GitHubParser

from codeplag.algorithms.compare import compare_works
from codeplag.config import read_settings_conf
from codeplag.consts import DEFAULT_MODE, SUPPORTED_EXTENSIONS
from codeplag.cplag.utils import CFeaturesGetter
from codeplag.display import (
    ComplexProgress,
    Progress,
    print_compare_result,
    print_pretty_progress,
)
from codeplag.getfeatures import AbstractGetter
from codeplag.logger import codeplag_logger as logger
from codeplag.pyplag.utils import PyFeaturesGetter
from codeplag.reporters import CSVReporter, JSONReporter
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    Extension,
    Flag,
    Mode,
    ProcessingWorksInfo,
    Threshold,
)


class WorksComparator:
    def __init__(
        self,
        extension: Extension,
        repo_regexp: Optional[str] = None,
        path_regexp: Optional[str] = None,
        mode: Mode = DEFAULT_MODE,
        set_github_parser: bool = False,
        all_branches: bool = False,
    ) -> None:
        """Initializes a feature getter for further comparison. Sets the needed
        settings from the settings config file.

        Args:
        ----
            extension (Extension): The extension of the checked works.
            repo_regexp (Optional[str]): Regular expression for filtering GitHub repositories.
            path_regexp (Optional[str]): Regular expression for filtering local files.
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

        self.features_getter: AbstractGetter = FeaturesGetter(
            logger=logger,
            repo_regexp=repo_regexp,
            path_regexp=path_regexp,
        )
        self.mode: Mode = mode
        self.progress: Optional[Progress] = None

        settings_conf = read_settings_conf()
        self.show_progress: Flag = settings_conf["show_progress"]
        self.threshold: Optional[Threshold] = settings_conf["threshold"]
        self.workers: int = settings_conf["workers"]
        reports = settings_conf.get("reports")
        if reports is not None:
            reports_extension = settings_conf["reports_extension"]
            Reporter = CSVReporter if reports_extension == "csv" else JSONReporter
            self.reporter = Reporter(reports)
        else:
            self.reporter = None

        if set_github_parser:
            self.set_github_parser(all_branches, settings_conf.get("environment"))

    def set_github_parser(
        self, all_branches: bool, environment: Optional[Path] = None
    ) -> None:
        """Sets a GitHubParser object for getting works information from GitHub.

        Args:
        ----
            all_branches (bool): Searching in all branches.
            environment (Optional[Path], optional): Path to the environment file
              with GitHub access token. Defaults to None.

        """
        if not environment:
            logger.warning(
                "Env file not found or not a file. "
                "Trying to get token from environment."
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
        self,
        files: Optional[list[Path]] = None,
        directories: Optional[list[Path]] = None,
        github_files: Optional[list[str]] = None,
        github_project_folders: Optional[list[str]] = None,
        github_user: str = "",
    ) -> None:
        if files is None:
            files = []
        if directories is None:
            directories = []
        if github_files is None:
            github_files = []
        if github_project_folders is None:
            github_project_folders = []

        logger.debug(
            f"Mode: {self.mode}; " f"Extension: {self.features_getter.extension}."
        )
        begin_time = monotonic()
        features_from_files = self.features_getter.get_from_files(files)
        features_from_gh_files = self.features_getter.get_from_github_files(
            github_files
        )

        logger.info("Starting searching for plagiarism ...")
        if self.mode == "many_to_many":
            self.__many_to_many_check(
                features_from_files,
                directories,
                features_from_gh_files,
                github_project_folders,
                github_user,
            )
        elif self.mode == "one_to_one":
            self.__one_to_one_check(
                features_from_files,
                directories,
                features_from_gh_files,
                github_project_folders,
                github_user,
            )
        logger.debug(f"Time for all {monotonic() - begin_time:.2f}s")
        logger.info("Ending searching for plagiarism ...")
        if isinstance(self.reporter, CSVReporter):
            self.reporter._write_df_to_fs()

    def __many_to_many_check(
        self,
        features_from_files: list[ASTFeatures],
        directories: list[Path],
        features_from_gh_files: list[ASTFeatures],
        github_project_folders: list[str],
        github_user: str,
    ):
        works: list[ASTFeatures] = []
        works.extend(features_from_files)
        works.extend(self.features_getter.get_from_dirs(directories))
        works.extend(features_from_gh_files)
        works.extend(
            self.features_getter.get_from_github_project_folders(github_project_folders)
        )
        works.extend(self.features_getter.get_from_users_repos(github_user))

        if self.show_progress:
            count_works = len(works)
            self.progress = Progress(_calc_iterations(count_works))
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            processed: list[ProcessingWorksInfo] = []
            for i, work1 in enumerate(works):
                for j, work2 in enumerate(works):
                    if i <= j:
                        continue
                    self._do_step(executor, processed, work1, work2)
            self._handle_completed_futures(processed)

    def __one_to_one_check(
        self,
        features_from_files: list[ASTFeatures],
        directories: list[Path],
        features_from_gh_files: list[ASTFeatures],
        github_project_folders: list[str],
        github_user: str,
    ):
        combined_elements = filter(
            bool,
            (
                features_from_files,
                *self.features_getter.get_from_dirs(directories, independent=True),
                features_from_gh_files,
                *self.features_getter.get_from_github_project_folders(
                    github_project_folders, independent=True
                ),
                *self.features_getter.get_from_users_repos(
                    github_user, independent=True
                ),
            ),
        )
        if self.show_progress:
            combined_elements = list(combined_elements)
            count_sequences = len(combined_elements)
            self.progress = ComplexProgress(
                _calc_iterations(count_sequences, self.mode)
            )
        cases = combinations(combined_elements, r=2)
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            processed: list[ProcessingWorksInfo] = []
            for case in cases:
                first_sequence, second_sequence = case
                if self.progress is not None:
                    assert isinstance(self.progress, ComplexProgress)
                    self.progress.add_internal_progress(
                        len(first_sequence) * len(second_sequence)
                    )
                for work1 in first_sequence:
                    for work2 in second_sequence:
                        self._do_step(executor, processed, work1, work2)
            self._handle_completed_futures(processed)

    def _do_step(
        self,
        executor: ProcessPoolExecutor,
        processing: list[ProcessingWorksInfo],
        work1: ASTFeatures,
        work2: ASTFeatures,
    ) -> None:
        if work1.filepath == work2.filepath:
            _print_pretty_progress_if_need_and_increase(self.progress, self.workers)
            return

        work1, work2 = sorted([work1, work2])
        metrics = None
        if isinstance(self.reporter, CSVReporter):
            metrics = self.reporter.get_compare_result_from_cache(work1, work2)
        if metrics is None:
            processing.append(
                ProcessingWorksInfo(
                    work1, work2, self._create_future_compare(executor, work1, work2)
                )
            )
            return
        self._handle_compare_result(work1, work2, metrics)
        _print_pretty_progress_if_need_and_increase(self.progress, self.workers)

    def _handle_compare_result(
        self,
        work1: ASTFeatures,
        work2: ASTFeatures,
        metrics: CompareInfo,
        save: bool = False,
    ) -> None:
        if metrics.structure is None:
            return
        if self.reporter and save:
            self.reporter.save_result(work1, work2, metrics)

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

    def _handle_completed_futures(
        self,
        processing: list[ProcessingWorksInfo],
    ):
        for proc_works_info in processing:
            metrics: CompareInfo = proc_works_info.compare_future.result()
            self._handle_compare_result(
                proc_works_info.work1, proc_works_info.work2, metrics, save=True
            )
            _print_pretty_progress_if_need_and_increase(self.progress, self.workers)

    def _create_future_compare(
        self,
        executor: ProcessPoolExecutor,
        work1: ASTFeatures,
        work2: ASTFeatures,
    ) -> Future:
        return executor.submit(compare_works, work1, work2, self.threshold)


class IgnoreThresholdWorksComparator(WorksComparator):
    def __init__(
        self,
        extension: Extension,
        repo_regexp: Optional[str] = None,
        path_regexp: Optional[str] = None,
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
    data = np.zeros(
        (
            compliance_matrix.shape[0],
            compliance_matrix.shape[1],
        ),
        dtype=np.float64,
    )
    for row in range(compliance_matrix.shape[0]):
        for col in range(compliance_matrix.shape[1]):
            data[row][col] = (
                compliance_matrix[row][col][0] / compliance_matrix[row][col][1]
            )
    compliance_matrix_df = pd.DataFrame(
        data=data, index=head_nodes1, columns=head_nodes2
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


def _print_pretty_progress_if_need_and_increase(
    progress: Optional[Progress], workers: int
) -> None:
    if progress is None:
        return
    print_pretty_progress(progress, workers)
    next(progress)

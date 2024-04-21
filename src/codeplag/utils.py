import logging
import math
import os
import uuid
from concurrent.futures import Future, ProcessPoolExecutor
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from time import monotonic, perf_counter
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
from decouple import Config, RepositoryEnv
from numpy.typing import NDArray
from requests import Session
from webparsers.github_parser import GitHubParser

from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.config import read_settings_conf, write_config
from codeplag.consts import (
    CSV_REPORT_COLUMNS,
    CSV_REPORT_FILENAME,
    CSV_SAVE_TICK,
    DEFAULT_WEIGHTS,
    SUPPORTED_EXTENSIONS,
)
from codeplag.cplag.utils import CFeaturesGetter
from codeplag.display import (
    ComplexProgress,
    Progress,
    print_compare_result,
)
from codeplag.getfeatures import AbstractGetter
from codeplag.handlers.report import (
    deserialize_compare_result,
    html_report_create,
    read_df,
    serialize_compare_result,
)
from codeplag.handlers.settings import settings_modify, settings_show
from codeplag.pyplag.utils import PyFeaturesGetter
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    Extension,
    FastMetrics,
    Flag,
    Mode,
    ProcessingWorksInfo,
    ReportsExtension,
    Settings,
    StructuresInfo,
    WorksReport,
)


def get_compliance_matrix_df(
    compliance_matrix: NDArray,
    head_nodes1: List[str],
    head_nodes2: List[str],
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


def fast_compare(
    features_f: ASTFeatures,
    features_s: ASTFeatures,
    weights: Tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> FastMetrics:
    """The function calculates the similarity of features of two programs
    using four algorithms, calculates their weighted average, and returns
    all of this  in 'FastMetrics' structure.

    @features_f - the features of the first  source file
    @features_s - the features of the second  source file
    @weights - weights of fast metrics that participate in
    counting total similarity coefficient
    """

    jakkar_coef = value_jakkar_coef(features_f.tokens, features_s.tokens)
    ops_res = counter_metric(features_f.operators, features_s.operators)
    kw_res = counter_metric(features_f.keywords, features_s.keywords)
    lits_res = counter_metric(features_f.literals, features_s.literals)
    weighted_average = np.average(
        np.array([jakkar_coef, ops_res, kw_res, lits_res]), weights=weights
    )

    fast_metrics = FastMetrics(
        jakkar=jakkar_coef,
        operators=ops_res,
        keywords=kw_res,
        literals=lits_res,
        weighted_average=float(weighted_average),
    )

    return fast_metrics


def compare_works(
    features1: ASTFeatures, features2: ASTFeatures, threshold: Optional[int] = None
) -> CompareInfo:
    """The function returns the result of comparing two works.

    Args:
        features1: The features of the first work.
        features2: The features of the second work.
        threshold: The threshold of plagiarism searcher alarm.

    Returns:
        CompareInfo, which is the result of comparing works.
        This can consist of fast metrics and, if the threshold
        value has been crossed, structure metric.
        If the threshold value is not set, it returns the structure
        metric anywhere.
    """

    fast_metrics = fast_compare(features1, features2)
    if threshold and (fast_metrics.weighted_average * 100.0) < threshold:
        return CompareInfo(fast=fast_metrics)

    compliance_matrix = np.zeros(
        (len(features1.head_nodes), len(features2.head_nodes), 2), dtype=np.int64
    )
    struct_res = struct_compare(
        features1.structure, features2.structure, compliance_matrix
    )
    struct_res = struct_res[0] / struct_res[1]

    structure_info = StructuresInfo(
        similarity=struct_res, compliance_matrix=compliance_matrix
    )

    return CompareInfo(fast=fast_metrics, structure=structure_info)


def calc_iterations(count: int, mode: Mode = "many_to_many") -> int:
    """Calculates the required number of iterations for all checks."""
    if count <= 1:
        return 0

    if mode == "many_to_many":
        return (count * (count - 1)) // 2
    if mode == "one_to_one":
        return math.factorial(count) // 2 * math.factorial(count - 2)
    else:
        raise ValueError(f"The provided mode '{mode}' is invalid.")


# TODO: Split this disaster class into smaller class and functions
class CodeplagEngine:
    def __init__(self, logger: logging.Logger, parsed_args: Dict[str, Any]) -> None:
        self.root: str = parsed_args.pop("root")
        self.command: Optional[str] = None
        # TODO: tmp
        self.logger = logger
        if self.root == "settings":
            self.command = parsed_args.pop(self.root)
            if self.command == "show":
                return

            self.parsed_args = parsed_args
        elif self.root == "report":
            self.path: Path = parsed_args.pop("path")
        else:
            settings_conf = read_settings_conf()
            self._set_features_getter(parsed_args)

            self.progress: Optional[Progress] = None
            self.mode: Mode = parsed_args.pop("mode", "many_to_many")
            self.show_progress: Flag = settings_conf["show_progress"]
            self.threshold: int = settings_conf["threshold"]
            self.workers: int = settings_conf["workers"]

            self.reports: Optional[Path] = settings_conf.get("reports")
            self.__reports_extension: ReportsExtension = settings_conf[
                "reports_extension"
            ]
            if self.__reports_extension == "csv" and self.reports:
                reports_path = self.reports / CSV_REPORT_FILENAME
                if reports_path.is_file():
                    self.__df_report = read_df(self.reports / CSV_REPORT_FILENAME)
                    self.__start_report_lines = self.__df_report.shape[0]
                else:
                    self.__df_report = pd.DataFrame(
                        columns=CSV_REPORT_COLUMNS, dtype=object
                    )
                    self.__start_report_lines = 0
                self.__csv_last_save = perf_counter()

            self.github_files: List[str] = parsed_args.pop("github_files", [])
            self.github_project_folders: List[str] = parsed_args.pop(
                "github_project_folders", []
            )
            self.github_user: str = parsed_args.pop("github_user", "") or ""
            if self.github_files or self.github_project_folders or self.github_user:
                self._set_github_parser(parsed_args, settings_conf)

            self.files: List[Path] = parsed_args.pop("files", [])
            self.directories: List[Path] = parsed_args.pop("directories", [])

    def _set_features_getter(
        self,
        parsed_args: Dict[str, Any],
    ) -> None:
        extension: Extension = parsed_args.pop("extension")
        if extension == "py":
            FeaturesGetter = PyFeaturesGetter
        elif extension == "cpp":
            FeaturesGetter = CFeaturesGetter
        else:
            raise Exception(f"Unsupported extension '{extension}'.")

        self.features_getter: AbstractGetter = FeaturesGetter(
            logger=self.logger,
            repo_regexp=parsed_args.pop("repo_regexp", None),
            path_regexp=parsed_args.pop("path_regexp", None),
        )

    def _set_github_parser(
        self, parsed_args: Dict[str, Any], settings_conf: Settings
    ) -> None:
        environment = settings_conf.get("environment")
        if not environment:
            self.logger.warning(
                "Env file not found or not a file. "
                "Trying to get token from environment."
            )
            access_token: str = os.environ.get("ACCESS_TOKEN", "")
        else:
            env_config = Config(RepositoryEnv(environment))
            access_token: str = env_config.get("ACCESS_TOKEN", default="")  # type: ignore
        if not access_token:
            self.logger.warning("GitHub access token is not defined.")
        self.features_getter.set_github_parser(
            GitHubParser(
                file_extensions=SUPPORTED_EXTENSIONS[self.features_getter.extension],
                check_all=parsed_args.pop("all_branches", False),
                access_token=access_token,
                logger=logging.getLogger(f"{self.logger.name}.webparsers"),
                session=Session(),
            )
        )

    def save_result(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
        reports_extension: ReportsExtension,
    ) -> None:
        if self.reports is None or not self.reports.is_dir():
            self.logger.error(
                "The folder for reports isn't provided or now isn't exists."
            )
            return

        # TODO: use match in the next py version
        if reports_extension == "csv":
            self.__save_result_to_csv(
                first_work,
                second_work,
                compare_info,
            )
        else:
            self.__save_result_to_json(
                first_work,
                second_work,
                compare_info,
            )

    def __save_result_to_json(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        metrics: CompareInfo,
    ) -> None:
        assert metrics.structure is not None

        struct_info_dict = metrics.structure._asdict()
        struct_info_dict["compliance_matrix"] = struct_info_dict[
            "compliance_matrix"
        ].tolist()
        report = WorksReport(
            date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            first_path=first_work.filepath.__str__(),
            second_path=second_work.filepath.__str__(),
            first_heads=first_work.head_nodes,
            second_heads=second_work.head_nodes,
            fast=metrics.fast._asdict(),
            structure=struct_info_dict,
        )
        if first_work.modify_date:
            report["first_modify_date"] = first_work.modify_date
        if second_work.modify_date:
            report["second_modify_date"] = second_work.modify_date

        try:
            report_file = self.reports / f"{uuid.uuid4().hex}.json"  # type: ignore
            write_config(report_file, report)
        except PermissionError:
            self.logger.error("Not enough rights to write reports to the folder.")

    def _write_df_to_fs(self) -> None:
        if self.__reports_extension != "csv" or not self.reports:
            return

        if self.__start_report_lines == self.__df_report.shape[0]:
            self.logger.debug("Nothing new to save to the csv report.")
            return

        report_path = self.reports / CSV_REPORT_FILENAME
        self.logger.debug(f"Saving report to the file '{report_path}'")
        self.__df_report.to_csv(report_path, sep=";")
        self.__start_report_lines = self.__df_report.shape[0]

    def __save_result_to_csv(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        metrics: CompareInfo,
    ) -> None:
        self.__df_report = pd.concat(
            [
                self.__df_report,
                serialize_compare_result(first_work, second_work, metrics),
            ],
            ignore_index=True,
        )
        if perf_counter() - self.__csv_last_save > CSV_SAVE_TICK:
            self._write_df_to_fs()
            # Time to write can be long
            self.__csv_last_save = perf_counter()

    def get_compare_result_from_cache(
        self, work1: ASTFeatures, work2: ASTFeatures
    ) -> Optional[CompareInfo]:
        if not (self.reports and self.__reports_extension == "csv"):
            return
        cache_val = self.__df_report[
            (self.__df_report.first_path == str(work1.filepath))
            & (self.__df_report.second_path == str(work2.filepath))
        ]
        if cache_val.shape[0]:
            return deserialize_compare_result(cache_val.iloc[0])

    def _create_future_compare(
        self,
        executor: ProcessPoolExecutor,
        work1: ASTFeatures,
        work2: ASTFeatures,
    ) -> Future:
        return executor.submit(compare_works, work1, work2, self.threshold)

    def __print_pretty_progress_and_increase(self) -> None:
        if self.progress is None:
            return
        time_spent_seconds = monotonic() - self.begin_time
        time_spent = timedelta(seconds=int(time_spent_seconds))
        current_progress = self.progress.progress
        if current_progress != 0.0:
            predicated_time_left = timedelta(
                seconds=int(
                    (1.0 - current_progress) / current_progress * time_spent_seconds
                )
            )
        else:
            predicated_time_left = "N/A"
        print(
            f"{self.progress}, "
            f"{time_spent} time spent [predicted time left {predicated_time_left}], "
            f"{self.workers} workers",
            end="\r",
        )
        next(self.progress)

    def _do_step(
        self,
        executor: ProcessPoolExecutor,
        processing: List[ProcessingWorksInfo],
        work1: ASTFeatures,
        work2: ASTFeatures,
    ) -> None:
        if work1.filepath == work2.filepath:
            self.__print_pretty_progress_and_increase()
            return

        work1, work2 = sorted([work1, work2])
        metrics = self.get_compare_result_from_cache(work1, work2)
        if metrics is None:
            processing.append(
                ProcessingWorksInfo(
                    work1, work2, self._create_future_compare(executor, work1, work2)
                )
            )
            return
        self._handle_compare_result(work1, work2, metrics)
        self.__print_pretty_progress_and_increase()

    def _handle_compare_result(
        self,
        work1: ASTFeatures,
        work2: ASTFeatures,
        metrics: CompareInfo,
        save: bool = False,
    ) -> None:
        if metrics.structure is None:
            return
        if self.reports and save:
            self.save_result(work1, work2, metrics, self.__reports_extension)

        if (metrics.structure.similarity * 100) <= self.threshold:
            print_compare_result(work1, work2, metrics)
        else:
            print_compare_result(
                work1,
                work2,
                metrics,
                get_compliance_matrix_df(
                    metrics.structure.compliance_matrix,
                    work1.head_nodes,
                    work2.head_nodes,
                ),
            )

    def _handle_completed_futures(
        self,
        processing: List[ProcessingWorksInfo],
    ):
        for proc_works_info in processing:
            metrics: CompareInfo = proc_works_info.compare_future.result()
            self._handle_compare_result(
                proc_works_info.work1, proc_works_info.work2, metrics, save=True
            )
            self.__print_pretty_progress_and_increase()

    def __many_to_many_check(
        self,
        features_from_files: List[ASTFeatures],
        features_from_gh_files: List[ASTFeatures],
    ):
        works: List[ASTFeatures] = []
        works.extend(features_from_files)
        works.extend(self.features_getter.get_from_dirs(self.directories))
        works.extend(features_from_gh_files)
        works.extend(
            self.features_getter.get_from_github_project_folders(
                self.github_project_folders
            )
        )
        works.extend(self.features_getter.get_from_users_repos(self.github_user))

        if self.show_progress:
            count_works = len(works)
            self.progress = Progress(calc_iterations(count_works))
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            processed: List[ProcessingWorksInfo] = []
            for i, work1 in enumerate(works):
                for j, work2 in enumerate(works):
                    if i <= j:
                        continue
                    self._do_step(executor, processed, work1, work2)
            self._handle_completed_futures(processed)

    def __one_to_one_check(
        self,
        features_from_files: List[ASTFeatures],
        features_from_gh_files: List[ASTFeatures],
    ):
        combined_elements = filter(
            bool,
            (
                features_from_files,
                *self.features_getter.get_from_dirs(self.directories, independent=True),
                features_from_gh_files,
                *self.features_getter.get_from_github_project_folders(
                    self.github_project_folders, independent=True
                ),
                *self.features_getter.get_from_users_repos(
                    self.github_user, independent=True
                ),
            ),
        )
        if self.show_progress:
            combined_elements = list(combined_elements)
            count_sequences = len(combined_elements)
            self.progress = ComplexProgress(calc_iterations(count_sequences, self.mode))
        cases = combinations(combined_elements, r=2)
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            processed: List[ProcessingWorksInfo] = []
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

    def __check(self) -> None:
        self.logger.debug(
            f"Mode: {self.mode}; Extension: {self.features_getter.extension}."
        )
        self.begin_time = monotonic()
        features_from_files = self.features_getter.get_from_files(self.files)
        features_from_gh_files = self.features_getter.get_from_github_files(
            self.github_files
        )

        self.logger.info("Starting searching for plagiarism ...")
        if self.mode == "many_to_many":
            self.__many_to_many_check(features_from_files, features_from_gh_files)
        elif self.mode == "one_to_one":
            self.__one_to_one_check(features_from_files, features_from_gh_files)
        self.logger.debug(f"Time for all {monotonic() - self.begin_time:.2f}s")
        self.logger.info("Ending searching for plagiarism ...")

    def run(self) -> Literal[0, 1]:
        self.logger.debug("Starting codeplag util ...")

        if self.root == "settings":
            if self.command == "show":
                settings_show()
            elif self.command == "modify":
                settings_modify(self.parsed_args)
                settings_show()
        elif self.root == "report":
            return html_report_create(self.path, self.logger)
        else:
            self.__check()
            self._write_df_to_fs()
        return 0

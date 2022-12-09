import logging
import math
import uuid
from datetime import datetime
from itertools import combinations
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.config import read_settings_conf, write_config, write_settings_conf
from codeplag.cplag.utils import CFeaturesGetter
from codeplag.display import print_compare_result
from codeplag.getfeatures import AbstractGetter
from codeplag.pyplag.utils import PyFeaturesGetter
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    Extension,
    FastMetrics,
    Flag,
    Settings,
    StructuresInfo,
    WorksReport,
)


def fast_compare(features_f: ASTFeatures,
                 features_s: ASTFeatures,
                 weights: tuple = (1, 0.4, 0.4, 0.4)) -> FastMetrics:
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
        [jakkar_coef, ops_res, kw_res, lits_res],
        weights=weights
    )

    fast_metrics = FastMetrics(
        jakkar=jakkar_coef,
        operators=ops_res,
        keywords=kw_res,
        literals=lits_res,
        weighted_average=weighted_average
    )

    return fast_metrics


def compare_works(features1: ASTFeatures,
                  features2: ASTFeatures,
                  threshold: int = 60) -> CompareInfo:
    """The function returns the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @threshold - threshold of plagiarism searcher alarm
    """

    fast_metrics = fast_compare(features1, features2)
    if (fast_metrics.weighted_average * 100.0) < threshold:
        return CompareInfo(fast=fast_metrics)

    compliance_matrix = np.zeros(
        (len(features1.head_nodes), len(features2.head_nodes), 2),
        dtype=np.int64
    )
    struct_res = struct_compare(features1.structure, features2.structure,
                                compliance_matrix)
    struct_res = struct_res[0] / struct_res[1]

    structure_info = StructuresInfo(
        similarity=struct_res,
        compliance_matrix=compliance_matrix
    )

    return CompareInfo(
        fast=fast_metrics,
        structure=structure_info
    )


def calc_iterations(count, mode: str = 'many_to_many') -> int:
    if count <= 1:
        return 0

    if mode == 'many_to_many':
        return (count * (count - 1)) // 2
    if mode == 'one_to_one':
        return math.factorial(count) // 2 * math.factorial(count - 2)

    return 0


def calc_progress(
    iteration: int,
    iterations: int,
    internal_iteration: int = 0,
    internal_iterations: int = 0
) -> float:
    if iterations == 0:
        return 0.0

    progress = iteration / iterations
    if internal_iterations == 0:
        return progress

    if internal_iteration * internal_iterations:
        progress += internal_iteration / (internal_iterations * iterations)

    return progress


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

            # Check if all None, print error
            self.environment: Optional[Path] = parsed_args.pop("environment")
            self.reports: Optional[Path] = parsed_args.pop("reports")
            self.threshold: int = parsed_args.pop("threshold")
            self.show_progress: Flag = parsed_args.pop("show_progress")
        else:
            settings_conf = read_settings_conf(logger)
            self._set_features_getter(parsed_args, settings_conf, logger)

            self.mode: str = parsed_args.pop('mode', 'many_to_many')
            self.show_progress: Flag = settings_conf.get('show_progress')
            self.threshold: int = settings_conf["threshold"]
            self.reports: Optional[Path] = settings_conf.pop(
                'reports', None
            )

            self.github_files: List[str] = parsed_args.pop('github_files', [])
            self.github_project_folders: List[str] = parsed_args.pop(
                'github_project_folders', []
            )
            self.github_user: str = parsed_args.pop('github_user', '')

            self.files: List[Path] = parsed_args.pop('files', [])
            self.directories: List[Path] = parsed_args.pop('directories', [])

    def _set_features_getter(
        self,
        parsed_args: Dict[str, Any],
        settings_conf: Settings,
        logger: logging.Logger
    ) -> None:
        extension: Extension = parsed_args.pop('extension')
        if extension == 'py':
            FeaturesGetter = PyFeaturesGetter
        elif extension == 'cpp':
            FeaturesGetter = CFeaturesGetter

        self.features_getter: AbstractGetter = FeaturesGetter(
            environment=settings_conf.get("environment"),
            all_branches=parsed_args.pop('all_branches', False),
            logger=logger,
            repo_regexp=parsed_args.pop('repo_regexp', None),
            path_regexp=parsed_args.pop('path_regexp', None)
        )

    def save_result(self,
                    first_work: ASTFeatures,
                    second_work: ASTFeatures,
                    fast_metrics: FastMetrics,
                    structure: StructuresInfo) -> None:
        if self.reports is None or not self.reports.is_dir():
            self.features_getter.logger.warning(
                "The folder for reports isn't provided or now isn't exists."
            )
            return

        struct_info_dict = structure._asdict()
        struct_info_dict['compliance_matrix'] = (
            struct_info_dict['compliance_matrix'].tolist()
        )
        report = WorksReport(
            date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            first_path=first_work.filepath.__str__(),
            second_path=second_work.filepath.__str__(),
            first_heads=first_work.head_nodes,
            second_heads=second_work.head_nodes,
            fast=fast_metrics._asdict(),
            structure=struct_info_dict
        )

        try:
            report_file = self.reports / f'{uuid.uuid4().hex}.json'
            write_config(report_file, report)
        except PermissionError:
            self.features_getter.logger.warning(
                "Not enough rights to write reports to the folder."
            )

    def _do_step(self, work1: ASTFeatures, work2: ASTFeatures) -> None:
        metrics = compare_works(work1, work2, self.threshold)
        if metrics.structure is None:
            return

        print_compare_result(
            work1,
            work2,
            metrics,
            self.threshold
        )
        if self.reports:
            self.save_result(work1, work2, metrics.fast, metrics.structure)

    def _calc_and_print_progress(
        self,
        iteration: int,
        iterations: int,
        internal_iteration: int = 0,
        internal_iterations: int = 0
    ) -> None:
        progress = calc_progress(
            iteration, iterations, internal_iteration, internal_iterations
        )
        print(f"Check progress: {progress:.2%}.", end='\r')

    def _settings_show(self) -> None:
        settings_config = read_settings_conf(self.logger)
        table = pd.DataFrame(
            list(settings_config.values()),
            index=[k.capitalize() for k in settings_config.keys()],
            columns=pd.Index(
                ["Value"],
                name="Key"
            )
        )
        print(table)

    def _settings_modify(self) -> None:
        settings_config = read_settings_conf(self.logger)
        for key in Settings.__annotations__:
            new_value = getattr(self, key, None)
            if new_value is not None:
                if isinstance(new_value, Path):
                    settings_config[key] = new_value.absolute()
                else:
                    settings_config[key] = new_value

            write_settings_conf(settings_config)

    def _check(self) -> None:
        self.features_getter.logger.debug(
            f"Mode: {self.mode}; "
            f"Extension: {self.features_getter.extension}."
        )

        begin_time = perf_counter()

        features_from_files = self.features_getter.get_from_files(self.files)
        features_from_gh_files = self.features_getter.get_from_github_files(
            self.github_files
        )

        self.features_getter.logger.info("Starting searching for plagiarism")
        if self.mode == 'many_to_many':
            works: List[ASTFeatures] = []
            works.extend(features_from_files)
            works.extend(
                self.features_getter.get_from_dirs(
                    self.directories
                )
            )
            works.extend(features_from_gh_files)
            works.extend(
                self.features_getter.get_from_github_project_folders(
                    self.github_project_folders
                )
            )
            works.extend(
                self.features_getter.get_from_users_repos(self.github_user)
            )

            count_works = len(works)
            iterations = calc_iterations(count_works)
            iteration = 0
            for i, work1 in enumerate(works):
                for j, work2 in enumerate(works):
                    if i <= j:
                        continue

                    if self.show_progress:
                        self._calc_and_print_progress(
                            iteration, iterations
                        )
                        iteration += 1

                    self._do_step(work1, work2)
        elif self.mode == 'one_to_one':
            combined_elements = filter(
                bool,
                (
                    features_from_files,
                    *self.features_getter.get_from_dirs(
                        self.directories, independent=True
                    ),
                    features_from_gh_files,
                    *self.features_getter.get_from_github_project_folders(
                        self.github_project_folders, independent=True
                    ),
                    *self.features_getter.get_from_users_repos(
                        self.github_user, independent=True
                    )
                )
            )
            if self.show_progress:
                combined_elements = list(combined_elements)
                count_sequences = len(combined_elements)
                iterations = calc_iterations(count_sequences, self.mode)
                iteration = 0

            cases = combinations(
                combined_elements,
                r=2
            )
            for case in cases:
                first_sequence, second_sequence = case
                internal_iterations = (
                    len(first_sequence) * len(second_sequence)
                )
                internal_iteration = 0
                for work1 in first_sequence:
                    for work2 in second_sequence:
                        if self.show_progress:
                            self._calc_and_print_progress(
                                iteration,  # type: ignore
                                iterations,  # type: ignore
                                internal_iteration,
                                internal_iterations
                            )
                            internal_iteration += 1

                        self._do_step(work1, work2)
                if self.show_progress:
                    iteration += 1  # type: ignore

        self.features_getter.logger.debug(f'Time for all {perf_counter() - begin_time:.2f} s')
        self.features_getter.logger.info("Ending searching for plagiarism.")

    def run(self) -> None:
        self.logger.debug("Starting codeplag util")

        if self.root == "settings":
            if self.command == "show":
                self._settings_show()
                return
            elif self.command == "modify":
                self._settings_modify()
                self._settings_show()
                return
        else:
            self._check()

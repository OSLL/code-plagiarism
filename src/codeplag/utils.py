import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import List, Optional

import argcomplete
import numpy as np
from decouple import Config, RepositoryEnv

from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.codeplagcli import CodeplagCLI
from codeplag.consts import GET_FRAZE, LOG_PATH, SUPPORTED_EXTENSIONS
from codeplag.display import print_compare_result
from codeplag.getfeatures import FeaturesGetter
from codeplag.logger import get_logger
from codeplag.types import (ASTFeatures, CompareInfo, FastMetrics,
                            StructuresInfo, WorksReport)
from webparsers.github_parser import GitHubParser


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
    if (fast_metrics.weighted_average * 100) < threshold:
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


class CodeplagEngine(FeaturesGetter):

    def __init__(self, logger: logging.Logger, args: List[str] = None) -> None:
        self.parser = CodeplagCLI()
        argcomplete.autocomplete(self.parser)

        if args is None:
            args = sys.argv[1:]

        parsed_args = vars(self.parser.parse_args(args))
        super(CodeplagEngine, self).__init__(
            extension=parsed_args.pop('extension'), logger=logger
        )

        self.mode: str = parsed_args.pop('mode', 'many_to_many')
        self.show_progress: bool = parsed_args.pop('show_progress', False)
        self.threshold: int = parsed_args.pop('threshold', 65)
        self.reports_directory: Optional[Path] = parsed_args.pop(
            'reports_directory', None
        )

        self.github_files: List[str] = parsed_args.pop('github_files', [])
        self.github_project_folders: List[str] = parsed_args.pop(
            'github_project_folders', []
        )
        self.github_user: str = parsed_args.pop('github_user', '')
        self._set_access_token(parsed_args.pop('environment', None))
        self._set_github_parser(parsed_args.pop('all_branches', False))
        self.regexp: str = parsed_args.pop('regexp', '')

        self.files: List[Path] = parsed_args.pop('files', [])
        self.directories: List[Path] = parsed_args.pop('directories', [])

        self.works: List[ASTFeatures] = []

    def _set_access_token(self, env_path: Optional[Path]) -> None:
        if not env_path:
            self.logger.warning(
                "Env file not found or not a file. "
                "Trying to get token from environment."
            )
            self._access_token: str = os.environ.get('ACCESS_TOKEN', '')
        else:
            env_config = Config(RepositoryEnv(env_path))
            self._access_token: str = env_config.get('ACCESS_TOKEN', default='')

        if not self._access_token:
            self.logger.warning('GitHub access token is not defined.')

    def _set_github_parser(self, branch_policy: bool) -> None:
        if any(
            [
                self.github_files,
                self.github_project_folders,
                self.github_user
            ]
        ):
            self.github_parser = GitHubParser(
                file_extensions=SUPPORTED_EXTENSIONS[
                    self.extension
                ],
                check_policy=branch_policy,
                access_token=self._access_token,
                logger=get_logger('webparsers', LOG_PATH)
            )

    def get_works_from_github_files(self) -> None:
        if self.github_files:
            self.logger.info(f"{GET_FRAZE} GitHub urls")
        for github_file in self.github_files:
            file_content = self.github_parser.get_file_from_url(github_file)[0]
            self.works.append(
                self.get_features_from_content(
                    file_content, github_file
                )
            )

    def get_works_from_github_project_folders(self) -> None:
        for github_project in self.github_project_folders:
            self.logger.info(f'{GET_FRAZE} {github_project}')
            gh_prj_files = self.github_parser.get_files_generator_from_dir_url(
                github_project
            )
            for file_content, url_file in gh_prj_files:
                self.works.append(
                    self.get_features_from_content(
                        file_content, url_file
                    )
                )

    def get_works_from_users_repos(self) -> None:
        if not self.github_user:
            return

        repos = self.github_parser.get_list_of_repos(
            owner=self.github_user,
            reg_exp=self.regexp
        )
        for repo in repos:
            self.logger.info(f'{GET_FRAZE} {repo.html_url}')
            files = self.github_parser.get_files_generator_from_repo_url(
                repo.html_url
            )
            for file_content, url_file in files:
                self.works.append(
                    self.get_features_from_content(
                        file_content, url_file
                    )
                )

    def save_result(self,
                    first_work: ASTFeatures,
                    second_work: ASTFeatures,
                    metrics: CompareInfo) -> None:
        if not self.reports_directory.is_dir():
            self.logger.warning(
                "Provided folder for reports now is not exists."
            )
            return

        struct_info_dict = metrics.structure._asdict()
        struct_info_dict['compliance_matrix'] = (
            struct_info_dict['compliance_matrix'].tolist()
        )
        report = WorksReport(
            date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            first_path=first_work.filepath.__str__(),
            second_path=second_work.filepath.__str__(),
            first_heads=first_work.head_nodes,
            second_heads=second_work.head_nodes,
            fast=metrics.fast._asdict(),
            structure=struct_info_dict
        )

        try:
            report_file = self.reports_directory / f'{uuid.uuid4().hex}.json'
            with open(report_file, 'w', encoding='utf-8') as file:
                file.write(json.dumps(report))
        except PermissionError:
            self.logger.warning(
                "Not enough rights to write reports to the folder."
            )

    def run(self) -> None:
        self.logger.debug("Starting codeplag util")

        self.logger.debug(
            f"Mode: {self.mode}; "
            f"Extension: {self.extension}."
        )

        begin_time = perf_counter()

        features_from_files = self.get_features_from_files(self.files)
        features_from_dirs = self.get_works_from_dirs(self.directories)
        self.get_works_from_github_files()
        self.get_works_from_github_project_folders()
        self.get_works_from_users_repos()

        self.logger.info("Starting searching for plagiarism")
        if self.mode == 'many_to_many':
            self.works.extend(features_from_files)
            self.works.extend(features_from_dirs)

            count_works = len(self.works)
            iterations = int((count_works * (count_works - 1)) / 2)
            iteration = 0
            for i, work1 in enumerate(self.works):
                for j, work2 in enumerate(self.works):
                    if i <= j:
                        continue

                    if self.show_progress:
                        iteration += 1
                        print(
                            f"Check progress: {iteration / iterations:.2%}.",
                            end='\r'
                        )

                    metrics = compare_works(
                        work1,
                        work2,
                        self.threshold
                    )
                    if not metrics.structure:
                        continue

                    print_compare_result(
                        work1,
                        work2,
                        metrics,
                        self.threshold
                    )
                    if self.reports_directory:
                        self.save_result(
                            work1,
                            work2,
                            metrics
                        )
        elif self.mode == 'one_to_one':
            # TODO
            pass

        self.logger.debug(f'Time for all {perf_counter() - begin_time:.2f} s')
        self.logger.info("Ending searching for plagiarism.")

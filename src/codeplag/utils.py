import logging
import os
import re
import sys
from time import perf_counter
from typing import List, Tuple, NamedTuple

import argcomplete
import numpy as np
import pandas as pd
from decouple import Config, RepositoryEnv

from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.astfeatures import ASTFeatures
from codeplag.codeplagcli import CodeplagCLI
from codeplag.consts import FILE_DOWNLOAD_PATH, SUPPORTED_EXTENSIONS
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import get_features as get_features_cpp
from codeplag.cplag.util import \
    get_cursor_from_file as get_cursor_from_file_cpp
from codeplag.cplag.util import \
    get_works_from_filepaths as get_works_from_filepaths_cpp
from codeplag.pyplag.utils import \
    get_ast_from_content as get_ast_from_content_py
from codeplag.pyplag.utils import \
    get_features_from_ast as get_features_from_ast_py
from codeplag.pyplag.utils import \
    get_works_from_filepaths as get_works_from_filepaths_py
from webparsers.github_parser import GitHubParser


GET_FRAZE = 'Getting works features from'


class FastMetrics(NamedTuple):
    jakkar: float
    operators: float
    keywords: float
    literals: float
    weighted_average: float


class StructuresInfo(NamedTuple):
    similarity: float
    compliance_matrix: np.array


class CompareInfo(NamedTuple):
    fast: FastMetrics
    structure: StructuresInfo = None


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


def print_compare_result(features1: ASTFeatures,
                         features2: ASTFeatures,
                         compare_info: CompareInfo,
                         threshold: int = 60) -> None:
    """The function prints the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @compare_info - structure consist compare metrics of two works
    @threshold - threshold of plagiarism searcher alarm
    """

    print(" " * 40)
    print('+' * 40)
    print(
        'May be similar:',
        features1.filepath,
        features2.filepath,
        end='\n\n', sep='\n'
    )
    main_metrics_df = pd.DataFrame(
        [compare_info.fast], index=['Similarity'],
        columns=pd.Index(
            (field.upper() for field in compare_info.fast._fields),
            name='FastMetrics:'
        )
    )
    print(main_metrics_df)
    print()

    additional_metrics_df = pd.DataFrame(
        compare_info.structure.similarity, index=['Similarity'],
        columns=pd.Index(
            ['Structure'],
            name='AdditionalMetrics:'
        )
    )
    print(additional_metrics_df)
    print()

    if (compare_info.structure.similarity * 100) > threshold:
        data = np.zeros(
            (
                compare_info.structure.compliance_matrix.shape[0],
                compare_info.structure.compliance_matrix.shape[1]
            ),
            dtype=np.float64
        )
        for row in range(
            compare_info.structure.compliance_matrix.shape[0]
        ):
            for col in range(
                compare_info.structure.compliance_matrix.shape[1]
            ):
                data[row][col] = (
                    compare_info.structure.compliance_matrix[row][col][0] /
                    compare_info.structure.compliance_matrix[row][col][1]
                )
        compliance_matrix_df = pd.DataFrame(
            data=data,
            index=features1.head_nodes,
            columns=features2.head_nodes
        )

        print(compliance_matrix_df, '\n')

    print('+' * 40)


def get_files_path_from_directory(directory: str,
                                  extensions: list = None) -> List[str]:
    '''
        The function returns paths to all files in the directory
        and its subdirectories which have the extension transmitted
        in arguments
    '''
    if not extensions:
        extensions = SUPPORTED_EXTENSIONS['default']

    allowed_files = []
    for current_dir, _folders, files in os.walk(directory):
        for file in files:
            allowed = False
            for extension in extensions:
                if re.search(extension, file):
                    allowed = True

                    break
            if allowed:
                allowed_files.append(os.path.join(current_dir, file))

    return allowed_files


def print_suspect_parts(source_code: str,
                        marked_tokens: List[int],
                        tokens_pos: List[Tuple[int, int]],
                        color: str = Colors.FAIL) -> None:
    ROWS = {
        row for (row, _column) in
        [tokens_pos[index] for index in marked_tokens]
    }

    row = 1
    column = 1

    for symbol in source_code:
        if symbol == '\n':
            row += 1
            column = 1

        if row in ROWS:
            print(color + symbol, end=Colors.ENDC)

        column += 1


def print_code_and_highlight_suspect(source_code: str,
                                     marked_tokens: List[int],
                                     tokens_pos: List[Tuple[int, int]],
                                     color=Colors.FAIL) -> None:
    ROWS = {row for (row, column) in
            [tokens_pos[index] for index in marked_tokens]}

    row = 1
    column = 1

    for symbol in source_code:
        if symbol == '\n':
            row += 1
            column = 1

        if row in ROWS:
            print(color + symbol, end=Colors.ENDC)
        else:
            print(symbol, end="")

        column += 1


class CodeplagEngine:

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

        self.parser = CodeplagCLI()
        argcomplete.autocomplete(self.parser)

    def set_access_token(self, env_path: str) -> None:
        if not env_path:
            self.logger.warning(
                "Env file not found or not a file. "
                "Trying to get token from environment."
            )
            self.access_token = os.environ.get('ACCESS_TOKEN', '')
        else:
            env_config = Config(RepositoryEnv(env_path))
            self.access_token = env_config.get('ACCESS_TOKEN', default='')

        if not self.access_token:
            self.logger.warning('GitHub access token is not defined.')

    def append_work_features(self,
                             file_content: str,
                             url_to_file: str) -> None:
        if self.extension == 'py':
            tree = get_ast_from_content_py(file_content, url_to_file)
            features = get_features_from_ast_py(tree, url_to_file)
            self.works.append(features)
        elif self.extension == 'cpp':
            with open(FILE_DOWNLOAD_PATH, 'w', encoding='utf-8') as out_file:
                out_file.write(file_content)
            cursor = get_cursor_from_file_cpp(FILE_DOWNLOAD_PATH, COMPILE_ARGS)
            features = get_features_cpp(cursor, FILE_DOWNLOAD_PATH)
            os.remove(FILE_DOWNLOAD_PATH)
            features.filepath = url_to_file
            self.works.append(features)

    def get_works_from_files(self, files: List[str]) -> None:
        if not files:
            return

        self.logger.info(f'{GET_FRAZE} files')
        if self.extension == 'py':
            self.works.extend(get_works_from_filepaths_py(files))
        elif self.extension == 'cpp':
            self.works.extend(
                get_works_from_filepaths_cpp(
                    files,
                    COMPILE_ARGS
                )
            )

    def get_works_from_dirs(self, dirs: List[str]) -> None:
        for dir in dirs:
            self.logger.info(f'{GET_FRAZE} {dir}')
            filepaths = get_files_path_from_directory(
                dir,
                extensions=SUPPORTED_EXTENSIONS[self.extension]
            )
            if self.extension == 'py':
                self.works.extend(
                    get_works_from_filepaths_py(filepaths)
                )
            elif self.extension == 'cpp':
                self.works.extend(
                    get_works_from_filepaths_cpp(
                        filepaths,
                        COMPILE_ARGS
                    )
                )

    def get_works_from_github_files(self,
                                    github_files: List[str]) -> None:
        if github_files:
            self.logger.info(f"{GET_FRAZE} GitHub urls")
        for github_file in github_files:
            file_content = self.github_parser.get_file_from_url(github_file)[0]
            self.append_work_features(file_content, github_file)

    def get_works_from_github_project_folders(
            self,
            github_projects: List[str]) -> None:
        for github_project in github_projects:
            self.logger.info(f'{GET_FRAZE} {github_project}')
            gh_prj_files = self.github_parser.get_files_generator_from_dir_url(
                github_project
            )
            for file_content, url_file in gh_prj_files:
                self.append_work_features(file_content, url_file)

    def get_works_from_users_repos(self,
                                   github_user: str,
                                   reg_exp: str) -> None:
        if not github_user:
            return

        repos = self.github_parser.get_list_of_repos(
            owner=github_user,
            reg_exp=reg_exp
        )
        for repo_url in repos.values():
            self.logger.info(f'{GET_FRAZE} {repo_url}')
            files = self.github_parser.get_files_generator_from_repo_url(
                repo_url
            )
            for file_content, url_file in files:
                self.append_work_features(file_content, url_file)

    def run(self, args: List[str] = None) -> None:
        self.logger.debug("Starting codeplag util")

        if args is None:
            args = sys.argv[1:]

        parsed_args = vars(self.parser.parse_args(args))
        self.set_access_token(parsed_args.get('environment'))
        self.extension = parsed_args.get('extension')

        self.logger.debug(
            f"Mode: {parsed_args['mode']}; "
            f"Extension: {parsed_args['extension']}."
        )

        begin_time = perf_counter()

        if parsed_args.get('mode') == 'many_to_many':
            self.works = []
            self.github_parser = GitHubParser(
                file_extensions=SUPPORTED_EXTENSIONS[
                    self.extension
                ],
                check_policy=parsed_args.get('all_branches'),
                access_token=self.access_token
            )

            self.get_works_from_files(parsed_args.get('files'))
            self.get_works_from_dirs(parsed_args.get('directories'))
            self.get_works_from_github_files(
                parsed_args.get('github_files')
            )
            self.get_works_from_github_project_folders(
                parsed_args.get('github_project_folders')
            )
            self.get_works_from_users_repos(
                parsed_args.get('github_user'),
                parsed_args.get('regexp')
            )

            self.logger.info("Starting searching for plagiarism")
            count_works = len(self.works)
            iterations = int((count_works * (count_works - 1)) / 2)
            iteration = 1
            for i, work1 in enumerate(self.works):
                for j, work2 in enumerate(self.works):
                    if i <= j:
                        continue

                    if parsed_args.get('show_progress'):
                        print(
                            f"Check progress: {iteration / iterations:.2%}.",
                            end='\r'
                        )

                    metrics = compare_works(
                        work1,
                        work2,
                        parsed_args.get('threshold')
                    )
                    if metrics.structure:
                        print_compare_result(
                            work1,
                            work2,
                            metrics,
                            parsed_args.get('threshold')
                        )

                    iteration += 1

        self.logger.debug(f'Time for all {perf_counter() - begin_time:.2f} s')
        self.logger.info("Ending searching for plagiarism.")

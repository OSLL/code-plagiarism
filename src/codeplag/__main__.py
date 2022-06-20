import os
import pandas as pd

from time import perf_counter
from decouple import Config, RepositoryEnv

from webparsers.github_parser import GitHubParser
from codeplag.logger import get_logger
from codeplag.consts import (
    FILE_DOWNLOAD_PATH, LOG_PATH, SUPPORTED_EXTENSIONS
)
from codeplag.cplag.const import COMPILE_ARGS
from codeplag.codeplagcli import get_parser
from codeplag.utils import (
    get_files_path_from_directory,
    compare_works
)
from codeplag.pyplag.utils import (
    get_works_from_filepaths as get_works_from_filepaths_py,
    get_ast_from_content as get_ast_from_content_py,
    get_features_from_ast as get_features_from_ast_py
)
from codeplag.cplag.util import (
    get_cursor_from_file as get_cursor_from_file_cpp,
    get_works_from_filepaths as get_works_from_filepaths_cpp
)
from codeplag.cplag.tree import (
    get_features as get_features_cpp
)


def append_work_features_py(file_content, url_to_file, works):
    tree = get_ast_from_content_py(file_content, url_to_file)
    features = get_features_from_ast_py(tree, url_to_file)
    works.append(features)


def append_work_features_cpp(file_content, url_to_file, works):
    with open(FILE_DOWNLOAD_PATH, 'w') as out_file:
        out_file.write(file_content)
    cursor = get_cursor_from_file_cpp(FILE_DOWNLOAD_PATH, COMPILE_ARGS)
    features = get_features_cpp(cursor, FILE_DOWNLOAD_PATH)
    os.remove(FILE_DOWNLOAD_PATH)
    features.filepath = url_to_file
    works.append(features)


def run(logger):
    logger.debug("Starting codeplag util")

    parser = get_parser()
    args = vars(parser.parse_args())

    logger.debug(
        "Mode: {}; Extension: {}; Environment path: {}.".format(
            args['mode'],
            args['extension'],
            args['environment']
        )
    )

    MODE = args.pop('mode')
    ENVIRONMENT = args.pop('environment')
    EXTENSION = args.pop('extension')
    THRESHOLD = args.pop('threshold')
    SHOW_PROGRESS = args.pop('show_progress')
    BRANCH_POLICY = args.pop('all_branches')
    REG_EXP = args.pop('regexp')
    FILES = args.pop('files')
    DIRECTORIES = args.pop('directories')
    GITHUB_FILES = args.pop('github_files')
    GITHUB_PROJECT_FOLDERS = args.pop('github_project_folders')
    GITHUB_USER = args.pop('github_user')

    if ENVIRONMENT:
        env_config = Config(RepositoryEnv(ENVIRONMENT))
        ACCESS_TOKEN = env_config.get('ACCESS_TOKEN', default='')
        if not ACCESS_TOKEN:
            logger.debug('GitHub access token is not defined.')
    else:
        ACCESS_TOKEN = ''

    begin_time = perf_counter()
    if MODE == 'many_to_many':
        works = []
        gh = GitHubParser(
            file_extensions=SUPPORTED_EXTENSIONS[EXTENSION],
            check_policy=BRANCH_POLICY,
            access_token=ACCESS_TOKEN
        )
        if EXTENSION == 'py':
            if FILES:
                logger.info("Getting works features from files")
                works.extend(get_works_from_filepaths_py(FILES))

            for directory in DIRECTORIES:
                logger.info('Getting works features from {}'.format(directory))
                filepaths = get_files_path_from_directory(
                    directory,
                    extensions=SUPPORTED_EXTENSIONS[EXTENSION]
                )
                works.extend(get_works_from_filepaths_py(filepaths))

            if GITHUB_FILES:
                logger.info("Getting GitHub files from urls")
            for github_file in GITHUB_FILES:
                file_content = gh.get_file_from_url(github_file)[0]
                append_work_features_py(file_content, github_file, works)

            for github_project in GITHUB_PROJECT_FOLDERS:
                logger.info('Getting works features from {}'.format(github_project))
                github_project_files = gh.get_files_generator_from_dir_url(github_project)
                for file_content, url_file in github_project_files:
                    append_work_features_py(file_content, url_file, works)

            if GITHUB_USER:
                repos = gh.get_list_of_repos(owner=GITHUB_USER,
                                             reg_exp=REG_EXP)
                for repo, repo_url in repos.items():
                    logger.info('Getting works features from {}'.format(repo_url))
                    files = gh.get_files_generator_from_repo_url(repo_url)
                    for file_content, url_file in files:
                        append_work_features_py(file_content, url_file, works)
        if EXTENSION == 'cpp':
            if FILES:
                logger.info("Getting works features from files.")
                works.extend(get_works_from_filepaths_cpp(FILES, COMPILE_ARGS))

            for directory in DIRECTORIES:
                logger.info('Getting works features from {}.'.format(directory))
                filepaths = get_files_path_from_directory(
                    directory,
                    extensions=SUPPORTED_EXTENSIONS[EXTENSION]
                )
                works.extend(get_works_from_filepaths_cpp(filepaths, COMPILE_ARGS))

            if GITHUB_FILES:
                logger.info("Getting GitHub files from urls.")
            for github_file in GITHUB_FILES:
                file_content = gh.get_file_from_url(github_file)[0]
                append_work_features_cpp(file_content, github_file, works)

            for github_project in GITHUB_PROJECT_FOLDERS:
                logger.info('Getting works features from {}.'.format(github_project))
                github_project_files = gh.get_files_generator_from_dir_url(github_project)
                for file_content, url_file in github_project_files:
                    append_work_features_cpp(file_content, url_file, works)

            if GITHUB_USER:
                repos = gh.get_list_of_repos(
                    owner=GITHUB_USER,
                    reg_exp=REG_EXP
                )
                for repo, repo_url in repos.items():
                    logger.info('Getting works features from {}.'.format(repo_url))
                    files = gh.get_files_generator_from_repo_url(repo_url)
                    for file_content, url_file in files:
                        append_work_features_cpp(file_content, url_file, works)

        logger.info("Starting searching for plagiarism")
        count_works = len(works)
        iterations = int((count_works * (count_works - 1)) / 2)
        iteration = 1
        for i, work1 in enumerate(works):
            for j, work2 in enumerate(works):
                if i <= j:
                    continue

                if SHOW_PROGRESS:
                    print("Check progress: {:.2%}.".format(iteration / iterations), end='\r')

                compare_works(work1, work2, THRESHOLD)
                iteration += 1

    logger.debug('Time for all {:.2f} s'.format(perf_counter() - begin_time))

    logger.info("Ending searching for plagiarism.")


if __name__ == '__main__':
    pd.options.display.float_format = '{:,.2%}'.format
    logger = get_logger(__name__, LOG_PATH)
    try:
        run(logger)
    except Exception:
        logger.error(
            "An unexpected error occurred while running the utility. "
            f"For getting more information, check file '{LOG_PATH}'."
        )
        logger.debug("Trace:", exc_info=True)

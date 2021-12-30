from time import perf_counter
from decouple import Config, RepositoryEnv

from webparsers.github_parser import GitHubParser
from codeplag.logger import get_logger
from codeplag.consts import LOG_PATH
from codeplag.codeplagcli import get_parser
from codeplag.utils import get_files_path_from_directory
from codeplag.pyplag.utils import (
    get_works_from_filepaths as get_works_from_filepaths_py,
    get_ast_from_content as get_ast_from_content_py,
    get_features_from_ast as get_features_from_ast_py
)


logger = get_logger(__name__, LOG_PATH)
try:
    env_config = Config(RepositoryEnv('./.env'))
except FileNotFoundError:
    logger.debug('The environment file did not define')
else:
    ACCESS_TOKEN = env_config.get('ACCESS_TOKEN', default='')
    if not ACCESS_TOKEN:
        logger.debug('GitHub access token is not defined')


if __name__ == '__main__':
    parser = get_parser()
    args = vars(parser.parse_args())

    logger.info("Starting searching for plagiarism")
    logger.debug("Mode: {}; Extension: {}".format(args['mode'], args['extension']))

    MODE = args.pop('mode')
    EXTENSION = args.pop('extension')
    THRESHOLD = args.pop('threshold')
    BRANCH_POLICY = args.pop('all_branches')
    REG_EXP = args.pop('regexp')

    begin_time = perf_counter()
    if MODE == 'many_to_many':
        works = []
        if EXTENSION == 'py':
            gh = GitHubParser(file_extensions=[EXTENSION], check_policy=BRANCH_POLICY,
                              access_token=ACCESS_TOKEN)

            works.extend(get_works_from_filepaths_py(args.get('files')))
            for directory in args.get('directories'):
                filepaths = get_files_path_from_directory(directory, extensions=[r".py\b"])
                works.extend(get_works_from_filepaths_py(filepaths))

            for github_file in args.get('github_files'):
                tree = get_ast_from_content_py(gh.get_file_from_url(github_file)[0],
                                               github_file)
                features = get_features_from_ast_py(tree, github_file)
                works.append(features)
            # TODO git_user, git_project
        # TODO cpp/c

        print(works)

    logger.debug('Time for all {:.2f} s'.format(perf_counter() - begin_time))

    logger.info("Ending searching for plagiarism")

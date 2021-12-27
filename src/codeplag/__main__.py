from time import perf_counter
from codeplag.logger import get_logger
from codeplag.consts import LOG_PATH
from codeplag.codeplagcli import get_parser
from codeplag.pyplag.utils import (
    get_ast_from_filename, get_features_from_ast
)

logger = get_logger(__name__, LOG_PATH)


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
            for file in (args.get('files') if args.get('files') else []):
                tree = get_ast_from_filename(file)
                features = get_features_from_ast(tree, file)
                works.append(features)

        print(works)

    logger.debug('Time for all {:.2f} m'.format((perf_counter() - begin_time) / 60))

    logger.info("Ending searching for plagiarism")

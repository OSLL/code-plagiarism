from time import perf_counter

from codeplag.logger import get_logger
from codeplag.consts import LOG_PATH
from codeplag.codeplagcli import get_parser
from codeplag.utils import get_files_path_from_directory
from codeplag.pyplag.utils import (
    get_works_from_filepaths as get_works_from_filepaths_py
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
            works.extend(get_works_from_filepaths_py(args.get('files')))
            for directory in (args.get('directories') if args.get('directories') else []):
                filepaths = get_files_path_from_directory(directory, extensions=[r".py\b"])
                works.extend(get_works_from_filepaths_py(filepaths))

        print(works)

    logger.debug('Time for all {:.2f} s'.format(perf_counter() - begin_time))

    logger.info("Ending searching for plagiarism")

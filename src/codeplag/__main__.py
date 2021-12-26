from time import perf_counter
from codeplag.logger import get_logger
from codeplag.codeplagcli import get_parser
from codeplag.consts import LOG_PATH


logger = get_logger(__name__, LOG_PATH)


if __name__ == '__main__':
    parser = get_parser()
    parser.parse_args()

    logger.info("Starting searching for plagiarism")

    begin_time = perf_counter()
    logger.debug('Time for all {:.2f} m'.format((perf_counter() - begin_time) / 60))

    logger.info("Ending searching for plagiarism")

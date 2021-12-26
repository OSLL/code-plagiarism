import logging


def get_file_handler(filename):
    log_format = ('%(asctime)s - [%(levelname)s] - %(name)s - '
                   + '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')
    log_arguments = {
                       'fmt': log_format,
                       'datefmt': '%b %-d %T'
                    }
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(**log_arguments))

    return file_handler


def get_stream_handler():
    log_format = ('%(asctime)s - [%(levelname)s] - %(message)s')
    log_arguments = {
                       'fmt': log_format,
                       'datefmt': '%b %-d %T'
                    }
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(**log_arguments))

    return stream_handler


def get_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(filename))
    logger.addHandler(get_stream_handler())

    return logger

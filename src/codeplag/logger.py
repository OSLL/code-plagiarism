import logging

_log_format = ('%(asctime)s - [%(levelname)s] - %(name)s - '
               + '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')
_log_arguments = {
                    'fmt': _log_format,
                    'datefmt': '%Y-%m-%d,%H:%M:%S'
                 }


def get_file_handler(filename):
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(**_log_arguments))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(logging.Formatter(**_log_arguments))
    return stream_handler


def get_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler(filename))
    logger.addHandler(get_stream_handler())
    return logger

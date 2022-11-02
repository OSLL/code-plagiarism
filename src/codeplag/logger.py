import logging
import sys
from pathlib import Path


def get_file_handler(filename: Path) -> logging.FileHandler:
    log_format = (
        '%(asctime)s - [%(levelname)s] - %(name)s - '
        '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
    )
    log_arguments = {
        'fmt': log_format,
        'datefmt': '%b %-d %T'
    }
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(**log_arguments))

    return file_handler


def get_stream_handler() -> logging.StreamHandler:
    log_format = ('%(levelname)s: %(message)s')
    log_arguments = {
        'fmt': log_format,
        'datefmt': '%b %-d %T'
    }
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(**log_arguments))

    return stream_handler


def get_logger(name: str, filename: Path) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(filename))
    logger.addHandler(get_stream_handler())

    return logger

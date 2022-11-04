import logging
import sys
from pathlib import Path

from codeplag.display import error, info, red_bold, warning


class StreamFormatter(logging.Formatter):

    FORMATS = {
        logging.INFO: info,
        logging.WARNING: warning,
        logging.ERROR: error,
        logging.CRITICAL: red_bold
    }

    def __init__(self):
        self._level_fmt = '[%(levelname)s]'
        self._log_fmt = ' %(asctime)s - %(message)s'
        super().__init__(datefmt='%H:%M')

    def format(self, record: logging.LogRecord) -> str:
        self._style._fmt = self.FORMATS.get(
            record.levelno, info
        )(self._level_fmt) + self._log_fmt

        return super().format(record)


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
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(StreamFormatter())

    return stream_handler


def get_logger(name: str, filename: Path) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(filename))
    logger.addHandler(get_stream_handler())

    return logger

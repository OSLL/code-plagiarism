import logging
import sys
from pathlib import Path

from codeplag.display import error, info, red_bold, warning


class StreamFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: info,
        logging.WARNING: warning,
        logging.ERROR: error,
        logging.CRITICAL: red_bold,
    }

    def __init__(self):
        self._level_fmt = "[%(levelname)s]"
        self._log_fmt = " %(asctime)s - %(message)s"
        super().__init__(datefmt="%H:%M")

    def format(self, record: logging.LogRecord) -> str:
        self._style._fmt = (
            self.FORMATS.get(record.levelno, info)(self._level_fmt) + self._log_fmt
        )

        return super().format(record)


def get_file_handler(filename: Path) -> logging.FileHandler:
    log_format = (
        "%(asctime)s - [%(levelname)s] - %(name)s - "
        "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    )
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            fmt=log_format,
            datefmt="%b %-d %T",
        )
    )

    return file_handler


def get_stderr_handler() -> logging.StreamHandler:
    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(StreamFormatter())

    return stderr_handler


def get_stdout_handler() -> logging.StreamHandler:
    class STDOutFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno in [logging.INFO, logging.DEBUG]

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(STDOutFilter())
    stdout_handler.setFormatter(StreamFormatter())

    return stdout_handler


def get_logger(name: str, filename: Path, verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(get_file_handler(filename))
    logger.addHandler(get_stdout_handler())
    logger.addHandler(get_stderr_handler())

    return logger

import logging
import sys
from pathlib import Path

from typing_extensions import Self

from codeplag.consts import DEFAULT_LOG_LEVEL, UTIL_NAME
from codeplag.display import clear_line, error, info, red_bold, warning
from codeplag.types import LogLevel


class StreamFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: info,
        logging.WARNING: warning,
        logging.ERROR: error,
        logging.CRITICAL: red_bold,
    }

    def __init__(self: Self) -> None:
        self._level_fmt = "[%(levelname)s]"
        self._log_fmt = " %(asctime)s - %(message)s"
        super().__init__(datefmt="%H:%M")

    def format(self: Self, record: logging.LogRecord) -> str:
        self._style._fmt = self.FORMATS.get(record.levelno, info)(self._level_fmt) + self._log_fmt

        return super().format(record)


class CustomStreamHandler(logging.StreamHandler):
    def emit(self: Self, record: logging.LogRecord) -> None:
        clear_line()
        super(CustomStreamHandler, self).emit(record)


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


def get_stderr_handler() -> CustomStreamHandler:
    stderr_handler = CustomStreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(StreamFormatter())

    return stderr_handler


def get_stdout_handler() -> CustomStreamHandler:
    class STDOutFilter(logging.Filter):
        def filter(self: Self, record: logging.LogRecord) -> bool:
            return record.levelno in [logging.INFO, logging.DEBUG]

    stdout_handler = CustomStreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(STDOutFilter())
    stdout_handler.setFormatter(StreamFormatter())

    return stdout_handler


def set_handlers(
    logger: logging.Logger, filename: Path, log_level: LogLevel = DEFAULT_LOG_LEVEL
) -> None:
    levelno = getattr(logging, log_level.upper())
    logger.setLevel(levelno)
    logger.addHandler(get_file_handler(filename))
    if levelno in [logging.INFO, logging.DEBUG]:
        logger.addHandler(get_stdout_handler())
    logger.addHandler(get_stderr_handler())


def log_err(*msgs: str) -> None:
    for msg in msgs:
        codeplag_logger.error(msg)


codeplag_logger = logging.getLogger(UTIL_NAME)

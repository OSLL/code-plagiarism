import os
import re
from pathlib import Path
from typing import Final, get_args

from codeplag.types import (
    Extension,
    Extensions,
    Language,
    LogLevel,
    MaxDepth,
    Mode,
    NgramsLength,
    ReportsExtension,
    ReportType,
    Threshold,
)

UTIL_NAME: Final[str] = "@UTIL_NAME@"
UTIL_VERSION: Final[str] = "@UTIL_VERSION@"

# Paths
CONFIG_PATH: Final[Path] = Path("@CONFIG_PATH@")
LOG_PATH: Final[Path] = Path("@CODEPLAG_LOG_PATH@")
LIB_PATH: Final[Path] = Path("@LIB_PATH@")
GENERAL_TEMPLATE_PATH: Final[Path] = LIB_PATH / "general.templ"
SOURCES_TEMPLATE_PATH: Final[Path] = LIB_PATH / "sources.templ"
TRANSLATIONS_PATH: Final[Path] = LIB_PATH / "translations"
# =====

# Default values
DEFAULT_THRESHOLD: Final[Threshold] = 65
DEFAULT_NGRAMS_LENGTH: Final[NgramsLength] = 3
DEFAULT_WEIGHTS: Final[tuple[float, float, float, float]] = (1.0, 0.4, 0.4, 0.4)
DEFAULT_LANGUAGE: Final[Language] = "en"
DEFAULT_LOG_LEVEL: Final[LogLevel] = "info"
DEFAULT_REPORT_EXTENSION: Final[ReportsExtension] = "csv"
DEFAULT_GENERAL_REPORT_NAME: Final[str] = "report.html"
DEFAULT_SOURCES_REPORT_NAME: Final[str] = "sources.html"
DEFAULT_WORKERS: Final[int] = os.cpu_count() or 1
DEFAULT_MODE: Final[Mode] = "many_to_many"
DEFAULT_MAX_DEPTH: Final[MaxDepth] = 999
DEFAULT_REPORT_TYPE: Final[ReportType] = "general"
DEFAULT_MONGO_HOST: Final[str] = "host.docker.internal"
DEFAULT_MONGO_USER: Final[str] = "root"
DEFAULT_MONGO_PASS: Final[str] = "example"
DEFAULT_MONGO_PORT: Final[int] = 27017
# =============

GET_FRAZE: Final[str] = "Getting works features from"

# CSV report
CSV_REPORT_FILENAME: Final[str] = f"{UTIL_NAME}_report.csv"
CSV_SAVE_TICK_SEC: Final[int] = 60
CSV_REPORT_COLUMNS: Final[tuple[str, ...]] = (
    "date",
    "first_modify_date",
    "first_sha256",
    "second_modify_date",
    "second_sha256",
    "first_path",
    "second_path",
    "first_heads",
    "second_heads",
    "jakkar",
    "operators",
    "keywords",
    "literals",
    "weighted_average",
    "struct_similarity",
    "compliance_matrix",
)

# Choices
MODE_CHOICE: Final[tuple[Mode, ...]] = get_args(Mode)
REPORTS_EXTENSION_CHOICE: Final[tuple[ReportsExtension, ...]] = get_args(ReportsExtension)
EXTENSION_CHOICE: Final[tuple[Extension, ...]] = get_args(Extension)
LANGUAGE_CHOICE: Final[tuple[Language, ...]] = get_args(Language)
LOG_LEVEL_CHOICE: Final[tuple[LogLevel, ...]] = get_args(LogLevel)
WORKERS_CHOICE: Final[tuple[int, ...]] = tuple(range(1, DEFAULT_WORKERS + 1))
MAX_DEPTH_CHOICE: Final[tuple[int, ...]] = get_args(MaxDepth)
NGRAMS_LENGTH_CHOICE: Final[tuple[int, ...]] = get_args(NgramsLength)
REPORT_TYPE_CHOICE: Final[tuple[ReportType, ...]] = get_args(ReportType)
# =======

ALL_EXTENSIONS: Final[tuple[re.Pattern]] = (re.compile(r"\..*$"),)
# Don't  checks changing values by key
SUPPORTED_EXTENSIONS: Final[dict[Extension, Extensions]] = {
    "py": (re.compile(r"\.py$"),),
    "cpp": (re.compile(r"\.cpp$"), re.compile(r"\.c$"), re.compile(r"\.h$")),
}

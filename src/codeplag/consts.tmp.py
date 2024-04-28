import os
import re
from pathlib import Path
from typing import Dict, Final, List, Tuple, get_args

from codeplag.types import (
    Extension,
    Extensions,
    Language,
    Mode,
    ReportsExtension,
    Threshold,
)

UTIL_NAME: Final[str] = "@UTIL_NAME@"
UTIL_VERSION: Final[str] = "@UTIL_VERSION@"

# Paths
CONFIG_PATH: Final[Path] = Path("@CONFIG_PATH@")
FILE_DOWNLOAD_PATH: Final[Path] = Path(f"/tmp/{UTIL_NAME}_download.out")
LOG_PATH: Final[Path] = Path("@CODEPLAG_LOG_PATH@")
TEMPLATE_PATH: Final[Dict[Language, Path]] = {
    "ru": Path("@LIB_PATH@/report_ru.templ"),
    "en": Path("@LIB_PATH@/report_en.templ"),
}
# =====

# Default values
DEFAULT_THRESHOLD: Final[Threshold] = 65
DEFAULT_WEIGHTS: Final[Tuple[float, float, float, float]] = (1.0, 0.4, 0.4, 0.4)
DEFAULT_LANGUAGE: Final[Language] = "en"
DEFAULT_REPORT_EXTENSION: Final[ReportsExtension] = "csv"
DEFAULT_GENERAL_REPORT_NAME: Final[str] = "report.html"
DEFAULT_WORKERS: Final[int] = os.cpu_count() or 1
DEFAULT_MODE: Final[Mode] = "many_to_many"
# =============

GET_FRAZE: Final[str] = "Getting works features from"

# CSV report
CSV_REPORT_FILENAME: Final[str] = f"{UTIL_NAME}_report.csv"
CSV_SAVE_TICK_SEC: Final[int] = 60
CSV_REPORT_COLUMNS: Final[Tuple[str, ...]] = (
    "date",
    "first_modify_date",
    "second_modify_date",
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
MODE_CHOICE: Final[Tuple[Mode, ...]] = get_args(Mode)
REPORTS_EXTENSION_CHOICE: Final[Tuple[ReportsExtension, ...]] = get_args(
    ReportsExtension
)
EXTENSION_CHOICE: Final[Tuple[Extension, ...]] = get_args(Extension)
LANGUAGE_CHOICE: Final[Tuple[Language, ...]] = get_args(Language)
WORKERS_CHOICE: Final[List[int]] = list(range(1, DEFAULT_WORKERS + 1))
# =======

ALL_EXTENSIONS: Final[Tuple[re.Pattern]] = (re.compile(r"\..*$"),)
# Don't  checks changing values by key
SUPPORTED_EXTENSIONS: Final[Dict[Extension, Extensions]] = {
    "py": (re.compile(r"\.py$"),),
    "cpp": (re.compile(r"\.cpp$"), re.compile(r"\.c$"), re.compile(r"\.h$")),
}

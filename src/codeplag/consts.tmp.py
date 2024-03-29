import re
from pathlib import Path
from typing import Dict, Final, List, Tuple

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

# Default values
DEFAULT_THRESHOLD: Final[Threshold] = 65
DEFAULT_WEIGHTS: Final[Tuple[float, float, float, float]] = (1.0, 0.4, 0.4, 0.4)
DEFAULT_LANGUAGE: Final[Language] = "en"
DEFAULT_REPORT_EXTENSION: Final[ReportsExtension] = "csv"
DEFAULT_GENERAL_REPORT_NAME: Final[str] = "report.html"

GET_FRAZE: Final[str] = "Getting works features from"

# CSV report
CSV_REPORT_FILENAME: Final[str] = f"{UTIL_NAME}_report.csv"
CSV_SAVE_TICK: Final[int] = 60
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

MODE_CHOICE: Final[List[Mode]] = ["many_to_many", "one_to_one"]
REPORTS_EXTENSION_CHOICE: Final[List[ReportsExtension]] = ["csv", "json"]
EXTENSION_CHOICE: Final[List[Extension]] = ["py", "cpp"]
LANGUAGE_CHOICE: Final[List[Language]] = ["en", "ru"]
ALL_EXTENSIONS: Final[Tuple[re.Pattern]] = (re.compile(r"\..*$"),)
# Don't  checks changing values by key
SUPPORTED_EXTENSIONS: Final[Dict[Extension, Extensions]] = {
    "py": (re.compile(r"\.py$"),),
    "cpp": (re.compile(r"\.cpp$"), re.compile(r"\.c$"), re.compile(r"\.h$")),
}

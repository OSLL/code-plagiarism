import re
from pathlib import Path
from typing import Dict, Final, List, Tuple

from codeplag.types import Extension, Extensions, Mode, Threshold

# Paths
CONFIG_PATH: Final[Path] = Path("@CONFIG_PATH@")
FILE_DOWNLOAD_PATH: Final[Path] = Path("/tmp/@UTIL_NAME@_download.out")
LOG_PATH: Final[Path] = Path("@CODEPLAG_LOG_PATH@")

GET_FRAZE: Final[str] = 'Getting works features from'

DEFAULT_THRESHOLD: Final[Threshold] = 65
MODE_CHOICE: Final[List[Mode]] = ["many_to_many", "one_to_one"]
EXTENSION_CHOICE: Final[List[Extension]] = ["py", "cpp"]
ALL_EXTENSIONS: Final[Tuple[re.Pattern]] = (re.compile(r'\..*$'),)
# Don't  checks changing values by key
SUPPORTED_EXTENSIONS: Final[Dict[Extension, Extensions]] = {
    'py': (
        re.compile(r'\.py$'),
    ),
    'cpp': (
        re.compile(r'\.cpp$'),
        re.compile(r'\.c$'),
        re.compile(r'\.h$')
    ),
}

UTIL_NAME: Final[str] = "@UTIL_NAME@"
UTIL_VERSION: Final[str] = "@UTIL_VERSION@"

import re
from pathlib import Path
from typing import Dict, List

from codeplag.types import Extensions, Mode, Threshold

# Paths
CONFIG_PATH = Path("@CONFIG_PATH@")
FILE_DOWNLOAD_PATH = Path("/tmp/@UTIL_NAME@_download.out")
LOG_PATH = Path("@CODEPLAG_LOG_PATH@")

GET_FRAZE = 'Getting works features from'

DEFAULT_THRESHOLD: Threshold = 65
MODE_CHOICE: List[Mode] = ["many_to_many", "one_to_one"]
SUPPORTED_EXTENSIONS: Dict[str, Extensions] = {
    'py': (
        re.compile(r'\.py$'),
    ),
    'cpp': (
        re.compile(r'\.cpp$'),
        re.compile(r'\.c$'),
        re.compile(r'\.h$')
    ),
    'default': (
        re.compile(r'\..*$'),
    )
}

UTIL_NAME = "@UTIL_NAME@"
UTIL_VERSION = "@UTIL_VERSION@"

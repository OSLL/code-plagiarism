import site
from pathlib import Path

from codeplag.consts import UTIL_NAME

PACKAGE_PATH = Path(site.getsitepackages()[0]) / UTIL_NAME
assert PACKAGE_PATH.exists()


def test_no_py_files():
    for path in PACKAGE_PATH.glob("**/*"):
        if path.is_dir():
            continue
        assert path.suffix == ".so"

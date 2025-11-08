import sys
import tomllib
from typing import Final

with open("pyproject.toml", "rb") as f:
    pyproject_content = tomllib.load(f)

BUILD_REQUIREMENTS: Final = (
    pyproject_content["build-system"]["requires"]
    + pyproject_content["dependency-groups"]["translate"]
    + pyproject_content["dependency-groups"]["man"]
)
LINT_REQUIREMENTS: Final = pyproject_content["dependency-groups"]["lint"]
TEST_REQUIREMENTS: Final = pyproject_content["dependency-groups"]["test"]
INSTALL_REQUIREMENTS: Final = pyproject_content["project"]["dependencies"]


if "--build-requirements" in sys.argv:
    print(" ".join(BUILD_REQUIREMENTS))
    sys.exit(0)
if "--lint-requirements" in sys.argv:
    print(" ".join(LINT_REQUIREMENTS))
    sys.exit(0)
if "--test-requirements" in sys.argv:
    print(" ".join(TEST_REQUIREMENTS))
    sys.exit(0)
if "--install-requirements" in sys.argv:
    print(" ".join(INSTALL_REQUIREMENTS))
    sys.exit(0)
try:
    from Cython.Build import cythonize
    from setuptools import Extension, setup
except ModuleNotFoundError:
    print(
        "For the correct build install required build dependencies: "
        f"'{' '.join(BUILD_REQUIREMENTS)}'."
    )
    sys.exit(1)


setup(
    platforms=["linux"],
    ext_modules=cythonize(
        [
            Extension("*", ["src/codeplag/**/*.py"]),
        ],
        language_level=3,
    ),
)

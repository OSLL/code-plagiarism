import sys
import tomllib

with open("pyproject.toml", "rb") as f:
    pyproject_content = tomllib.load(f)

BUILD_REQUIREMENTS: tuple[str, ...] = (
    "argparse-manpage==4.6",
    "Babel==2.17.0",
    "Cython~=3.0.12",
    "setuptools~=75.8.1",
    "Jinja2~=3.1.5",
)
# fmt: off
LINT_REQUIREMENTS: tuple[str, ...] = (
    "pre-commit~=4.3.0",
)
# fmt: on
TEST_REQUIREMENTS: tuple[str, ...] = (
    "pytest~=8.4.2",
    "pytest-mock~=3.15.1",
    "pytest-cov~=7.0.0",
)


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
    print(" ".join(pyproject_content["project"]["dependencies"]))
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

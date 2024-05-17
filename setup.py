import os
import sys
from pathlib import Path
from typing import Tuple

from setuptools import Extension, find_packages, setup

BUILD_REQUIREMENTS: Tuple[str, ...] = (
    "argparse-manpage==3",
    "Babel==2.15.0",
    "Cython~=3.0.8",
)
INSTALL_REQUIREMENTS: Tuple[str, ...] = (
    "argcomplete~=2.0.0",
    "numpy~=1.23.5",
    "pandas~=1.4.3",
    "ccsyspath~=1.1.0",
    "clang~=16.0.1.1",
    "llvmlite~=0.40.1",
    "libclang~=16.0.0",
    "python-decouple~=3.6",
    "requests~=2.31.0",
    "typing-extensions~=4.3.0",
    "aiohttp~=3.9.3",
    "Jinja2~=3.1.2",
    "cachetools==5.3.1",
    "gidgethub~=5.3.0",
)
UTIL_NAME = os.getenv("UTIL_NAME")
UTIL_VERSION = os.getenv("UTIL_VERSION")


if "--build-requirements" in sys.argv:
    print(" ".join(BUILD_REQUIREMENTS))
    sys.exit(0)
elif "--install-requirements" in sys.argv:
    print(" ".join(INSTALL_REQUIREMENTS))
    sys.exit(0)
elif UTIL_NAME is None or UTIL_VERSION is None:
    print("Please provide UTIL_NAME and UTIL_VERSION environment variables.")
    sys.exit(1)
try:
    from Cython.Build import cythonize
except ModuleNotFoundError:
    print(
        "For the correct build install required build dependencies: "
        f"'{' '.join(BUILD_REQUIREMENTS)}'."
    )
    sys.exit(1)


setup(
    name=f"{UTIL_NAME}",
    version=f"{UTIL_VERSION}",
    description="Code plagiarism searching package",
    author="Artyom Semidolin, Dmitry Nikolaev, Alexander Evsikov",
    url="https://github.com/OSLL/code-plagiarism",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="MIT License",
    platforms=["linux"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Plagiarism Detection",
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    ext_modules=cythonize(
        [
            Extension("*", [f"src/{UTIL_NAME}/**/*.py"]),
        ],
        language_level=3,
    ),
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIREMENTS,
    entry_points={
        "console_scripts": [
            f"{UTIL_NAME} = {UTIL_NAME}:main",
        ]
    },
)

import os
import sys
from pathlib import Path

from setuptools import find_packages, setup

INSTALL_REQUIREMENTS = [
    'argcomplete~=2.0.0',
    'numpy~=1.23.1',
    'pandas~=1.4.3',
    'ccsyspath~=1.1.0',
    'clang~=14.0',
    'llvmlite~=0.39.0',
    'libclang~=14.0.1',
    'colorama~=0.4.5',
    'termcolor~=1.1.0',
    'python-decouple~=3.6',
    'requests~=2.28.1',
]
UTIL_NAME = os.getenv('UTIL_NAME')
UTIL_VERSION = os.getenv('UTIL_VERSION')


if '--install-requirements' in sys.argv:
    print(' '.join(INSTALL_REQUIREMENTS))
    sys.exit(0)
elif UTIL_NAME is None or UTIL_VERSION is None:
    print('Please provide UTIL_NAME and UTIL_VERSION environment variables.')
    sys.exit(1)


setup(
    name=f'{UTIL_NAME}',
    version=f'{UTIL_VERSION}',
    description='Code plagiarism searching package',
    author='Artyom Semidolin, Dmitry Nikolaev, Alexander Evsikov',
    url='https://github.com/OSLL/code-plagiarism',
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license='MIT License',
    platforms=["linux"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Plagiarism Detection',
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires='>=3.8',
    install_requires=INSTALL_REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'codeplag = codeplag:main',
        ]
    }
)

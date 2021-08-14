from setuptools import setup, find_packages
from pathlib import Path


setup(
    name='codeplag',
    version='0.0.1',
    description='Code plagiarism searching package',
    author='Artyom Semidolin, Dmitry Nikolaev, Alexander Evsikov',
    project_urls={
        'Source Code': 'https://github.com/OSLL/code-plagiarism',
    },
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Plagiarism Detection',
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.17',
        'pandas>=1.0.5',
        'ccsyspath>=1.1.0',
        'clang>=11.0',
        'libclang>=10.0.1.0',
        'numba>=0.52.0',
        'colorama>=0.3.9',
        'termcolor>=1.1.0',
        'python-decouple>=3.4',
        'requests',
    ],
    tests_require=[
        'pytest',
    ]
)

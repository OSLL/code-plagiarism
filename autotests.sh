#!/bin/bash

codeplag --version && \
codeplag -ext cpp --files src/codeplag/cplag/tests/data/sample1.cpp src/codeplag/cplag/tests/data/sample2.cpp && \
codeplag -ext cpp --directories src/codeplag/cplag/tests/data && \
codeplag -ext py --directories src/codeplag/cplag/tests/data src/codeplag/cplag/tests --files ./src/codeplag/pyplag/astwalkers.py && \
codeplag -ext py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py https://github.com/OSLL/code-plagiarism/blob/main/setup.py && \
codeplag -ext py --github-user OSLL --regexp "code-plag" && \
codeplag -ext py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/tests

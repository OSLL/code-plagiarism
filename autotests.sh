#!/bin/bash

codeplag --version && \
codeplag --directories src/codeplag/cplag/tests/data src/ --files src/codeplag/cplag/tests/data/sample1.cpp src/codeplag/cplag/tests/data/sample2.cpp -ext cpp && \
codeplag -ext py --files ./src/codeplag/pyplag/astwalkers.py --directories ./src/codeplag/pyplag && \
codeplag -ext py --directories ./src/codeplag/algorithms ./src && \
codeplag -ext py --files src/codeplag/pyplag/astwalkers.py --github-user OSLL --regexp "code-" --all-branches && \
codeplag -ext py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py --github-user OSLL -e "code-" -ab && \
codeplag -ext py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py -d src/codeplag/pyplag/ && \
codeplag -ext py --directories src/ --github-user OSLL -e "code-" && \
codeplag -ext py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --github-user OSLL -e "code-" && \
codeplag -ext py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --directories src/codeplag/pyplag/

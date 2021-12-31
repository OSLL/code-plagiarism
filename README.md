# Code Plagiarism Analysis

## 1. Install

First of all, clone the repository and moved into this.

```
  sudo apt install git # if not installed
  git clone https://github.com/OSLL/code-plagiarism.git
  cd code-plagiarism/
```

### 1.1 Manual installation on local computer

- OS Ubuntu Linux >= 18.04

- python version >= 3.6 && < 3.8

- Run these commands:

```
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    sudo apt install clang libncurses5

    # Optional
    pip3 install virtualenv
    python3 -m venv venv
    source venv/bin/activate

    pip3 install -U pip # pip3 version >= 19.0
    pip3 install argparse-manpage
    pip3 install --upgrade setuptools # Ensure that an up-to-date version of setuptools is installed
    make
```

### 1.2 Docker

- Create a code-plagiarism docker image

```
  $ make docker
```

- Starting tests with using created image
```
  $ make docker-test
```

- Run a code-plagiarism container

```
  $ make docker-run
```

## 2. Tests

- Testing for analyzers with unittest lib
  ```
    $ make test
  ```
- Testing for analyzers with pytest lib (if installed)
  ```
    $ make test-pytest
  ```

## 3. Work with codeplagcli

  Before starting work with searching on GitHub, you may define variable ACCESS_TOKEN in file .env in the folder from which you want to run the app:

  ACCESS_TOKEN - Personal access token which add more requests to repos and access to private repos if you give it.

  > call help
  ```
  $ codeplag --help
  ```
  > for more information run after `make` or in a docker container
  ```
  $ man codeplag
  ```

## 4. Demo examples (works in the project directory and with an installed codeplag package)

- python analyzer
  ```
    $ codeplag -ext py --files ./src/codeplag/pyplag/astwalkers.py --directories ./src/codeplag/pyplag
    $ codeplag -ext py --directories ./src/codeplag/algorithms ./src
    $ codeplag -ext py --files src/codeplag/pyplag/astwalkers.py --github-user OSLL --regexp code- --all-branches
    $ codeplag -ext py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py --github-user OSLL -e code- -ab
    $ codeplag -ext py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py -d src/codeplag/pyplag/
    $ codeplag -ext py --directories src/ --github-user OSLL -e code-
    $ codeplag -ext py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --github-user OSLL -e code-
    $ codeplag -ext py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --directories src/codeplag/pyplag/
  ```

- C++/C analyzer
  ```
    $ codeplag -ext cpp --directories src/codeplag/cplag/tests/data src/ --files src/codeplag/cplag/tests/data/sample1.cpp src/codeplag/cplag/tests/data/sample2.cpp
  ```

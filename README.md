# Code Plagiarism Analysis

## 1. Install

First of all, clone the repository and moved into this.

```
  git clone https://github.com/OSLL/code-plagiarism.git
  cd code-plagiarism/
```

### 1.1 Manual installation on local computer

- OS Ubuntu Linux >= 18.04

- python version >= 3.6 && < 3.8

- Run these commands:

```
    sudo apt update
    sudo apt install git
    sudo apt install python3 python3-pip python3-venv
    sudo apt install clang libncurses5

    pip3 install virtualenv
    python3 -m venv venv
    source venv/bin/activate

    pip3 install -U pip # pip3 version >= 19.0
    pip3 install --upgrade setuptools # Ensure that an up-to-date version of setuptools is installed
    python3 setup.py install || make install

    make test # Run tests to check work of the util
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

## 3. Work with analyzers

- python analyzer
  > call help
  ```
    $ codeplag --help
  ```
  > Local file compares with files in a local directory
  ```
    $ codeplag --file PATH --dir PATH [--threshold THRESHOLD]
  ```
  > Files in local project compares with files in a local directory
  ```
    $ codeplag --project PATH --dir PATH [--threshold THRESHOLD]
  ```
  Before starting work with searching on GitHub, you may define variable ACCESS_TOKEN in file .env in the folder from which you want to run the app:

  ACCESS_TOKEN - Personal access token which add more requests to repos and access to private repos if you give it.

  > Local file compares with files in git repositories
  ```
    $ codeplag --file PATH --git URL [--regexp EXPR] [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Git file compares with files in git repositories
  ```
    $ codeplag --git_file URL --git URL [--regexp EXPR] [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Git file compares with files in a local directory
  ```
    $ codeplag --git_file URL --dir PATH [--threshold THRESHOLD]
  ```
  > Files in local project compares with git repositories
  ```
    $ codeplag --project PATH --git URL [--regexp EXPR]  [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Files in git project compares with git repositories
  ```
    $ codeplag --git_project URL --git URL [--regexp EXPR]  [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Files in git project compares with files in a local directory
  ```
    $ codeplag --git_project URL --dir PATH [--threshold THRESHOLD]
  ```
- C++/C analyzer
  > Local file compares with files in a local directory
  ```
    $ codeplag --file PATH --dir PATH [--threshold THRESHOLD]
  ```
  > Files in local project compares with files in a local directory
  ```
    $ codeplag --project PATH --dir PATH [--threshold THRESHOLD]
  ```

## 4. Demo examples (works in the project directory and with an installed codeplag package)

- python analyzer
  ```
    $ codeplag --file ./src/codeplag/pyplag/astwalkers.py --dir ./src/codeplag/pyplag
    $ codeplag --project ./src --dir ./src/codeplag/algorithms
    $ codeplag --file src/codeplag/pyplag/astwalkers.py --git OSLL --regexp code- --check_policy 1
    $ codeplag --git_file https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py --git OSLL -e code- -cp 1
    $ codeplag --git_file https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py -d src/codeplag/pyplag/
    $ codeplag --project src/ --git OSLL -e code-
    $ codeplag --git_project https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --git OSLL -e code-
    $ codeplag --git_project https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag -d src/codeplag/pyplag/
  ```

- C++/C analyzer
  ```
    $ codeplag --file src/codeplag/cplag/tests/data/sample1.cpp --dir src/codeplag/cplag/tests/data
    $ codeplag --project src/codeplag/cplag/ --dir src/codeplag/cplag/tests/data
  ```

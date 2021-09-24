# Code Plagiarism Analysis

## 1. Collaboration rules

### 1.1. Code style

- C++ google style ([guide](https://google.github.io/styleguide/cppguide.html))

- Python PEP8 style ([guide](https://www.python.org/dev/peps/pep-0008/))

## 2. Install

### 2.1 Manual

- OS Ubuntu Linux >= 18.04

- python version >= 3.6

- pip3 version >= 19.0 (pip3 install -U pip)

- Ensure that an up-to-date version of setuptools is installed:

```
  pip3 install --upgrade setuptools
```

- install **clang** and **libncurses5** with apt or other packages manager

- python3 setup.py install --user

- if you want to easy install and test the app then run ./install.sh (it uses apt)

### 2.2 Docker

- Create a code-plagiarism docker image

```
  docker build . -t codeplag
```

- Run a code-plagiarism container

```
  docker run -it --name codeplag codeplag /bin/bash
```

## 3. Tests

- Testing for C/C++ and Python 3 analyzers with unittest lib
  ```
    $ python3 -m unittest discover <path/to/the/src/folder/of/the/project>
  ```
  > For getting more testing information add the `-v` flag
  ```
    $ python3 -m unittest discover <path/to/the/src/folder/of/the/project> -v
  ```
- Testing for C/C++ and Python 3 analyzers with pytest lib (Works from the cloned repository)
  ```
    $ python3 -m pytest
  ```
  > For getting more testing information add the `-v` flag
  ```
    $ python3 -m pytest -v
  ```

## 4. Work with analyzers

- python analyzer
  > call help
  ```
    $ python3 -m codeplag.pyplag --help
  ```
  > Local file compares with files in a local directory
  ```
    $ python3 -m codeplag.pyplag --file PATH --dir PATH [--threshold THRESHOLD]
  ```
  > Files in local project compares with files in a local directory
  ```
    $ python3 -m codeplag.pyplag --project PATH --dir PATH [--threshold THRESHOLD]
  ```
  Before starting work with searching on GitHub, you may define variable ACCESS_TOKEN in file .env in the folder from which you want to run the app:

  ACCESS_TOKEN - Personal access token which add more requests to repos and access to private repos if you give it.

  > Local file compares with files in git repositories
  ```
    $ python3 -m codeplag.pyplag --file PATH --git URL [--reg_exp EXPR] [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Git file compares with files in git repositories
  ```
    $ python3 -m codeplag.pyplag --git_file URL --git URL [--reg_exp EXPR] [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Git file compares with files in a local directory
  ```
    $ python3 -m codeplag.pyplag --git_file URL --dir PATH [--threshold THRESHOLD]
  ```
  > Files in local project compares with git repositories
  ```
    $ python3 -m codeplag.pyplag --project PATH --git URL [--reg_exp EXPR]  [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Files in git project compares with git repositories
  ```
    $ python3 -m codeplag.pyplag --git_project URL --git URL [--reg_exp EXPR]  [--check_policy CHECK_POLICY] [--threshold THRESHOLD]
  ```
  > Files in git project compares with files in a local directory
  ```
    $ python3 -m codeplag.pyplag --git_project URL --dir PATH [--threshold THRESHOLD]
  ```
- C++/C analyzer
  > Compare all files in folder
  ```
    $ python3 -m codeplag.cplag <path/to/folder/with/cpp/or/cc/files>
  ```

## 5. Demo examples (works in the project directory and with an installed codeplag package)

- python analyzer
  ```
    $ python3 -m codeplag.pyplag --file ./src/codeplag/pyplag/astwalkers.py --dir ./src/codeplag/pyplag
    $ python3 -m codeplag.pyplag --project ./src --dir ./src/codeplag/algorithms
    $ python3 -m codeplag.pyplag --file src/codeplag/pyplag/astwalkers.py --git OSLL --reg_exp code- --check_policy 1
    $ python3 -m codeplag.pyplag --git_file https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/mode.py --git OSLL -e code- -cp 1
    $ python3 -m codeplag.pyplag --git_file https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/mode.py -d src/codeplag/pyplag/
    $ python3 -m codeplag.pyplag --project src/ --git OSLL -e code-
    $ python3 -m codeplag.pyplag --git_project https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --git OSLL -e code-
    $ python3 -m codeplag.pyplag --git_project https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag -d src/codeplag/pyplag/
  ```

- C++/C analyzer
  ```
    $ python3 -m codeplag.cplag ./other/cpp/tests
  ```

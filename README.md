# Code Plagiarism Analysis

## 1. Collaboration rules

### 1.1. Code style

- C++ google style ([guide](https://google.github.io/styleguide/cppguide.html))

- Python PEP8 style ([guide](https://www.python.org/dev/peps/pep-0008/))

## 2. Install requirements

- OS Linux

- python version 3.6+ or even 3.8+

- pip3 version >= 19.0 (pip3 install -U pip)

- pip3 install -r ./requirements.txt

- sudo apt install clang

- sudo apt install libncurses5

## 3. Tests

- Testing for C/C++ and Python 3 analyzers
  ```
    $ python3 -m unittest discover src/
  ```
  > For getting more testing information add the `-v` flag
  ```
    $ python3 -m unittest discover src/ -v
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
  Before starting work with repositories, you may to define variable ACCESS_TOKEN in src/github_helper/.env:

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

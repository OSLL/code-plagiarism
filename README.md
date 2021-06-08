# Code Plagiarism Analysis

## 1. Collaboration rules

### 1.1. Code style

- C++ google style ([guide](https://google.github.io/styleguide/cppguide.html))

- Python PEP8 style ([guide](https://www.python.org/dev/peps/pep-0008/))

## 2. Install requirements

- python version 3.6+ or even 3.8+

- pip3 version >= 19.0 (pip3 install -U pip)

- pip3 install -r ./requirements.txt

- sudo apt install clang

- sudo apt install libncurses5

## 3. Tests

- Testing for C/C++ analyzer
  > Test of cplag functions
  ```
    $ python3 test/cplag
  ```

  > Flag `-v` for more testing information
  ```
    $ python3 test/cplag -v
  ```
- Testing for python analyzer (Temporarily not working)
  > Test of pyplag functions
  ```
    $ python3 test/pyplag
  ```

  > Flag `-v` for more testing information
  ```
    $ python3 test/pyplag -v
  ```

## 4. Work with analyzers

- python analyzer
  > Compare all files in folder
  ```
    $ python3 src/pyplag <path/to/folder/with/py/files>
  ```
  Before starting work with repositories, you must to define variable OWNER in src/github_helper/.env and ACCESS_TOKEN:

  OWNER - organization user name on github;

  ACCESS_TOKEN - Personal access token which add more requests to repos and access to private repos if you give it.

  > Compare file in folder with files in github repositories
  ```
    $ python3 src/pyplag <path/to/file/which/compare> <reg_exp>
  ```
  > Compare file by link on github starts with https:// with files in github repositories
  ```
    $ python3 src/pyplag <link/to/file/which/compare> <reg_exp>
  ```
- C++/C analyzer
  > Compare all files in folder
  ```
    $ python3 src/cplag <path/to/folder/with/cpp/or/cc/files>
  ```

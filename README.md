# Code Plagiarism Analysis

Program for finding plagiarism in the source code written in Python 3, C, and C++ based on comparing AST metadata.

## 1. Install

### 1.1 Build and run local Docker container

- Create a code-plagiarism docker image

  ```
  $ make docker-image
  ```

- Rebuild created code-plagiarism docker image

  ```
  $ make docker-image REBUILD=1
  ```

- Run created a code-plagiarism container

  ```
  $ make docker-run
  ```

- Show help information about other make commands

  ```
  $ make help
  ```

### 1.2 Pull the Docker Image from Docker Hub

- Pull an image from Docker Hub
  ```
  $ docker pull artanias/codeplag-ubuntu22.04:latest
  ```

- Run container based on pulled image and connect volume with your data
  > The docker image has volume '/usr/src/works' which is the directory with your data.
  ```
  $ docker run --rm --tty --interactive --volume <absolute_local_path_with_data>:/usr/src/works "artanias/codeplag-ubuntu22.04:latest" /bin/bash
  ```
  or if Mongo is used on localhost
  ```
  $ docker run --rm --tty --interactive --volume <absolute_local_path_with_data>:/usr/src/works --add-host=host.docker.internal:host-gateway "artanias/codeplag-ubuntu22.04:latest" /bin/bash
  ```

### 1.3 Install with package manager apt-get

- Requirements:
  - OS Ubuntu Linux == 22.04
  - Python version == 3.10

- For this purpose, you need to get installing package from releases [tab](https://github.com/OSLL/code-plagiarism/releases) with extension .deb;
- The next step is run commands on the target system:
  ```
  $ sudo apt update
  $ sudo apt install python3 python3-pip
  $ sudo apt install clang libncurses5
  $ sudo apt-get install <path_to_the_package>/<package_name>.deb
  ```

### 1.4 MongoDB cache

If you want to use MongoDB cache for saving reports and works metadata, complete steps:

- Run MongoDB (you can configure DB params in [compose](docker/compose.yml))

  ```
  $ docker compose --file docker/compose.yml up --detach
  ```

## 2. Tests

### 2.1. Pre-commit

- Check code with linters, format code, and check used types with pre-commit.
  ```
  # Before local checking, you need to install dependencies into your virtual environment.
  $ python3 -m pip install --requirement docs/notebooks/requirements.txt
  $ python3 -m pip install $(python3 -m setup.py --build-requirements)
  $ python3 -m pip install $(python3 -m setup.py --install-requirements)
  $ python3 -m pip install pre-commit==4.1.0
  $ make pre-commit
  ```

- Also, before committing, you need to install pre-commit hooks in the repository.
  ```
  $ pre-commit install
  ```

### 2.2. Unit tests

- Testing for analyzers with pytest lib (required preinstalled pytest framework).
  ```
  $ pip3 install $(python3 setup.py --test-requirements)
  $ make test
  ```

### 2.3. Auto tests

- Testing work of the util with written autotests (required installed util and 'ACCESS_TOKEN' with empty accesses, look ahead).
  ```
  $ make autotest
  ```

## 3. Work with codeplagcli

  Before starting work with searching on GitHub, you may define variable ACCESS_TOKEN in file .env in the folder from which you want to run the app:

  > ACCESS_TOKEN - Personal access token which add more requests to repos and access to private repos if you give it.

  For beginning, you may to call help for getting information about available CLI options

  ```
  $ codeplag --help
  ```

  For getting more information about CLI run after **make** or in a docker container
  ```
  $ man codeplag
  ```

  When using **bash** as your shell, **codeplag** can use [argcomplete](https://kislyuk.github.io/argcomplete/) for auto-completion. For permanent completion activation, use:
  ```
  $ register-python-argcomplete codeplag >> ~/.bashrc
  ```

## 4. Demo examples (works in the project directory and with an installed codeplag package)

- Show help: `$ codeplag --help`
- Show help of subcommands (and further along the chain similarly): `$ codeplag check --help`
- Setting up the util:
  ```
  # Setup check threshold to 70
  # Language to English
  # Show check progress
  # Extension of reports 'csv'
  # Reports path to '/usr/src/works'
  # Path to environment variables '/usr/src/works/.env'
  $ codeplag settings modify --threshold 70 --language en --show_progress 1 --reports_extension csv --reports /usr/src/works --environment /usr/src/works/.env --ngrams-length 2 --workers 4
  ```
- If you use MongoDB with custom settings configure util
  ```
  $ codeplag settings modify --mongo-port <mongo-port> --mongo-user <mongo-user> --mongo-pass <mongo-pass> --mongo-host <mongo-host>
  ```
- Python analyzer:
  ```
  $ codeplag check --extension py --files src/codeplag/pyplag/astwalkers.py --directories src/codeplag/pyplag
  $ codeplag check --extension py --directories src/codeplag/algorithms src
  $ codeplag check --extension py --files src/codeplag/pyplag/astwalkers.py --github-user OSLL --repo-regexp code- --all-branches
  $ codeplag check --extension py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py --github-user OSLL --repo-regexp code- --all-branches
  $ codeplag check --extension py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py --directories src/codeplag/pyplag/
  $ codeplag check --extension py --directories src/ --github-user OSLL --repo-regexp code-
  $ codeplag check --extension py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --github-user OSLL --repo-regexp code-
  $ codeplag check --extension py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --directories src/codeplag/pyplag/
  ```
- C++/C analyzer:
  ```
  $ codeplag check --extension cpp --directories src/codeplag/cplag/tests/data src/ --files test/codeplag/cplag/data/sample1.cpp test/codeplag/cplag/data/sample2.cpp
  $ codeplag check --extension cpp --github-files https://github.com/OSLL/code-plagiarism/blob/main/test/codeplag/cplag/data/sample3.cpp https://github.com/OSLL/code-plagiarism/blob/main/test/codeplag/cplag/data/sample4.cpp
  $ codeplag check --extension cpp --github-project-folders https://github.com/OSLL/code-plagiarism/tree/main/test
  $ codeplag check --extension cpp --github-user OSLL --repo-regexp "code-plag"
  ```
- Create html report: `codeplag report create --path /usr/src/works`

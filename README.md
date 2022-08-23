# Code Plagiarism Analysis

## 1. Install

### 1.1 Manual installation on the local system from sources

  First of all, clone the repository and moved into this.

  ```
  sudo apt install git # if not installed
  git clone https://github.com/OSLL/code-plagiarism.git
  cd code-plagiarism/
  ```

- OS Ubuntu Linux >= 20.04

- Python version >= 3.8

- Run these commands:

  ```
  sudo apt update
  sudo apt install python3 python3-pip
  sudo apt install clang libncurses5

  # Optional
  sudo apt install python3-venv
  pip3 install virtualenv
  python3 -m venv venv
  source venv/bin/activate

  pip3 install -U pip # pip3 version >= 19.0
  pip3 install argparse-manpage==3 requests==2.28.1
  pip3 install --upgrade setuptools # Ensure that an up-to-date version of setuptools is installed
  make
  ```
### 1.2 Build and run local Docker container

- Create a code-plagiarism docker image

  ```
  $ make docker-image
  ```

- Starting tests with using created image
  ```
  $ make docker-test
  ```

- Run created a code-plagiarism container

  ```
  $ make docker-run
  ```

### 1.3 Pull the Docker Image from Docker Hub

- Pull an image from Docker Hub
  ```
  $ docker pull artanias/codeplag-ubuntu20.04:latest
  ```

- Run container based on pulled image and connect volume with your data
  ```
  $ docker run --rm --tty --interactive --volume <absolute_local_path_with_data>:<absolute_containter_path_with_data> "artanias/codeplag-ubuntu20.04:latest" /bin/bash
  ```

### 1.4 Install with package manager apt-get

- For this purpose, you need to get installing package from releases [tab](https://github.com/OSLL/code-plagiarism/releases) with extension .deb;
- The next step is run command on the target system:
  ```
  $ sudo apt-get install <path_to_the_package>/<package_name>.deb
  ```

## 2. Tests

- Testing for analyzers with pytest lib (required preinstalled pytest framework)
  ```
  $ pip3 install pytest==7.1.2
  $ make test
  ```

- Testing work of the util with written autotests (required installed util and 'ACCESS_TOKEN' with empty accesses, look ahead)
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

## 5. Demo examples (works in the project directory and with an installed codeplag package)

- Python analyzer
  ```
  $ codeplag --extension py --files src/codeplag/pyplag/astwalkers.py --directories src/codeplag/pyplag
  $ codeplag --extension py --directories src/codeplag/algorithms src
  $ codeplag --extension py --files src/codeplag/pyplag/astwalkers.py --github-user OSLL --regexp code- --all-branches
  $ codeplag --extension py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py --github-user OSLL --regexp code- --all-branches
  $ codeplag --extension py --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py --directories src/codeplag/pyplag/
  $ codeplag --extension py --directories src/ --github-user OSLL --regexp code-
  $ codeplag --extension py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --github-user OSLL --regexp code-
  $ codeplag --extension py --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag --directories src/codeplag/pyplag/
  ```

- C++/C analyzer
  ```
  $ codeplag --extension cpp --directories src/codeplag/cplag/tests/data src/ --files test/codeplag/cplag/data/sample1.cpp test/codeplag/cplag/data/sample2.cpp
  $ codeplag --extension cpp --github-files https://github.com/OSLL/code-plagiarism/blob/main/test/codeplag/cplag/data/sample3.cpp https://github.com/OSLL/code-plagiarism/blob/main/test/codeplag/cplag/data/sample4.cpp
  $ codeplag --extension cpp --github-project-folders https://github.com/OSLL/code-plagiarism/tree/main/test
  $ codeplag --extension cpp --github-user OSLL --regexp "code-plag"
  ```

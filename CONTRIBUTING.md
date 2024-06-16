# Contributing

First of all thank you for your desire to contribute in that project.

## Development environment

Before starting work with this project you need to install [Python 3.10](https://www.python.org/), [Docker](https://www.docker.com/) (for commands like 'make docker-test').

After that you'll need to install and setup pre-commit hooks for checking style of source code, formatting it and checking types:

```
$ pip3 install pre-commit
$ pre-commit install  # Run from cloned or forked repo
```

## Writing tests

For writing tests you'll need to install python package [pytest](https://docs.pytest.org/). All new tests should write with use of that framework.

Unit tests placed in the 'test/unit' folder which repeats structure of the 'src/' folder with sources. Auto tests placed in the 'test/auto' folder.

Note that all of the unit tests names should starts with prefix 'test_'.

## Branches rules

1) The 'main' branch consists sources of the last work and tested version of the util, correct documentation, some helpfull scripts and research notebooks;
2) The 'develop' branch consist source of the current developing version;
3) All pull requests should fix one issue or some related issues. After the review, all commits will squash (combined into one) and merge with descriptive message.

## Making pull requests

Sequence for submitting PR:

1) Fork this repo (for external contributors) or clone (for internal contributors);
2) Make branch off of 'develop' branch;
3) Add descriptive unit tests;
4) If desire, you may to add auto tests. When adding error fixes it's required;
5) After making commits check that all pre-commit hooks is passed;
6) Push commits into your remote branch and than create pull request.

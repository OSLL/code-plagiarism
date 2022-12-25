# Contributing

First of all thank you for your desire to contribute in that project.

## Development environment

Before starting work with this project you need to install [Python 3.8](https://www.python.org/), [Docker](https://www.docker.com/) (for commands like 'make docker-test').

After that you'll need to install and setup pre-commit hooks for checking style of source code, formatting it and checking types:

```
$ pip3 install pre-commit
$ pre-commit install  # Run from cloned repo
```

## Writing tests

For writing tests you'll need to install python package [pytest](https://docs.pytest.org/). All new tests should write with use of that framework.

Unit tests placed in the 'test/unit' folder which repeats structure of the 'src/' folder with sources. Auto tests placed in the 'test/auto' folder.

Note that all of the unit tests names should starts with prefix 'test_'.

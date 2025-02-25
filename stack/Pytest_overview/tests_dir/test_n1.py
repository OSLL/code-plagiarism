import pytest


def add(a, b):
    return a + b


def test_1():
    assert add(1, 1) == 2
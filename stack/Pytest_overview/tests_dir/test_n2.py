import pytest


def mult(a, b):
    return a * b


def test_1():
    assert mult(2, 3) == 6

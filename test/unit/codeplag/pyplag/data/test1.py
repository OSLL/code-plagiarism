INT_CONST: int = 10
INT_CONST += 15
FLOAT_CONST = 10.5


def my_func(length, future):  # noqa: ANN001
    future += length
    print(future)
    return future


if True:
    my_func(2, 3)

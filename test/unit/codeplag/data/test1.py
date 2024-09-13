def my_func(length, future):  # noqa: ANN001
    future += length
    print(future)
    return future


if True:
    my_func(2, 3)

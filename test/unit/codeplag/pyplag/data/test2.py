def my_func(length, future, shifr):  # noqa: ANN001
    future += length
    print(shifr * future)
    return future


if True:
    my_func(2, 3, "Hello")

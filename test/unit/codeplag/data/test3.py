import os


def join_path(path):  # noqa: ANN001
    cwd = os.getcwd()

    return os.path.join(cwd, path)


def example(new_path, is_exist):  # noqa: ANN001
    if is_exist:
        new_path = join_path(new_path)

    return new_path

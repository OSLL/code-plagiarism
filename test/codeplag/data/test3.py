import os


def join_path(path):
    cwd = os.getcwd()

    return os.path.join(cwd, path)


def example(new_path, is_exist):
    if is_exist:
        new_path = join_path(new_path)

    return new_path

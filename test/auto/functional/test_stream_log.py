from utils import SUCCESS_CODE, run_check


def test_splitted_streams():
    result = run_check([], extension="cpp", verbose=False)

    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")

    assert result.returncode == SUCCESS_CODE
    assert len(stdout.splitlines()) == 2
    assert len(stderr.splitlines()) == 1

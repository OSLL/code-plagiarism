from utils import run_check


def test_splitted_streams():
    result = run_check([], extension="cpp", verbose=False)

    stdout = result.cmd_res.stdout.decode("utf-8")
    stderr = result.cmd_res.stderr.decode("utf-8")

    result.assert_success()
    assert len(stdout.splitlines()) == 2
    assert len(stderr.splitlines()) == 1

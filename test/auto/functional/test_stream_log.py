from utils import run_check


def test_splitted_streams():
    # Try to get a file that does not exist
    github_file = "https://github.com/OSLL/code-plagiarism/blob/main/skfjkljflsd"
    result = run_check(["--github-files", github_file], extension="cpp")

    stdout = result.cmd_res.stdout.decode("utf-8")
    stderr = result.cmd_res.stderr.decode("utf-8")

    result.assert_failed()
    assert len(stdout.splitlines()) > 1
    assert len(stderr.splitlines()) > 1

import re

from utils import SUCCESS_CODE, run_check, run_cmd


def test_log_once():
    dir = "src/codeplag"
    result = run_check(["--directories", dir], extension="cpp")

    pattern = f"Getting works features from {dir}"
    output_result = result.stdout.decode("utf-8")

    assert result.returncode == SUCCESS_CODE
    assert pattern in output_result

    handled_stdout = re.sub(pattern, "", output_result, count=1)
    assert pattern not in handled_stdout


def test_man_unminimized():
    result = run_cmd(["dpkg-divert", "--truename", "/usr/bin/man"])

    assert result.stdout.decode("utf-8").strip() == "/usr/bin/man"

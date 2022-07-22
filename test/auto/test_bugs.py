import re

from utils import SUCCESS_CODE, run_util


def test_log_once():
    dir = 'src/codeplag'
    result = run_util(
        ['--directories', dir],
        ext='cpp'
    )

    pattern = f'Getting works features from {dir}'
    output_result = result.stdout.decode('utf-8')

    assert result.returncode == SUCCESS_CODE
    assert pattern in output_result

    handled_stdout = re.sub(pattern, "", output_result, count=1)
    assert pattern not in handled_stdout

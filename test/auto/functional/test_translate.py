import pytest
from utils import modify_settings, run_util


@pytest.fixture(scope="function", autouse=True)
def set_english_translation():
    modify_settings(language="en").assert_success()

    yield


def test_translate_same_between_calls():
    assert (
        run_util(["check", "--help"]).cmd_res.stdout
        == run_util(["check", "--help"]).cmd_res.stdout
    )


def test_translate_changed_between_calls_when_language_changed():
    first_call_stdout = run_util(["check", "--help"]).cmd_res.stdout
    modify_settings(language="ru").assert_success()
    second_call_stdout = run_util(["check", "--help"]).cmd_res.stdout

    assert first_call_stdout != second_call_stdout

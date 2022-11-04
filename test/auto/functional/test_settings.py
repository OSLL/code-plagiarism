import pytest
from utils import modify_settings, show_settings

from codeplag.consts import CONFIG_PATH, UTIL_NAME


@pytest.fixture(scope='module', autouse=True)
def teardown():
    yield

    CONFIG_PATH.write_text("{}")


@pytest.mark.parametrize(
    "env, reports, threshold",
    [
        (".env", "src", 83),
        ("setup.py", "test", 67),
        (f"src/{UTIL_NAME}/utils.py", "debian", 93)
    ]
)
def test_modify_settings(env, reports, threshold):
    assert modify_settings(
        environment=env,
        reports=reports,
        threshold=threshold
    ).returncode == 0

    show_result = show_settings()
    assert show_result.returncode == 0

    assert bytes(env, encoding='utf-8') in show_result.stdout
    assert bytes(reports, encoding='utf-8') in show_result.stdout
    assert bytes(str(threshold), encoding='utf-8') in show_result.stdout


@pytest.mark.parametrize(
    "env, reports, threshold",
    [
        (".env", "src", 101),
        ("setup.py", "test983hskdfue", 67),
        (f"src/{UTIL_NAME}/utils.pyjlsieuow0", "debian", 93)
    ]
)
def test_modify_settings_bad(env, reports, threshold):
    assert modify_settings(
        environment=env,
        reports=reports,
        threshold=threshold
    ).returncode != 0

import pytest
from codeplag.consts import CONFIG_PATH, UTIL_NAME
from utils import modify_settings


@pytest.fixture(scope='module', autouse=True)
def teardown():
    yield

    CONFIG_PATH.write_text("{}")


@pytest.mark.parametrize(
    "env, reports, threshold, show_progress",
    [
        (f"src/{UTIL_NAME}/types.py", "src", 83, 0),
        ("setup.py", "test", 67, 1),
        (f"src/{UTIL_NAME}/utils.py", "debian", 93, 0)
    ]
)
def test_modify_settings(env, reports, threshold, show_progress):
    result = modify_settings(
        environment=env,
        reports=reports,
        threshold=threshold,
        show_progress=show_progress
    )
    assert result.returncode == 0

    assert bytes(env, encoding='utf-8') in result.stdout
    assert bytes(reports, encoding='utf-8') in result.stdout
    assert bytes(str(threshold), encoding='utf-8') in result.stdout
    assert bytes(str(show_progress), encoding='utf-8') in result.stdout


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

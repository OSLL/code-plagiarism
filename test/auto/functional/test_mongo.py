import time

import pytest
from testcontainers.mongodb import MongoDbContainer
from utils import modify_settings, run_check

from codeplag.consts import CONFIG_PATH, DEFAULT_MONGO_PASS, DEFAULT_MONGO_USER
from codeplag.db.mongo import MongoDBConnection

PY_SIM_FILES = ["test/unit/codeplag/data/test1.py", "test/unit/codeplag/data/test2.py"]
PY_FILES = ["test/unit/codeplag/data/test1.py", "test/unit/codeplag/data/test3.py"]


@pytest.fixture(scope="module")
def mongo_container() -> MongoDbContainer:
    with MongoDbContainer(
        "mongo:6.0", username=DEFAULT_MONGO_USER, password=DEFAULT_MONGO_PASS
    ) as mongo:
        mongo.start()
        time.sleep(8)
        yield mongo


@pytest.fixture(scope="module")
def mongo_connection(mongo_container: MongoDbContainer) -> MongoDBConnection:
    host = mongo_container.get_container_host_ip()
    port = int(mongo_container.get_exposed_port(27017))
    user = mongo_container.username
    password = mongo_container.password

    conn = MongoDBConnection(
        host=host,
        port=port,
        user=user,
        password=password,
    )
    yield conn


@pytest.fixture(scope="module", autouse=True)
def setup_module(mongo_connection: MongoDBConnection) -> None:
    modify_settings(
        log_level="trace",
        reports_extension="mongo",
        mongo_host=mongo_connection.host,
        mongo_port=mongo_connection.port,
        mongo_user=mongo_connection.user,
        mongo_pass=mongo_connection.password,
    ).assert_success()

    yield

    CONFIG_PATH.write_text("{}")


@pytest.fixture(autouse=True)
def clear_db(mongo_connection: MongoDBConnection) -> None:
    mongo_connection.clear_db()

    yield


@pytest.mark.parametrize(
    "cmd, found_plag",
    [
        (["--files", *PY_FILES], False),
        (["--files", *PY_SIM_FILES], True),
    ],
)
def test_py_correct_mongo_connection(cmd: list[str], found_plag: bool):
    result = run_check(cmd, extension="py")

    if found_plag:
        result.assert_found_similarity()
    else:
        result.assert_success()
    assert "Successfully connected to MongoDB!" in result.cmd_res.stdout

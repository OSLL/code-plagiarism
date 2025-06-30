"""MIT License.

Written 2025 by Artyom Semidolin.
"""

import os
from typing import Generator

import pytest

from codeplag.consts import DEFAULT_MONGO_PORT, DEFAULT_MONGO_USER
from codeplag.db.mongo import MongoDBConnection


@pytest.fixture(scope="module")
def mongo_host() -> str:
    host = os.environ.get("MONGO_HOST")
    assert host, f"Invalid MONGO_HOST environment '{host}'."
    return host


@pytest.fixture(scope="function")
def clear_db() -> Generator[None, None, None]:
    host = os.environ.get("MONGO_HOST")
    assert host, f"Invalid MONGO_HOST environment '{host}'."
    connection = MongoDBConnection(
        host=host,
        port=DEFAULT_MONGO_PORT,
        user=DEFAULT_MONGO_USER,
        password=DEFAULT_MONGO_USER,
    )
    connection.clear_db()

    yield

    connection.disconnect()


@pytest.fixture(scope="module")
def mongo_connection(mongo_host: str) -> Generator[MongoDBConnection, None, None]:
    conn = MongoDBConnection(
        host=mongo_host,
        port=DEFAULT_MONGO_PORT,
        user=DEFAULT_MONGO_USER,
        password=DEFAULT_MONGO_USER,
    )
    yield conn

    conn.disconnect()

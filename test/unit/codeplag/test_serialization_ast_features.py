from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from codeplag.reporters import serialize_ASTFeatures, deserialize_ASTFeatures
from codeplag.types import ASTFeatures


@pytest.fixture
def mock_default_logger(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.reporters.logger")


@pytest.fixture
def mock_write_config(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("codeplag.reporters.write_config")


class TestSerialization:
    def test_serialize_deserialize_astfeatures(self):
        features = ASTFeatures("example_path")
        serialized = serialize_ASTFeatures(features)
        deserialized = deserialize_ASTFeatures(serialized)

        assert features == deserialized
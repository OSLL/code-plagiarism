from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from codeplag.featurecache import serialize_feratures_to_dict, deserialize_feratures_from_dict
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
        serialized = serialize_feratures_to_dict(features)
        deserialized = deserialize_feratures_from_dict(serialized)

        assert features.sha256 == deserialized.sha256
        assert features.count_of_nodes == deserialized.count_of_nodes
        assert features.head_nodes == deserialized.head_nodes
        assert features.operators == deserialized.operators
        assert features.keywords == deserialized.keywords
        assert features.literals == deserialized.literals
        assert features.unodes == deserialized.unodes
        assert features.from_num == deserialized.from_num
        assert features.count_unodes == deserialized.count_unodes
        assert features.structure == deserialized.structure
        assert features.tokens == deserialized.tokens
        assert features.tokens_pos == deserialized.tokens_pos
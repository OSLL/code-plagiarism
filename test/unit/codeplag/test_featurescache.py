from typing_extensions import Self

from codeplag.featurescache import deserialize_features_from_dict, serialize_features_to_dict
from codeplag.types import ASTFeatures


class TestSerialization:
    def test_serialize_deserialize_astfeatures(self: Self, first_features: ASTFeatures) -> None:
        serialized = serialize_features_to_dict(first_features)
        deserialized = deserialize_features_from_dict(serialized)

        assert first_features == deserialized
        assert first_features.sha256 == deserialized.sha256
        assert first_features.modify_date == deserialized.modify_date
        assert first_features.count_of_nodes == deserialized.count_of_nodes
        assert first_features.head_nodes == deserialized.head_nodes
        assert first_features.operators == deserialized.operators
        assert first_features.keywords == deserialized.keywords
        assert first_features.literals == deserialized.literals
        assert first_features.unodes == deserialized.unodes
        assert first_features.from_num == deserialized.from_num
        assert first_features.count_unodes == deserialized.count_unodes
        assert first_features.structure == deserialized.structure
        assert first_features.tokens == deserialized.tokens
        assert first_features.tokens_pos == deserialized.tokens_pos

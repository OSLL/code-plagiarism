from abc import abstractmethod, ABC
from pathlib import Path

from typing_extensions import Self

from codeplag.db.mongo import FeaturesRepository
from codeplag.getfeatures import set_sha256
from codeplag.types import ASTFeatures


@set_sha256
def get_work_info(filepath: Path | str) -> ASTFeatures:
    features = ASTFeatures(filepath)

    return features


class AbstractFeaturesCache(ABC):
    @abstractmethod
    def save_features(self: Self, features: ASTFeatures) -> None: ...

    @abstractmethod
    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None: ...

    def get_features_from_filepath(self: Self, filepath: str | Path) -> ASTFeatures | None:
        features = get_work_info(filepath)

        return self.get_features(features)


class DummyFeaturesCache(AbstractFeaturesCache):
    def save_features(self: Self, features: ASTFeatures) -> None:
        return None

    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None:
        return None


class MongoFeaturesCache(AbstractFeaturesCache):
    def __init__(self: Self, repository: FeaturesRepository) -> None:
        self.repository = repository

    def save_features(self: Self, features: ASTFeatures) -> None:
        """Updates the cache with new work metadata and writes it to the MongoDB.

        Args:
            features (ASTFeatures): Contains work metadata.
        """
        self.repository.write_features(features)

    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None:
        return None


def serialize_features_to_dict(work: ASTFeatures) -> dict:
    serialized_dict = work.__dict__

    serialized_dict['filepath'] = str(work.filepath)

    return serialized_dict


def deserialize_features_from_dict(work_dict: dict) -> ASTFeatures:
    features = ASTFeatures(work_dict['filepath'])
    keys = list(work_dict.keys())
    keys.pop(keys.index('filepath'))
    for key in keys:
        setattr(features, key, work_dict.get(key))
    return features

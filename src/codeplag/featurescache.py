from abc import ABC, abstractmethod
from pathlib import Path

from typing_extensions import Self

from codeplag.types import ASTFeatures


def get_work_info(filepath: Path | str) -> ASTFeatures:
    features = ASTFeatures(filepath)
    features.sha256 = features.get_sha256()

    return features


class AbstractFeaturesCache(ABC):
    @abstractmethod
    def save_features(self: Self, features: ASTFeatures) -> None: ...

    @abstractmethod
    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None: ...

    def get_features_from_filepath(self: Self, filepath: str | Path) -> ASTFeatures | None:
        features = get_work_info(filepath)

        return self.get_features(features)


def serialize_features_to_dict(work: ASTFeatures) -> dict:
    serialized_dict = work.__dict__

    serialized_dict["filepath"] = str(work.filepath)

    return serialized_dict


def deserialize_features_from_dict(work_dict: dict) -> ASTFeatures:
    features = ASTFeatures(work_dict["filepath"])
    keys = list(work_dict.keys())
    keys.pop(keys.index("filepath"))
    for key in keys:
        setattr(features, key, work_dict.get(key))
    return features

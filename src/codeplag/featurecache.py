from abc import abstractmethod, ABC

from typing_extensions import Self

from codeplag.types import ASTFeatures


class AbstractFeatureCache(ABC):
    @abstractmethod
    def save_feature(self: Self, feature: ASTFeatures) -> None: ...

    @abstractmethod
    def get_feature(self: Self, work: ASTFeatures) -> ASTFeatures | None: ...


def serialize_feratures_to_dict(work: ASTFeatures) -> dict:
    return work.__dict__


def deserialize_feratures_from_dict(work_dict: dict) -> ASTFeatures:
    features = ASTFeatures(work_dict['filepath'])
    keys = list(work_dict.keys())
    keys.pop(keys.index('filepath'))
    for key in keys:
        setattr(features, key, work_dict.get(key))
    return features

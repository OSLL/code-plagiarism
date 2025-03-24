from abc import abstractmethod, ABC

from typing_extensions import Self

from codeplag.types import ASTFeatures


class AbstractFeatureCache(ABC):
    @abstractmethod
    def save_feature(self: Self, feature: ASTFeatures) -> None: ...

    @abstractmethod
    def get_feature(self: Self, work: ASTFeatures) -> ASTFeatures | None: ...

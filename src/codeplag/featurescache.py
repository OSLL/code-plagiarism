"""MIT License.

Written 2025 by Ivan Volkov, Daniil Lokosov
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

from typing_extensions import Self

from codeplag.types import (
    ASTFeatures,
    ASTFeaturesDict,
    NodeCodePlace,
    NodeCodePlaceDict,
    NodeStructurePlace,
    NodeStructurePlaceDict,
)
from webparsers.types import WorkInfo


class AbstractFeaturesCache(ABC):
    @abstractmethod
    def save_features(self: Self, features: ASTFeatures) -> None: ...

    @abstractmethod
    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None: ...

    def get_features_from_filepath(self: Self, filepath: Path) -> ASTFeatures | None:
        work = ASTFeatures(filepath)
        work.sha256 = work.get_sha256()

        return self.get_features(work)

    def get_features_from_work_info(self: Self, work_info: WorkInfo) -> ASTFeatures | None:
        work = ASTFeatures(work_info.link)
        work.modify_date = work_info.commit.date

        return self.get_features(work)


def serialize_node_structure_place_to_dict(nsp: NodeStructurePlace) -> NodeStructurePlaceDict:
    return {
        "depth": nsp.depth,
        "uid": nsp.uid,
    }


def serialize_node_code_place_to_dict(ncp: NodeCodePlace) -> NodeCodePlaceDict:
    return {
        "lineno": ncp.lineno,
        "col_offset": ncp.col_offset,
    }


def serialize_features_to_dict(work: ASTFeatures) -> ASTFeaturesDict:
    return {
        "filepath": str(work.filepath),
        "sha256": work.sha256,
        "modify_date": work.modify_date,
        "count_of_nodes": work.count_of_nodes,
        "head_nodes": work.head_nodes,
        "operators": dict(work.operators),
        "keywords": dict(work.keywords),
        "literals": dict(work.literals),
        "unodes": work.unodes,
        "from_num": {str(k): work.from_num[k] for k in work.from_num},
        "count_unodes": work.count_unodes,
        "structure": list(map(serialize_node_structure_place_to_dict, work.structure)),
        "tokens": work.tokens,
        "tokens_pos": list(map(serialize_node_code_place_to_dict, work.tokens_pos)),
    }


def deserialize_node_structure_place_from_dict(nsp: NodeStructurePlaceDict) -> NodeStructurePlace:
    return NodeStructurePlace(nsp["depth"], nsp["uid"])


def deserialize_node_code_place_from_dict(ncp: NodeCodePlaceDict) -> NodeCodePlace:
    return NodeCodePlace(ncp["lineno"], ncp["col_offset"])


def deserialize_features_from_dict(work_dict: ASTFeaturesDict) -> ASTFeatures:
    features = ASTFeatures(
        filepath=work_dict["filepath"],
        sha256=work_dict["sha256"],
        count_of_nodes=work_dict["count_of_nodes"],
        head_nodes=work_dict["head_nodes"],
        operators=defaultdict(int, work_dict["operators"]),
        keywords=defaultdict(int, work_dict["keywords"]),
        literals=defaultdict(int, work_dict["literals"]),
        unodes=work_dict["unodes"],
        from_num={int(k): work_dict["from_num"][k] for k in work_dict["from_num"]},
        count_unodes=work_dict["count_unodes"],
        structure=list(map(deserialize_node_structure_place_from_dict, work_dict["structure"])),
        tokens=work_dict["tokens"],
        tokens_pos=list(map(deserialize_node_code_place_from_dict, work_dict["tokens_pos"])),
    )

    features.modify_date = work_dict["modify_date"]
    return features

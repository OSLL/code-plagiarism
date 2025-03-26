from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

from typing_extensions import Self

from codeplag.types import ASTFeatures, NodeStructurePlace, NodeCodePlace


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


def serialize_node_structure_place_to_dict(nsp: NodeStructurePlace) -> dict:
    return {
        "depth": nsp.depth,
        "uid": nsp.uid,
    }


def serialize_node_code_place_to_dict(ncp: NodeCodePlace) -> dict:
    return {
        "lineno": ncp.lineno,
        "col_offset": ncp.col_offset,
    }


def serialize_features_to_dict(work: ASTFeatures) -> dict:
    serialized_dict = {
        "filepath": str(work.filepath),
        "sha256": work.sha256,
        "modify_date": work.modify_date,
        "count_of_nodes": work.count_of_nodes,
        "head_nodes": work.head_nodes,
        "operators": dict(work.operators),
        "keywords": dict(work.keywords),
        "literals": dict(work.literals),
        "unodes": work.unodes,
        "from_num": work.from_num,
        "count_unodes": work.count_unodes,
        "structure": list(map(serialize_node_structure_place_to_dict, work.structure)),
        "tokens": work.tokens,
        "tokens_pos": list(map(serialize_node_code_place_to_dict, work.tokens_pos)),
    }

    return serialized_dict


def deserialize_node_structure_place_from_dict(nsp: dict) -> NodeStructurePlace:
    return NodeStructurePlace(nsp["depth"], nsp["uid"])


def deserialize_node_code_place_from_dict(ncp: dict) -> NodeCodePlace:
    return NodeCodePlace(ncp["lineno"], ncp["col_offset"])


def deserialize_features_from_dict(work_dict: dict) -> ASTFeatures:
    features = ASTFeatures(
        filepath=work_dict["filepath"],
        sha256=work_dict["sha256"],
        count_of_nodes=work_dict["count_of_nodes"],
        head_nodes=work_dict["head_nodes"],
        operators=defaultdict(int, work_dict["operators"]),
        keywords=defaultdict(int, work_dict["keywords"]),
        literals=defaultdict(int, work_dict["literals"]),
        unodes=work_dict["unodes"],
        from_num=work_dict["from_num"],
        count_unodes=work_dict["count_unodes"],
        structure=list(map(deserialize_node_structure_place_from_dict, work_dict["structure"])),
        tokens=work_dict["tokens"],
        tokens_pos=list(map(deserialize_node_code_place_from_dict, work_dict["tokens_pos"])),
    )

    features.modify_date = work_dict["modify_date"]
    return features

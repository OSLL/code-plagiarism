"""This module contains logic for saving a comparison result into CSV."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from time import monotonic

import numpy as np
import pandas as pd
from typing_extensions import Self

from codeplag.consts import CSV_REPORT_COLUMNS, CSV_REPORT_FILENAME, CSV_SAVE_TICK_SEC
from codeplag.logger import codeplag_logger as logger
from codeplag.types import (
    ASTFeatures,
    FastCompareInfo,
    FullCompareInfo,
    StructureCompareInfo,
)


class AbstractReporter(ABC):
    @abstractmethod
    def __init__(self: Self) -> None: ...

    @abstractmethod
    def save_result(self: Self, compare_info: FullCompareInfo) -> None: ...

    @abstractmethod
    def get_result(
        self: Self, work1: ASTFeatures, work2: ASTFeatures
    ) -> FullCompareInfo | None: ...


class CSVReporter(AbstractReporter):
    def __init__(self: Self, reports: Path) -> None:
        if reports.is_dir():
            self.reports_path = reports / CSV_REPORT_FILENAME
        else:
            self.reports_path = reports
        self.__need_update: bool = False
        if self.reports_path.exists():
            self.__df_report = read_df(self.reports_path)
        else:
            self.__df_report = pd.DataFrame(columns=np.array(CSV_REPORT_COLUMNS), dtype=object)
            write_df(self.__df_report, self.reports_path)
        self.__csv_last_save = monotonic()

    def save_result(self: Self, compare_info: FullCompareInfo) -> None:
        """Updates the cache with new comparisons and writes it to the filesystem periodically.

        Args:
            compare_info (FullCompareInfo): Contains information about comparisons
              between the first and second works.
        """
        if not self.reports_path.exists():
            logger.error("The file '%s' for reports is no longer exists.", self.reports_path)
            return
        cache_val = self.__df_report[
            (self.__df_report.first_path == str(compare_info.first_path))
            & (self.__df_report.second_path == str(compare_info.second_path))
        ]
        if isinstance(cache_val, pd.DataFrame):
            self.__df_report.drop(cache_val.index, inplace=True)  # type: ignore
        self.__df_report = pd.concat(
            [
                self.__df_report,
                serialize_compare_result(compare_info),
            ],
            ignore_index=True,
        )
        self.__need_update = True
        if monotonic() - self.__csv_last_save > CSV_SAVE_TICK_SEC:
            self._write_df_to_fs()
            # Time to write can be long
            self.__csv_last_save = monotonic()

    def _write_df_to_fs(self: Self) -> None:
        if not self.__need_update:
            logger.debug("Nothing new to save to the csv report.")
            return

        logger.debug(f"Saving report to the file '{self.reports_path}'")
        write_df(self.__df_report, self.reports_path)
        self.__need_update = False

    def get_result(self: Self, work1: ASTFeatures, work2: ASTFeatures) -> FullCompareInfo | None:
        cache_val = self.__df_report[
            (self.__df_report.first_path == str(work1.filepath))
            & (self.__df_report.second_path == str(work2.filepath))
        ]
        assert cache_val is not None
        if (
            cache_val.shape[0]
            and cache_val.iloc[0].first_sha256 == work1.sha256
            and cache_val.iloc[0].second_sha256 == work2.sha256
        ):
            return deserialize_compare_result(cache_val.iloc[0])


def read_df(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", index_col=0, dtype=object)  # type: ignore


def write_df(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, sep=";")


def serialize_compare_result(compare_info: FullCompareInfo) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": compare_info.date,
            "first_modify_date": compare_info.first_modify_date,
            "first_sha256": compare_info.first_sha256,
            "second_modify_date": compare_info.second_modify_date,
            "second_sha256": compare_info.second_sha256,
            "first_path": compare_info.first_path.__str__(),
            "second_path": compare_info.second_path.__str__(),
            "jakkar": compare_info.fast.jakkar,
            "operators": compare_info.fast.operators,
            "keywords": compare_info.fast.keywords,
            "literals": compare_info.fast.literals,
            "weighted_average": compare_info.fast.weighted_average,
            "struct_similarity": compare_info.structure.similarity,
            "first_heads": [compare_info.first_heads],
            "second_heads": [compare_info.second_heads],
            "compliance_matrix": [compare_info.structure.compliance_matrix.tolist()],
        },
        dtype=object,
    )


def deserialize_compare_result(compare_result: pd.Series) -> FullCompareInfo:
    if isinstance(compare_result.compliance_matrix, str):
        similarity_matrix = np.array(json.loads(compare_result.compliance_matrix))
    else:
        similarity_matrix = np.array(compare_result.compliance_matrix)

    return FullCompareInfo(
        date=compare_result.date,
        first_modify_date=compare_result.first_modify_date,
        first_sha256=compare_result.first_sha256,
        first_path=_deserialize_path(compare_result.first_path),
        first_heads=_deserialize_head_nodes(compare_result.first_heads),
        second_modify_date=compare_result.second_modify_date,
        second_sha256=compare_result.second_sha256,
        second_path=_deserialize_path(compare_result.second_path),
        second_heads=_deserialize_head_nodes(compare_result.second_heads),
        fast=FastCompareInfo(
            jakkar=float(compare_result.jakkar),
            operators=float(compare_result.operators),
            keywords=float(compare_result.keywords),
            literals=float(compare_result.literals),
            weighted_average=float(compare_result.weighted_average),
        ),
        structure=StructureCompareInfo(
            compliance_matrix=similarity_matrix,
            similarity=float(compare_result.struct_similarity),
        ),
    )


def serialize_compare_result_to_dict(compare_info: FullCompareInfo) -> dict:
    return {
        "date": compare_info.date,
        "first_modify_date": compare_info.first_modify_date,
        "first_sha256": compare_info.first_sha256,
        "first_path": str(compare_info.first_path),
        "first_heads": compare_info.first_heads,
        "second_modify_date": compare_info.second_modify_date,
        "second_sha256": compare_info.second_sha256,
        "second_path": str(compare_info.second_path),
        "second_heads": compare_info.second_heads,
        "compare_result": {
            "fast": dict(
                zip(
                    list(compare_info.fast.__annotations__.keys()),
                    list(compare_info.fast),
                    strict=True,
                )
            ),
            "structure": {
                "similarity": compare_info.structure.similarity,
                "compliance_matrix": compare_info.structure.compliance_matrix.tolist(),
            },
        },
    }


def deserialize_compare_result_from_dict(result: dict) -> FullCompareInfo:
    compare_result = result["compare_result"]
    structure_d = dict(compare_result["structure"])
    fast_d = dict(compare_result["fast"])

    return FullCompareInfo(
        date=result["date"],
        first_modify_date=result["first_modify_date"],
        first_sha256=result["first_sha256"],
        first_heads=result["first_heads"],
        first_path=_deserialize_path(result["first_path"]),
        second_modify_date=result["second_modify_date"],
        second_sha256=result["second_sha256"],
        second_heads=result["second_heads"],
        second_path=_deserialize_path(result["second_path"]),
        fast=FastCompareInfo(
            jakkar=float(fast_d["jakkar"]),
            operators=float(fast_d["operators"]),
            keywords=float(fast_d["keywords"]),
            literals=float(fast_d["literals"]),
            weighted_average=float(fast_d["weighted_average"]),
        ),
        structure=StructureCompareInfo(
            similarity=float(structure_d["similarity"]),
            compliance_matrix=np.array(structure_d["compliance_matrix"]),
        ),
    )


def _deserialize_head_nodes(head_nodes: str) -> list[str]:
    return [head[1:-1] for head in head_nodes[1:-1].split(", ")]


def _deserialize_path(path: str) -> str | Path:
    if path.startswith("http"):
        return path
    return Path(path)

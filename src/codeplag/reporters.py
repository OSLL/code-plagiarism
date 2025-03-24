"""This module contains logic for saving a comparison result into JSON or CSV."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from time import monotonic

import numpy as np
import pandas as pd
from typing_extensions import Self

from codeplag.consts import CSV_REPORT_COLUMNS, CSV_REPORT_FILENAME, CSV_SAVE_TICK_SEC
from codeplag.logger import codeplag_logger as logger
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    FastMetrics,
    StructuresInfo,
)


class AbstractReporter(ABC):
    def __init__(self: Self, reports: Path) -> None:
        self.reports = reports

    @abstractmethod
    def save_result(
        self: Self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
    ) -> None: ...


class CSVReporter(AbstractReporter):
    def __init__(self: Self, reports: Path) -> None:
        super().__init__(reports)
        self.reports_path = self.reports / CSV_REPORT_FILENAME
        self.__need_update: bool = False
        if self.reports_path.is_file():
            self.__df_report = read_df(self.reports_path)
        else:
            self.__df_report = pd.DataFrame(columns=CSV_REPORT_COLUMNS, dtype=object)
        self.__csv_last_save = monotonic()

    def save_result(
        self: Self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
    ) -> None:
        """Updates the cache with new comparisons and writes it to the filesystem periodically.

        Args:
            first_work (ASTFeatures): Contains the first work metadata.
            second_work (ASTFeatures): Contains the second work metadata.
            compare_info (CompareInfo): Contains information about comparisons
              between the first and second works.
        """
        if not self.reports.is_dir():
            logger.error("The folder for reports isn't exists.")
            return
        cache_val = self.__df_report[
            (self.__df_report.first_path == str(first_work.filepath))
            & (self.__df_report.second_path == str(second_work.filepath))
        ]
        self.__df_report.drop(cache_val.index, inplace=True)
        self.__df_report = pd.concat(
            [
                self.__df_report,
                serialize_compare_result(first_work, second_work, compare_info),
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
        self.__df_report.to_csv(self.reports_path, sep=";")
        self.__need_update = False

    def get_compare_result_from_cache(
        self: Self, work1: ASTFeatures, work2: ASTFeatures
    ) -> CompareInfo | None:
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


def serialize_compare_result(
    first_work: ASTFeatures,
    second_work: ASTFeatures,
    compare_info: CompareInfo,
) -> pd.DataFrame:
    assert compare_info.structure is not None

    return pd.DataFrame(
        {
            "date": _get_current_date(),
            "first_modify_date": first_work.modify_date,
            "first_sha256": first_work.sha256,
            "second_modify_date": second_work.modify_date,
            "second_sha256": second_work.sha256,
            "first_path": first_work.filepath.__str__(),
            "second_path": second_work.filepath.__str__(),
            "jakkar": compare_info.fast.jakkar,
            "operators": compare_info.fast.operators,
            "keywords": compare_info.fast.keywords,
            "literals": compare_info.fast.literals,
            "weighted_average": compare_info.fast.weighted_average,
            "struct_similarity": compare_info.structure.similarity,
            "first_heads": [first_work.head_nodes],
            "second_heads": [second_work.head_nodes],
            "compliance_matrix": [compare_info.structure.compliance_matrix.tolist()],
        },
        dtype=object,
    )


def deserialize_compare_result(compare_result: pd.Series) -> CompareInfo:
    if isinstance(compare_result.compliance_matrix, str):
        similarity_matrix = np.array(json.loads(compare_result.compliance_matrix))
    else:
        similarity_matrix = np.array(compare_result.compliance_matrix)

    compare_info = CompareInfo(
        fast=FastMetrics(
            jakkar=float(compare_result.jakkar),
            operators=float(compare_result.operators),
            keywords=float(compare_result.keywords),
            literals=float(compare_result.literals),
            weighted_average=float(compare_result.weighted_average),
        ),
        structure=StructuresInfo(
            compliance_matrix=similarity_matrix,
            similarity=float(compare_result.struct_similarity),
        ),
    )

    return compare_info


def _get_current_date() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def serialize_compare_result_to_dict(
    compare_info: CompareInfo
) -> dict:
    assert compare_info.structure is not None

    data = {
        "fast" : dict(zip(
            list(compare_info.fast.__annotations__.keys()), list(compare_info.fast)
        )),
        "structure" : 
        {
            "similarity": compare_info.structure.similarity, 
            "compliance_matrix": compare_info.structure.compliance_matrix.tolist()
        }
    }

    return data


def deserialize_compare_result_from_dict(compare_result: dict) -> CompareInfo:
    structure_d = dict(compare_result["structure"])
    fast_d = dict(compare_result["fast"])

    compare_info = CompareInfo(
        fast=FastMetrics(
            jakkar=fast_d['jakkar'],
            operators=fast_d['operators'],
            keywords=fast_d['keywords'],
            literals=fast_d['literals'],
            weighted_average=fast_d['weighted_average'],
        ),
        structure=StructuresInfo(
            similarity=structure_d['similarity'],
            compliance_matrix=np.array(structure_d['compliance_matrix']),
        ),
    )

    return compare_info

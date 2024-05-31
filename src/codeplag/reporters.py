"""This module contains logic for saving a comparison result into JSON or CSV."""

import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Optional

import numpy as np
import pandas as pd

from codeplag.config import write_config
from codeplag.consts import CSV_REPORT_COLUMNS, CSV_REPORT_FILENAME, CSV_SAVE_TICK_SEC
from codeplag.logger import codeplag_logger as logger
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    FastMetrics,
    StructuresInfo,
    WorksReport,
)


class AbstractReporter(ABC):
    def __init__(self, reports: Path) -> None:
        self.reports = reports

    @abstractmethod
    def save_result(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
    ) -> None:
        ...


class CSVReporter(AbstractReporter):
    def __init__(self, reports: Path) -> None:
        super().__init__(reports)
        self.reports_path = self.reports / CSV_REPORT_FILENAME
        if self.reports_path.is_file():
            self.__df_report = read_df(self.reports_path)
            self.__start_report_lines = self.__df_report.shape[0]
        else:
            self.__df_report = pd.DataFrame(columns=CSV_REPORT_COLUMNS, dtype=object)
            self.__start_report_lines = 0
        self.__csv_last_save = monotonic()

    def save_result(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
    ) -> None:
        if not self.reports.is_dir():
            logger.error("The folder for reports isn't exists.")
            return
        self.__df_report = pd.concat(
            [
                self.__df_report,
                serialize_compare_result(first_work, second_work, compare_info),
            ],
            ignore_index=True,
        )
        if monotonic() - self.__csv_last_save > CSV_SAVE_TICK_SEC:
            self._write_df_to_fs()
            # Time to write can be long
            self.__csv_last_save = monotonic()

    def _write_df_to_fs(self) -> None:
        if self.__start_report_lines == self.__df_report.shape[0]:
            logger.debug("Nothing new to save to the csv report.")
            return

        logger.debug(f"Saving report to the file '{self.reports_path}'")
        self.__df_report.to_csv(self.reports_path, sep=";")
        self.__start_report_lines = self.__df_report.shape[0]

    def get_compare_result_from_cache(
        self, work1: ASTFeatures, work2: ASTFeatures
    ) -> Optional[CompareInfo]:
        cache_val = self.__df_report[
            (self.__df_report.first_path == str(work1.filepath))
            & (self.__df_report.second_path == str(work2.filepath))
        ]
        assert cache_val is not None
        if cache_val.shape[0]:
            return deserialize_compare_result(cache_val.iloc[0])


class JSONReporter(AbstractReporter):
    def save_result(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
    ) -> None:
        if not self.reports.is_dir():
            logger.error("The folder for reports isn't exists.")
            return
        assert compare_info.structure is not None

        struct_info_dict = compare_info.structure._asdict()
        struct_info_dict["compliance_matrix"] = struct_info_dict[
            "compliance_matrix"
        ].tolist()
        report = WorksReport(
            date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            first_path=first_work.filepath.__str__(),
            second_path=second_work.filepath.__str__(),
            first_heads=first_work.head_nodes,
            second_heads=second_work.head_nodes,
            fast=compare_info.fast._asdict(),
            structure=struct_info_dict,
        )
        if first_work.modify_date:
            report["first_modify_date"] = first_work.modify_date
        if second_work.modify_date:
            report["second_modify_date"] = second_work.modify_date

        try:
            report_file = self.reports / f"{uuid.uuid4().hex}.json"
            write_config(report_file, report)
        except PermissionError:
            logger.error("Not enough rights to write reports to the folder.")


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
            "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "first_modify_date": first_work.modify_date,
            "second_modify_date": second_work.modify_date,
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

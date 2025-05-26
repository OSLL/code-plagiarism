"""MIT License.

Written 2025 by Daniil Lokosov
"""

from typing_extensions import Self

from codeplag.db.mongo import (
    FeaturesRepository,
    ReportRepository,
)
from codeplag.types import ASTFeatures, FullCompareInfo


class ReportRepositoryStub(ReportRepository):
    def __init__(self: Self) -> None:
        self.dict = {}

    def write_compare_info(
        self: Self, work1: ASTFeatures, work2: ASTFeatures, compare_info: FullCompareInfo
    ) -> None:
        work1, work2 = sorted([work1, work2])
        first_path, second_path = [str(work1.filepath), str(work2.filepath)]

        document_id = first_path, second_path

        document = {
            "first_sha256": work1.sha256,
            "second_sha256": work2.sha256,
            "first_modify_date": work1.modify_date,
            "second_modify_date": work2.modify_date,
            "compare_info": compare_info,
        }

        self.dict[document_id] = document

    def get_compare_info(
        self: Self, work1: ASTFeatures, work2: ASTFeatures
    ) -> ReportRepository.CompareInfoDocument | None:
        work1, work2 = sorted([work1, work2])
        first_path, second_path = [str(work1.filepath), str(work2.filepath)]
        document_id = first_path, second_path

        document = self.dict.get(document_id)
        if not document:
            return None

        return ReportRepository.CompareInfoDocument(
            first_sha256=document["first_sha256"],
            second_sha256=document["second_sha256"],
            first_modify_date=document["first_modify_date"],
            second_modify_date=document["second_modify_date"],
            compare_info=document["compare_info"],
        )


class FeaturesRepositoryStub(FeaturesRepository):
    def __init__(self: Self) -> None:
        self.dict = {}

    def write_features(self: Self, work: ASTFeatures) -> None:
        document_id = str(work.filepath)

        self.dict[document_id] = work

    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None:
        document_id = str(work.filepath)

        return self.dict.get(document_id, None)

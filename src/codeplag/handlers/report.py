import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Literal, Tuple

import jinja2
import numpy as np
import pandas as pd
from numpy.typing import NDArray

from codeplag.config import read_settings_conf
from codeplag.consts import (
    CSV_REPORT_FILENAME,
    DEFAULT_GENERAL_REPORT_NAME,
    DEFAULT_LANGUAGE,
    DEFAULT_THRESHOLD,
    TEMPLATE_PATH,
)
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    FastMetrics,
    Language,
    SameFuncs,
    SameHead,
    StructuresInfo,
)


def html_report_create(report_path: Path, logger: logging.Logger) -> Literal[0, 1]:
    settings_config = read_settings_conf()
    reports_path = settings_config.get("reports")
    if not reports_path:
        logger.error(
            "Can't create general report without provided in settings 'report' path."
        )
        return 1
    if settings_config["reports_extension"] == "json":
        logger.error("Can create report only when 'reports_extension' is csv.")
        return 1
    if not reports_path.exists():
        logger.error(
            f"There is nothing in '{reports_path}' to create a basic html report from."
        )
        return 1
    _create_report(
        reports_path / CSV_REPORT_FILENAME,
        report_path,
        threshold=settings_config["threshold"],
        language=settings_config["language"],
    )
    return 0


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


def read_df(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", index_col=0, dtype=object)


def _convert_similarity_matrix_to_percent_matrix(matrix: NDArray) -> NDArray:
    """Convert compliance matrix of size N x M x 2 to percent 2 dimensional matrix."""
    percent_matrix = np.zeros((matrix.shape[0], matrix.shape[1]), dtype=np.float64)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            percent_matrix[i][j] = round(matrix[i][j][0] / matrix[i][j][1] * 100, 2)
    return percent_matrix


def _deserialize_head_nodes(head_nodes: str) -> List[str]:
    return [head[1:-1] for head in head_nodes[1:-1].split(", ")]


def _replace_minimal_value(same_parts: dict, new_key: str, new_value: float) -> None:
    min_key = next(iter(same_parts))
    min_value = same_parts[min_key]
    for key, value in same_parts.items():
        if value >= min_value:
            continue
        min_value = value
        min_key = key
    if new_value <= min_value:
        return
    del same_parts[min_key]
    same_parts[new_key] = new_value


def _get_same_funcs(
    first_heads: List[str],
    second_heads: List[str],
    percent_matrix: NDArray,
    threshold: int = DEFAULT_THRESHOLD,
    n: int = 3,
) -> SameFuncs:
    result = {}
    for i, first_head in enumerate(first_heads):
        result[first_head] = {}
        inner_result = result[first_head]
        for j, second_head in enumerate(second_heads):
            same_percent = percent_matrix[i][j]
            cnt_items = len(inner_result)
            if not cnt_items:
                inner_result[second_head] = same_percent
            elif same_percent < threshold:
                if (
                    cnt_items == 1
                    and inner_result[(key := next(iter(inner_result)))] < same_percent
                ):
                    inner_result[second_head] = same_percent
                    del inner_result[key]
                continue
            elif cnt_items < n:
                inner_result[second_head] = same_percent
            else:
                _replace_minimal_value(inner_result, second_head, same_percent)
    for first_head in result:
        result[first_head] = sorted(
            (SameHead(key, value) for key, value in result[first_head].items()),
            key=lambda element: element.percent,
            reverse=True,
        )
    return result


def _get_parsed_line(
    df: pd.DataFrame,
) -> Generator[Tuple[pd.Series, CompareInfo, SameFuncs, SameFuncs], None, None]:
    for _, line in df.iterrows():
        cmp_res = deserialize_compare_result(line)
        first_heads = _deserialize_head_nodes(line.first_heads)
        second_heads = _deserialize_head_nodes(line.second_heads)
        assert cmp_res.structure is not None
        percent_matrix = _convert_similarity_matrix_to_percent_matrix(
            cmp_res.structure.compliance_matrix
        )
        same_parts_of_second = _get_same_funcs(
            first_heads, second_heads, percent_matrix
        )
        same_parts_of_first = _get_same_funcs(
            second_heads, first_heads, percent_matrix.T
        )
        if isinstance(line.first_modify_date, float):
            line.first_modify_date = ""
        if isinstance(line.second_modify_date, float):
            line.second_modify_date = ""
        yield line, cmp_res, same_parts_of_second, same_parts_of_first


def _create_report(
    df_path: Path,
    save_path: Path,
    threshold: int = DEFAULT_THRESHOLD,
    language: Language = DEFAULT_LANGUAGE,
):
    environment = jinja2.Environment()
    # TODO: use JinJa2 i18n
    template = environment.from_string(TEMPLATE_PATH[language].read_text())
    if save_path.is_dir():
        save_path = save_path / DEFAULT_GENERAL_REPORT_NAME
    save_path.write_text(
        template.render(
            data=_get_parsed_line(read_df(df_path)),
            list=list,
            len=len,
            round=round,
            threshold=threshold,
        )
    )

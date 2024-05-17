"""This module contains handlers for the report command of the CLI."""

from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Dict, Generator, List, Literal, Tuple, TypedDict

import jinja2
import numpy as np
import pandas as pd
from numpy.typing import NDArray

from codeplag.config import read_settings_conf
from codeplag.consts import (
    CSV_REPORT_FILENAME,
    DEFAULT_GENERAL_REPORT_NAME,
    DEFAULT_LANGUAGE,
    DEFAULT_SOURCES_REPORT_NAME,
    DEFAULT_THRESHOLD,
    GENERAL_TEMPLATE_PATH,
    SOURCES_TEMPLATE_PATH,
)
from codeplag.logger import codeplag_logger as logger
from codeplag.reporters import deserialize_compare_result, read_df
from codeplag.translate import get_translations
from codeplag.types import (
    CompareInfo,
    Language,
    ReportType,
    SameFuncs,
    SameHead,
)


def html_report_create(report_path: Path, report_type: ReportType) -> Literal[0, 1]:
    """Creates an HTML report based on the configuration settings.

    Args:
    ----
        report_path: The path where the report should be created.
        report_type: Type of the created report file.

    Returns:
    -------
        Literal[0, 1]: 0 if the report was successfully created, 1 otherwise.

    Example usage:
        >>> from pathlib import Path
        >>> html_report_create(Path('/path/to/report'))
        0

    """
    settings_config = read_settings_conf()
    reports_path = settings_config.get("reports")
    if not reports_path:
        logger.error(
            "Can't create general report without provided in settings 'report' path."
        )
        return 1
    if settings_config["reports_extension"] != "csv":
        logger.error("Can create report only when 'reports_extension' is csv.")
        return 1
    if not reports_path.exists():
        logger.error(
            f"There is nothing in '{reports_path}' to create a basic html report from."
        )
        return 1
    if report_type == "general":
        create_report_function = _create_report
    else:
        create_report_function = _create_sources_report
    create_report_function(
        reports_path / CSV_REPORT_FILENAME,
        report_path,
        settings_config["threshold"],
        settings_config["language"],
    )
    return 0


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
    include_funcs_less_threshold: bool = True,
    n: int = 3,
) -> SameFuncs:
    result = {}
    for i, first_head in enumerate(first_heads):
        result[first_head] = {}
        inner_result = result[first_head]
        for j, second_head in enumerate(second_heads):
            same_percent = percent_matrix[i][j]
            cnt_items = len(inner_result)
            if not cnt_items and include_funcs_less_threshold:
                inner_result[second_head] = same_percent
            elif same_percent < threshold:
                # This logic runs only when 'include_funcs_less_threshold' is True
                if (
                    cnt_items == 1
                    and inner_result[(key := next(iter(inner_result)))] < same_percent
                ):
                    inner_result[second_head] = same_percent
                    del inner_result[key]
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
    threshold: int = DEFAULT_THRESHOLD,
    include_funcs_less_threshold: bool = True,
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
            first_heads,
            second_heads,
            percent_matrix,
            threshold,
            include_funcs_less_threshold,
        )
        same_parts_of_first = _get_same_funcs(
            second_heads,
            first_heads,
            percent_matrix.T,
            threshold,
            include_funcs_less_threshold,
        )
        if isinstance(line.first_modify_date, float):
            line.first_modify_date = ""
        if isinstance(line.second_modify_date, float):
            line.second_modify_date = ""
        yield line, cmp_res, same_parts_of_second, same_parts_of_first


class Elements(TypedDict):
    cnt_elements: int
    same_parts: SameFuncs


SamePartsOfAll = Dict[str, Dict[str, Elements]]


def _search_sources(
    df: pd.DataFrame, threshold: int = DEFAULT_THRESHOLD
) -> SamePartsOfAll:
    same_parts_of_all: SamePartsOfAll = defaultdict(lambda: {})
    for line, _, same_parts_of_second, same_parts_of_first in _get_parsed_line(
        df, threshold, include_funcs_less_threshold=False
    ):
        same_parts_of_all[line.first_path][line.second_path] = Elements(
            cnt_elements=0, same_parts=deepcopy(same_parts_of_second)
        )
        same_parts_of_all[line.second_path][line.first_path] = Elements(
            cnt_elements=0, same_parts=deepcopy(same_parts_of_first)
        )
        for function, same_functions in same_parts_of_second.items():
            cnt_same_functions = len(same_functions)
            if cnt_same_functions == 0:
                same_parts_of_all[line.first_path][line.second_path]["same_parts"].pop(
                    function
                )
                continue
            same_parts_of_all[line.first_path][line.second_path][
                "cnt_elements"
            ] += cnt_same_functions
        for function, same_functions in same_parts_of_first.items():
            cnt_same_functions = len(same_functions)
            if cnt_same_functions == 0:
                same_parts_of_all[line.second_path][line.first_path]["same_parts"].pop(
                    function
                )
                continue
            same_parts_of_all[line.second_path][line.first_path][
                "cnt_elements"
            ] += cnt_same_functions
        if same_parts_of_all[line.first_path][line.second_path]["cnt_elements"] == 0:
            del same_parts_of_all[line.first_path][line.second_path]
        if same_parts_of_all[line.second_path][line.first_path]["cnt_elements"] == 0:
            del same_parts_of_all[line.second_path][line.first_path]
    same_parts_of_all = {k: v for k, v in same_parts_of_all.items() if v}
    return same_parts_of_all


def _create_report(
    df_path: Path,
    save_path: Path,
    threshold: int = DEFAULT_THRESHOLD,
    language: Language = DEFAULT_LANGUAGE,
):
    environment = jinja2.Environment(extensions=["jinja2.ext.i18n"])
    environment.install_gettext_translations(get_translations())  # type: ignore
    template = environment.from_string(GENERAL_TEMPLATE_PATH.read_text())
    if save_path.is_dir():
        save_path = save_path / DEFAULT_GENERAL_REPORT_NAME
    save_path.write_text(
        template.render(
            data=_get_parsed_line(read_df(df_path)),
            list=list,
            len=len,
            round=round,
            threshold=threshold,
            language=language,
        )
    )


def _create_sources_report(
    df_path: Path,
    save_path: Path,
    threshold: int = DEFAULT_THRESHOLD,
    language: Language = DEFAULT_LANGUAGE,
) -> None:
    data = _search_sources(read_df(df_path), threshold)
    environment = jinja2.Environment(extensions=["jinja2.ext.i18n"])
    environment.install_gettext_translations(get_translations())  # type: ignore
    template = environment.from_string(SOURCES_TEMPLATE_PATH.read_text())
    if save_path.is_dir():
        save_path = save_path / DEFAULT_SOURCES_REPORT_NAME
    save_path.write_text(
        template.render(
            data=data,
            language=language,
            enumerate=enumerate,
            Path=Path,
            list=list,
            len=len,
            round=round,
        )
    )

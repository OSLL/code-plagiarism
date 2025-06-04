"""This module contains handlers for the report command of the CLI."""

from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Generator, TypedDict, Literal

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
    ExitCode,
    FullCompareInfo,
    Language,
    ReportType,
    SameFuncs,
    SameHead,
    Threshold,
)


class Elements(TypedDict):
    cnt_elements: int
    same_parts: SameFuncs
    max_funcs_same_percentages: dict[str, float]


SamePartsOfAll = dict[str, dict[str, Elements]]
CntHeadNodes = dict[str, int]
ResultingSamePercentages = dict[str, float]


def html_report_create(
    report_path: Path,
    report_type: ReportType,
    first_root_path: Path | str | None = None,
    second_root_path: Path | str | None = None,
) -> Literal[ExitCode.EXIT_INVAL] | Literal[ExitCode.EXIT_SUCCESS]:
    """Creates an HTML report based on the configuration settings.

    Args:
    ----
        report_path (Path): The path where the report should be created.
        report_type (ReportType): Type of the created report file.
        first_root_path (Path | str | None): Path to first compared works.
        second_root_path (Path | str | None): Path to second compared works.

    Returns:
    -------
        ExitCode: 'EXIT_SUCCESS' if the report was successfully created or another value when
          an error occurred.

    Raises:
    -------
        ValueError: When provided invalid report type or only one path.

    Example usage:
        >>> from pathlib import Path
        >>> html_report_create(Path('/path/to/report'), 'general')
        <ExitCode.EXIT_SUCCESS: 0>

    """
    settings_config = read_settings_conf()
    reports_extension = settings_config["reports_extension"]
    if reports_extension == "csv":
        reports_path = settings_config.get("reports")
        if not reports_path:
            logger.error(
                "Can't create general report without provided in settings 'report' path."
            )
            return ExitCode.EXIT_INVAL
        if reports_path.is_dir():
            reports_path = reports_path / CSV_REPORT_FILENAME
        if not reports_path.exists():
            logger.error(f"There is nothing in '{reports_path}' to create a basic html report from.")
            return ExitCode.EXIT_INVAL
        return __html_report_create_from_csv(
            report_path,
            reports_path,
            report_type,
            settings_config["threshold"],
            settings_config["language"],
            first_root_path,
            second_root_path
        )
    elif reports_extension == "mongo":
        logger.error("Not implemented 'mongo' reports.")
        return ExitCode.EXIT_INVAL
    else:
        logger.error(
            f"Can create report only when 'reports_extension' in ('csv', 'mongo'). "
            f"Provided '{reports_extension}'."
        )
        return ExitCode.EXIT_INVAL


def calculate_general_total_similarity(
    df: pd.DataFrame, unique_first_paths: NDArray, unique_second_paths: NDArray
) -> float:
    total_similarity = 0.0
    if unique_first_paths.size == 0:
        return total_similarity
    for first_path in unique_first_paths:
        max_similarity = 0.0
        for second_path in unique_second_paths:
            sorted_paths = sorted([first_path, second_path])
            selected = df[
                (df["first_path"].str.startswith(sorted_paths[0]))  # type: ignore
                & (df["second_path"].str.startswith(sorted_paths[1]))  # type: ignore
            ]
            if selected is None or selected.size == 0:
                continue
            module_similarity = float(selected.iloc[0]["weighted_average"])
            if module_similarity > max_similarity:
                max_similarity = module_similarity
        total_similarity += max_similarity
    return round(total_similarity / unique_first_paths.size * 100, 2)


def calculate_sources_total_similarity(
    same_percentages: ResultingSamePercentages,
    pattern: str,
) -> float:
    item_cnt = 0
    total_similarity = 0.0
    for path, percentage in same_percentages.items():
        if not path.startswith(pattern):
            continue
        total_similarity += percentage
        item_cnt += 1
    if item_cnt == 0:
        return 0.0
    return round(total_similarity / item_cnt, 2)


def _convert_similarity_matrix_to_percent_matrix(matrix: NDArray) -> NDArray:
    """Convert compliance matrix of size N x M x 2 to percent 2 dimensional matrix."""
    percent_matrix = np.empty((matrix.shape[0], matrix.shape[1]), dtype=np.float64)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            percent_matrix[i][j] = round(matrix[i][j][0] / matrix[i][j][1] * 100, 2)
    return percent_matrix


def _deserialize_head_nodes(head_nodes: str) -> list[str]:
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
    first_heads: list[str],
    second_heads: list[str],
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
) -> Generator[tuple[pd.Series, FullCompareInfo, SameFuncs, SameFuncs], None, None]:
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
        yield line, cmp_res, same_parts_of_second, same_parts_of_first


def _get_resulting_same_percentages(
    same_parts_of_all: SamePartsOfAll, cnt_head_nodes: CntHeadNodes
) -> ResultingSamePercentages:
    resulting_same_percentages: ResultingSamePercentages = {}
    for first_path, same_works in same_parts_of_all.items():
        max_funcs_same_percentages = {}
        for second_work in same_works.values():
            for function, same_percentage in second_work["max_funcs_same_percentages"].items():
                if same_percentage <= max_funcs_same_percentages.get(function, 0):
                    continue
                max_funcs_same_percentages[function] = same_percentage
        resulting_percentage = round(
            sum(max_funcs_same_percentages.values()) / cnt_head_nodes[first_path],
            2,
        )
        resulting_same_percentages[first_path] = resulting_percentage
    return resulting_same_percentages


def _search_sources(
    df: pd.DataFrame, threshold: int = DEFAULT_THRESHOLD
) -> tuple[SamePartsOfAll, CntHeadNodes]:
    same_parts_of_all: SamePartsOfAll = defaultdict(lambda: {})
    cnt_head_nodes: CntHeadNodes = {}
    for line, _, same_parts_of_second, same_parts_of_first in _get_parsed_line(
        df, threshold, include_funcs_less_threshold=False
    ):
        for path, heads in zip(
            (line.first_path, line.second_path),
            (line.first_heads, line.second_heads),
            strict=True,
        ):
            if path in cnt_head_nodes:
                continue
            cnt_head_nodes[path] = len(_deserialize_head_nodes(heads))
        for first_path, second_path, same_parts in (
            (line.first_path, line.second_path, same_parts_of_second),
            (line.second_path, line.first_path, same_parts_of_first),
        ):
            element = same_parts_of_all[first_path][second_path] = Elements(
                cnt_elements=0,
                same_parts=deepcopy(same_parts),
                max_funcs_same_percentages={},
            )
            for function, same_functions in same_parts.items():
                if (cnt_same_functions := len(same_functions)) == 0:
                    element["same_parts"].pop(function)
                    continue
                element["max_funcs_same_percentages"][function] = max(
                    same_function.percent for same_function in same_functions
                )
                element["cnt_elements"] += cnt_same_functions
            if element["cnt_elements"] == 0:
                del same_parts_of_all[first_path][second_path]

    return {k: v for k, v in same_parts_of_all.items() if v}, cnt_head_nodes


def _create_general_report(
    df: pd.DataFrame,
    save_path: Path,
    environment: jinja2.Environment,
    threshold: Threshold = DEFAULT_THRESHOLD,
    language: Language = DEFAULT_LANGUAGE,
    paths: tuple[str, str] | None = None,
) -> None:
    if paths is not None:
        unique_first_paths = pd.unique(df["first_path"])
        unique_second_paths = pd.unique(df["second_path"])
        assert isinstance(unique_first_paths, np.ndarray)
        assert isinstance(unique_second_paths, np.ndarray)
        first_root_path_sim = calculate_general_total_similarity(
            df, unique_first_paths, unique_second_paths
        )
        second_root_path_sim = calculate_general_total_similarity(
            df, unique_second_paths, unique_first_paths
        )
    else:
        first_root_path_sim = None
        second_root_path_sim = None
    template = environment.from_string(GENERAL_TEMPLATE_PATH.read_text())
    if save_path.is_dir():
        save_path = save_path / DEFAULT_GENERAL_REPORT_NAME
    save_path.write_text(
        template.render(
            data=_get_parsed_line(df),
            list=list,
            len=len,
            round=round,
            threshold=threshold,
            language=language,
            first_root_path_sim=first_root_path_sim,
            second_root_path_sim=second_root_path_sim,
            paths=paths,
        )
    )


def _create_sources_report(
    df: pd.DataFrame,
    save_path: Path,
    environment: jinja2.Environment,
    threshold: Threshold = DEFAULT_THRESHOLD,
    language: Language = DEFAULT_LANGUAGE,
    paths: tuple[str, str] | None = None,
) -> None:
    data, cnt_head_nodes = _search_sources(df, threshold)
    same_percentages = _get_resulting_same_percentages(data, cnt_head_nodes)
    if paths is not None:
        first_root_path_sim = calculate_sources_total_similarity(same_percentages, paths[0])
        second_root_path_sim = calculate_sources_total_similarity(same_percentages, paths[1])
    else:
        first_root_path_sim = None
        second_root_path_sim = None
    template = environment.from_string(SOURCES_TEMPLATE_PATH.read_text())
    if save_path.is_dir():
        save_path = save_path / DEFAULT_SOURCES_REPORT_NAME
    save_path.write_text(
        template.render(
            data=data,
            same_percentages=same_percentages,
            threshold=threshold,
            language=language,
            enumerate=enumerate,
            Path=Path,
            list=list,
            len=len,
            round=round,
            first_root_path_sim=first_root_path_sim,
            second_root_path_sim=second_root_path_sim,
            paths=paths,
        )
    )


def __html_report_create_from_csv(
    report_path: Path,
    reports_path: Path,
    report_type: ReportType,
    threshold: Threshold,
    language: Language,
    first_root_path: Path | str | None = None,
    second_root_path: Path | str | None = None,
) -> Literal[ExitCode.EXIT_SUCCESS]:
    if report_type == "general":
        create_report_function = _create_general_report
    elif report_type == "sources":
        create_report_function = _create_sources_report
    else:
        raise ValueError(_("Invalid report type."))
    all_paths_provided = all([first_root_path, second_root_path])
    if not all_paths_provided and any([first_root_path, second_root_path]):
        raise ValueError(_("All paths must be provided."))

    df = read_df(reports_path)
    if all_paths_provided:
        paths = tuple(sorted([str(first_root_path), str(second_root_path)]))
        df = df[df["first_path"].str.startswith(paths[0])]  # type: ignore
        df = df[df["second_path"].str.startswith(paths[1])]  # type: ignore
    else:
        paths = None
    environment = jinja2.Environment(extensions=["jinja2.ext.i18n"])
    environment.install_gettext_translations(get_translations())  # type: ignore
    create_report_function(
        df,  # type:ignore
        report_path,
        environment,
        threshold,
        language,
        paths,  # type: ignore
    )
    return ExitCode.EXIT_SUCCESS

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from codeplag.handlers.report import (
    CntHeadNodes,
    ResultingSamePercentages,
    SamePartsOfAll,
    _convert_similarity_matrix_to_percent_matrix,
    _get_parsed_line,
    _get_resulting_same_percentages,
    _get_same_funcs,
    _replace_minimal_value,
    calculate_general_total_similarity,
    calculate_sources_total_similarity,
)
from codeplag.reporters import serialize_compare_result
from codeplag.types import FullCompareInfo, SameHead


@pytest.mark.parametrize(
    ("same_percentages", "pattern", "expected"),
    [
        ({}, "pattern", 0.0),
        (
            {
                "/usr/codeplag/marshal.py": 80.0,
                "/usr/codeplag/featurebased.py": 81.25,
                "/home/band/setup.py": 50.0,
            },
            "/usr/codeplag",
            80.62,
        ),
    ],
)
def test_calculate_sources_total_similarity(
    same_percentages: ResultingSamePercentages, pattern: str, expected: float
):
    assert calculate_sources_total_similarity(same_percentages, pattern) == expected


@pytest.mark.parametrize(
    ("df", "unique_first_paths", "unique_second_paths", "expected"),
    [
        (pd.DataFrame({}), np.array([]), np.array([]), 0.0),
        (
            pd.DataFrame(
                {
                    "first_path": ["a.py", "b.py", "a.py"],
                    "second_path": ["c.py", "d.py", "e.py"],
                    "weighted_average": [0.15, 0.1, 0.3],
                }
            ),
            np.array(["a.py", "b.py"]),
            np.array(["c.py", "d.py", "e.py"]),
            20.0,
        ),
        (
            pd.DataFrame(
                {
                    "first_path": ["a.py", "b.py", "a.py"],
                    "second_path": ["c.py", "d.py", "e.py"],
                    "weighted_average": [0.15, 0.1, 0.3],
                }
            ),
            np.array(["c.py", "d.py", "e.py"]),
            np.array(["a.py", "b.py"]),
            18.33,
        ),
    ],
)
def test_calculate_general_total_similarity(
    df: pd.DataFrame,
    unique_first_paths: np.ndarray,
    unique_second_paths: np.ndarray,
    expected: float,
):
    assert (
        calculate_general_total_similarity(df, unique_first_paths, unique_second_paths) == expected
    )


@pytest.mark.parametrize(
    ("same_parts", "new_key", "new_value", "expected"),
    [
        ({"foo": 10.1, "bar": 20.5}, "foorbar", 30.5, {"bar": 20.5, "foorbar": 30.5}),
        ({"foo": 30.1, "bar": 20.5}, "foobar", 5.5, {"foo": 30.1, "bar": 20.5}),
    ],
    ids=[
        "'foo' replaced with 'foobar'",
        "new value is smaller than provided and not inserted",
    ],
)
def test__replace_minimal_value(
    same_parts: dict[str, float],
    new_key: str,
    new_value: float,
    expected: dict[str, float],
):
    _replace_minimal_value(same_parts, new_key, new_value)

    assert same_parts == expected


@pytest.mark.parametrize(
    ("first_heads", "second_heads", "threshold", "include_funcs_less_threshold", "n", "expected"),
    [
        (
            ["foo", "bar", "foobar", "barfoo"],
            ["func_name", "sum", "mult", "div", "sub"],
            70,
            True,
            2,
            {
                "foo": [SameHead("sub", 50.0)],
                "bar": [SameHead("div", 80.0), SameHead("sum", 74.0)],
                "foobar": [SameHead("sub", 90.0), SameHead("div", 85.0)],
                "barfoo": [SameHead("func_name", 40.0)],
            },
        ),
        (
            ["foo", "bar", "foobar", "barfoo"],
            ["func_name", "sum", "mult", "div", "sub"],
            70,
            False,
            2,
            {
                "foo": [],
                "bar": [SameHead("div", 80.0), SameHead("sum", 74.0)],
                "foobar": [SameHead("sub", 90.0), SameHead("div", 85.0)],
                "barfoo": [],
            },
        ),
    ],
    ids=[
        "Same functions with less threshold.",
        "Same functions without less threshold.",
    ],
)
def test__get_same_funcs(
    first_heads: list[str],
    second_heads: list[str],
    threshold: int,
    include_funcs_less_threshold: bool,
    n: int,
    expected: dict[str, list[SameHead]],
):
    percent_matrix = np.array(
        [
            [10.0, 20.0, 30.0, 40.0, 50.0],
            [72.0, 74.0, 3.0, 80.0, 5.0],
            [70.0, 75.0, 80.0, 85.0, 90.0],
            [40.0, 30.0, 20.0, 10.0, 10.0],
        ]
    )

    result = _get_same_funcs(
        first_heads,
        second_heads,
        percent_matrix,
        threshold,
        include_funcs_less_threshold,
        n,
    )
    assert expected == result


def test__get_parsed_line(first_compare_result: FullCompareInfo) -> None:
    compare_df = serialize_compare_result(first_compare_result)
    compare_df.iloc[0].first_heads = str(compare_df.iloc[0].first_heads)
    compare_df.iloc[0].second_heads = str(compare_df.iloc[0].second_heads)

    result = list(_get_parsed_line(compare_df, compare_df.iterrows))

    assert result[0][0].fast == first_compare_result.fast
    assert result[0][0].structure
    assert result[0][0].structure.similarity == first_compare_result.structure.similarity
    assert result[0][0].structure.similarity == first_compare_result.structure.similarity
    assert np.array_equal(
        result[0][0].structure.compliance_matrix,
        first_compare_result.structure.compliance_matrix,
    )
    assert result[0][1] == {
        "my_func[1]": [SameHead(name="my_func[1]", percent=79.17)],
        "If[7]": [
            SameHead(name="If[7]", percent=88.89),
            SameHead(name="my_func[1]", percent=18.52),
        ],
    }
    assert result[0][2] == {
        "my_func[1]": [SameHead(name="my_func[1]", percent=79.17)],
        "If[7]": [
            SameHead(name="If[7]", percent=88.89),
            SameHead(name="my_func[1]", percent=33.33),
        ],
    }


@pytest.mark.parametrize(
    ("same_parts_of_all", "cnt_head_nodes", "expected"),
    [
        (
            {
                "marshal.py": {
                    "config.py": {
                        "cnt_elements": 1,
                        "max_funcs_same_percentages": {"FEATURES_GETTERS[9]": 80.0},
                    }
                },
                "featurebased.py": {
                    "featurebased_ob.py": {
                        "cnt_elements": 7,
                        "max_funcs_same_percentages": {
                            "add_not_counted[166]": 95.0,
                            "counter_metric[4]": 88.0,
                            "find_max_index[112]": 75.0,
                            "get_children_indexes[87]": 84.0,
                            "matrix_value[137]": 100.0,
                            "op_shift_metric[37]": 90.0,
                            "struct_compare[191]": 87.0,
                        },
                    },
                    "featurebased_rn.py": {
                        "cnt_elements": 7,
                        "max_funcs_same_percentages": {
                            "add_not_counted[166]": 80.0,
                            "counter_metric[4]": 86.0,
                            "find_max_index[112]": 78.0,
                            "get_children_indexes[87]": 95.0,
                            "matrix_value[137]": 100.0,
                            "op_shift_metric[37]": 77.0,
                            "struct_compare[191]": 86.0,
                        },
                    },
                    "featurebased_rn_ob.py": {
                        "cnt_elements": 7,
                        "max_funcs_same_percentages": {
                            "add_not_counted[166]": 95.0,
                            "counter_metric[4]": 100.0,
                            "find_max_index[112]": 73.0,
                            "get_children_indexes[87]": 100.0,
                            "matrix_value[137]": 64.0,
                            "op_shift_metric[37]": 70.0,
                            "struct_compare[191]": 80.0,
                        },
                    },
                    "marshal.py": {
                        "cnt_elements": 0,
                        "max_funcs_same_percentages": {},
                    },
                },
            },
            {
                "marshal.py": 1,
                "featurebased.py": 8,
            },
            {"marshal.py": 80.0, "featurebased.py": 81.25},
        )
    ],
)
def test__get_resulting_same_percentages(
    same_parts_of_all: SamePartsOfAll,
    cnt_head_nodes: CntHeadNodes,
    expected: ResultingSamePercentages,
):
    assert _get_resulting_same_percentages(same_parts_of_all, cnt_head_nodes) == expected


def test__convert_similarity_matrix_to_percent_matrix():
    assert _convert_similarity_matrix_to_percent_matrix(
        np.array([[[1, 2], [1, 3], [3, 4]], [[1, 8], [1, 4], [3, 5]]])
    ).tolist() == [[50.0, 33.33, 75.0], [12.5, 25.0, 60.0]]

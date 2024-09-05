import numpy as np
import pandas as pd
import pytest
from codeplag.handlers.check import (
    _calc_iterations,
    compliance_matrix_to_df,
)
from codeplag.types import Mode
from pandas.testing import assert_frame_equal


@pytest.mark.parametrize(
    "count, mode, expected",
    [
        (10, "many_to_many", 45),
        (3, "one_to_one", 3),
        (-100, "many_to_many", 0),
        (0, "one_to_one", 0),
        (-10, "bad_mode", 0),
    ],
)
def test__calc_iterations(count: int, mode: Mode, expected: int):
    assert _calc_iterations(count, mode) == expected


def test__calc_iterations_bad():
    with pytest.raises(ValueError):
        _calc_iterations(100, "bad_mode")  # type: ignore


def test_compliance_matrix_to_df():
    compliance_matrix = np.array([[[1, 2], [1, 10], [3, 4]], [[1, 8], [1, 4], [3, 5]]])
    heads1 = ["get_value", "set_value"]
    heads2 = ["getter", "setter", "returner"]

    assert_frame_equal(
        compliance_matrix_to_df(compliance_matrix, heads1, heads2),
        pd.DataFrame(data=[[0.5, 0.1, 0.75], [0.125, 0.25, 0.6]], index=heads1, columns=heads2),
    )

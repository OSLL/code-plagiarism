from typing import List

import pytest
from codeplag.display import _calc_progress


@pytest.mark.parametrize(
    "args, result",
    [([4, 10], 0.4), ([10, 0], 0.0), ([5, 10, 15, 0], 0.5), ([5, 6, 1, 4], 0.875)],
)
def test_calc_progress(args: List[int], result: float):
    assert _calc_progress(*args) == result

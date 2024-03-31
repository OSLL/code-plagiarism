import pytest
from codeplag.display import ComplexProgress, Progress


def create_progress(iterations: int, iteration: int = 0) -> Progress:
    progress = Progress(iterations)
    assert progress.iterations == iterations
    progress._Progress__iteration = iteration
    return progress


def create_complex_progress(
    common_iterations: int = 0,
    common_iteration: int = 0,
    internal_iterations: int = 0,
    internal_iteration: int = 0,
) -> ComplexProgress:
    internal_progress = create_progress(internal_iterations, internal_iteration)
    complex_progress = ComplexProgress(common_iterations)
    assert complex_progress.iterations == common_iterations
    complex_progress._ComplexProgress__internal_progresses = [internal_progress]
    for _ in range(common_iteration):
        complex_progress.add_internal_progress(0)
    return complex_progress


class TestProgress:
    def test_check_progress_increased(self):
        iterations = 5
        progress = Progress(iterations)
        for real_percent, expect_percent in zip(
            progress, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        ):
            assert real_percent == expect_percent
            assert str(progress) == f"Progress: {expect_percent:.2%}"

    def test_progress_increase_failed(self):
        progress = create_progress(0, 0)
        with pytest.raises(StopIteration):
            next(progress)

    def test_can_not_change_iterations(self):
        with pytest.raises(AttributeError):
            Progress(10).iterations = 10


class TestComplexProgress:
    @pytest.mark.parametrize(
        "complex_progress,result",
        [
            (
                create_complex_progress(
                    common_iterations=10, common_iteration=4, internal_iterations=1
                ),
                0.4,
            ),
            (create_complex_progress(common_iterations=0, common_iteration=10), 1.0),
            (
                create_complex_progress(
                    common_iterations=10, common_iteration=5, internal_iterations=15
                ),
                0.5,
            ),
            (
                create_complex_progress(
                    common_iterations=6,
                    common_iteration=5,
                    internal_iterations=4,
                    internal_iteration=1,
                ),
                0.875,
            ),
        ],
    )
    def test_complex_progress(self, complex_progress: ComplexProgress, result: float):
        assert str(complex_progress) == f"Progress: {result:.2%}"

    @pytest.mark.parametrize(
        "progress",
        [
            (create_complex_progress()),
            (create_complex_progress(internal_iterations=10)),
        ],
        ids=[
            "Internal and common progress is zero.",
            "Only common progress is zero",
        ],
    )
    def test_progress_increase_failed(self, progress: ComplexProgress):
        with pytest.raises(StopIteration):
            next(progress)

    def test_can_not_change_iterations(self):
        with pytest.raises(AttributeError):
            ComplexProgress(10).iterations = 10

    def test_check_progress_increased(self):
        iterations = 5
        progress = ComplexProgress(iterations)
        progress.add_internal_progress(4)
        progress.add_internal_progress(5)
        progress.add_internal_progress(2)
        progress.add_internal_progress(1)
        progress.add_internal_progress(1)
        for real_percent, expect_percent in zip(
            progress,
            [
                0.0,
                0.05,
                0.1,
                0.15,
                0.2,
                0.24,
                0.28,
                0.32,
                0.36,
                0.4,
                0.5,
                0.6,
                0.8,
                1.0,
            ],
        ):
            assert real_percent == pytest.approx(expect_percent)
            assert str(progress) == f"Progress: {expect_percent:.2%}"
        with pytest.raises(StopIteration):
            next(progress)

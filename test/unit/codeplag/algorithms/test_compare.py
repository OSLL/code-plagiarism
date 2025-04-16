import pytest
from typing_extensions import Self

from codeplag.algorithms.compare import compare_works, fast_compare
from codeplag.types import ASTFeatures, FastCompareInfo, FullCompareInfo


class TestCompareWorks:
    def test_compare_works_with_structure(self: Self, first_compare_result: FullCompareInfo):
        assert first_compare_result.fast.jakkar == pytest.approx(0.737, 0.001)
        assert first_compare_result.fast.operators == pytest.approx(0.667, 0.001)
        assert first_compare_result.fast.keywords == 1.0
        assert first_compare_result.fast.literals == 0.75
        assert first_compare_result.fast.weighted_average == pytest.approx(0.774, 0.001)
        assert first_compare_result.structure is not None
        assert first_compare_result.structure.similarity == pytest.approx(0.823, 0.001)
        assert first_compare_result.structure.compliance_matrix.tolist() == [
            [[19, 24], [7, 21]],
            [[5, 27], [8, 9]],
        ]

    def test_compare_works_without_structure(
        self: Self,
        first_features: ASTFeatures,
        third_features: ASTFeatures,
    ):
        compare_info = compare_works(
            features1=first_features, features2=third_features, threshold=60
        )

        assert isinstance(compare_info, FastCompareInfo)
        assert compare_info.jakkar == 0.24
        assert compare_info.operators == 0.0
        assert compare_info.keywords == 0.6
        assert compare_info.literals == 0.0
        assert compare_info.weighted_average == pytest.approx(0.218, 0.001)


class TestFastCompare:
    def test_fast_compare_with_default_weights(
        self: Self, first_features: ASTFeatures, second_features: ASTFeatures
    ):
        metrics = fast_compare(first_features, second_features)

        assert metrics.jakkar == pytest.approx(0.737, 0.001)
        assert metrics.operators == pytest.approx(0.667, 0.001)
        assert metrics.keywords == 1.0
        assert metrics.literals == 0.75
        assert metrics.weighted_average == pytest.approx(0.774, 0.001)

    def test_fast_compare_with_different_weights(
        self: Self, first_features: ASTFeatures, second_features: ASTFeatures
    ):
        metrics = fast_compare(first_features, second_features, weights=(0.5, 0.6, 0.7, 0.8))

        assert metrics.weighted_average == pytest.approx(0.796, 0.001)

import pytest
from codeplag.algorithms.compare import compare_works, fast_compare
from codeplag.types import ASTFeatures


def test_compare_works(
    first_features: ASTFeatures,
    second_features: ASTFeatures,
    third_features: ASTFeatures,
):
    compare_info = compare_works(first_features, second_features)

    assert compare_info.fast.jakkar == pytest.approx(0.737, 0.001)
    assert compare_info.fast.operators == pytest.approx(0.667, 0.001)
    assert compare_info.fast.keywords == 1.0
    assert compare_info.fast.literals == 0.75
    assert compare_info.fast.weighted_average == pytest.approx(0.774, 0.001)
    assert compare_info.structure is not None
    assert compare_info.structure.similarity == pytest.approx(0.823, 0.001)
    assert compare_info.structure.compliance_matrix.tolist() == [
        [[19, 24], [7, 21]],
        [[5, 27], [8, 9]],
    ]

    compare_info2 = compare_works(first_features, third_features, 60)

    assert compare_info2.fast.jakkar == 0.24
    assert compare_info2.fast.operators == 0.0
    assert compare_info2.fast.keywords == 0.6
    assert compare_info2.fast.literals == 0.0
    assert compare_info2.fast.weighted_average == pytest.approx(0.218, 0.001)
    assert compare_info2.structure is None


def test_fast_compare_normal(first_features: ASTFeatures, second_features: ASTFeatures):
    metrics = fast_compare(first_features, second_features)

    assert metrics.jakkar == pytest.approx(0.737, 0.001)
    assert metrics.operators == pytest.approx(0.667, 0.001)
    assert metrics.keywords == 1.0
    assert metrics.literals == 0.75
    assert metrics.weighted_average == pytest.approx(0.774, 0.001)

    metrics2 = fast_compare(
        first_features, second_features, weights=(0.5, 0.6, 0.7, 0.8)
    )

    assert metrics2.weighted_average == pytest.approx(0.796, 0.001)

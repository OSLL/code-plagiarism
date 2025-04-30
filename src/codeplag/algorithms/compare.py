"""This module consists of complex algorithms for comparing two works."""

import numpy as np

from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.consts import DEFAULT_MAX_DEPTH, DEFAULT_NGRAMS_LENGTH, DEFAULT_WEIGHTS
from codeplag.types import (
    ASTFeatures,
    FastCompareInfo,
    FullCompareInfo,
    MaxDepth,
    NgramsLength,
    StructureCompareInfo,
    Threshold,
)


def fast_compare(
    features_f: ASTFeatures,
    features_s: ASTFeatures,
    ngrams_length: NgramsLength = DEFAULT_NGRAMS_LENGTH,
    weights: tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> FastCompareInfo:
    """Returns comparison result of two works compared by fast algorithms.

    Calculates the similarity of features of two programs using four algorithms, calculates their
    weighted average, and returns all of this  in 'FastCompareInfo' structure.

    Args:
    ----
        features_f: The features of the first  source file.
        features_s: The features of the second  source file.
        ngrams_length (NgramsLength): N-grams length.
        weights: Weights of fast metrics that participate in
          counting total similarity coefficient.

    """
    jakkar_coef = value_jakkar_coef(
        tokens_first=features_f.tokens,
        tokens_second=features_s.tokens,
        ngrams_length=ngrams_length,
    )
    ops_res = counter_metric(features_f.operators, features_s.operators)
    kw_res = counter_metric(features_f.keywords, features_s.keywords)
    lits_res = counter_metric(features_f.literals, features_s.literals)
    weighted_average = np.average(
        np.array([jakkar_coef, ops_res, kw_res, lits_res]), weights=weights
    )

    fast_metrics = FastCompareInfo(
        jakkar=jakkar_coef,
        operators=ops_res,
        keywords=kw_res,
        literals=lits_res,
        weighted_average=float(weighted_average),
    )

    return fast_metrics


def compare_works(
    features1: ASTFeatures,
    features2: ASTFeatures,
    ngrams_length: NgramsLength = DEFAULT_NGRAMS_LENGTH,
    max_depth: MaxDepth = DEFAULT_MAX_DEPTH,
    threshold: Threshold | None = None,
) -> FastCompareInfo | FullCompareInfo:
    """The function returns the complex result of comparing two works.

    Args:
    ----
        features1 (ASTFeatures): The features of the first work.
        features2 (ASTFeatures): The features of the second work.
        ngrams_length (NgramsLength): N-grams length.
        max_depth (MaxDepth | None): Max depth of the AST structure which play role in
          calculations.
        threshold (Threshold | None): The threshold of plagiarism searcher alarm.

    Returns:
    -------
        FastCompareInfo or FullCompareInfo, which is the result of comparing works.
        This can consist of fast metrics and, if the threshold
        value has been crossed, structure metric.
        If the threshold value is not set, it returns the structure
        metric anywhere (FullCompareInfo).

    """
    fast_compare_info = fast_compare(
        features_f=features1, features_s=features2, ngrams_length=ngrams_length
    )
    if threshold and (fast_compare_info.weighted_average * 100.0) < threshold:
        return fast_compare_info

    compliance_matrix = np.empty(
        (len(features1.head_nodes), len(features2.head_nodes), 2), dtype=np.int64
    )
    struct_res = struct_compare(
        [node for node in features1.structure if node.depth <= max_depth],
        [node for node in features2.structure if node.depth <= max_depth],
        compliance_matrix,
    )
    struct_res = struct_res[0] / struct_res[1]

    structure_info = StructureCompareInfo(
        similarity=struct_res, compliance_matrix=compliance_matrix
    )

    return FullCompareInfo(fast=fast_compare_info, structure=structure_info)

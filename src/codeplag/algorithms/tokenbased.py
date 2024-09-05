"""Token based algorithms for getting more information about two sequences.

This module provides obtaining N-grams, fingerprints from a sequence of tokens,
a quantitative assessment of the similarity of two sequences of tokens.
Also provides the ability to get the length of the longest common subsequence
of two token sequences.
"""

import math
from typing import Literal, Sequence, overload


@overload
def generate_ngrams(
    tokens: Sequence[int], n: int, hashit: Literal[False], unique: Literal[False]
) -> list[tuple[int, ...]]: ...


@overload
def generate_ngrams(
    tokens: Sequence[int], n: int, hashit: Literal[False], unique: Literal[True]
) -> set[tuple[int, ...]]: ...


@overload
def generate_ngrams(
    tokens: Sequence[int], n: int, hashit: Literal[True], unique: Literal[False]
) -> list[int]: ...


@overload
def generate_ngrams(
    tokens: Sequence[int], n: int, hashit: Literal[True], unique: Literal[True]
) -> set[int]: ...


@overload
def generate_ngrams(
    tokens: Sequence[int], n: int = 3, hashit: bool = False, unique: bool = False
) -> set[int] | list[int] | set[tuple[int, ...]] | list[tuple[int, ...]]: ...


def generate_ngrams(
    tokens: Sequence[int], n: int = 3, hashit: bool = False, unique: bool = False
) -> set[int] | list[int] | set[tuple[int, ...]] | list[tuple[int, ...]]:
    """The function returns a list or set of N-grams or list or set of hashes of ngrams.

    This function can be used to generate shingles.

    Args:
    ----
        tokens (Sequence[int]): list of tokens.
        n (int): count of elements in ngrams.
        hashit (bool): If is True, then the function returns a list or set of
          hashes of N-grams.
        unique (bool): If is True, then the function returns a set of N-grams or
          hashes of N-grams.

    """
    count_tokens = len(tokens)
    if hashit:
        if unique:
            return {hash(tuple(tokens[i : i + n])) for i in range(count_tokens - n + 1)}
        return [hash(tuple(tokens[i : i + n])) for i in range(count_tokens - n + 1)]

    if unique:
        return {tuple(tokens[i : i + n]) for i in range(count_tokens - n + 1)}

    return [tuple(tokens[i : i + n]) for i in range(count_tokens - n + 1)]


def get_imprints_from_hashes(hashes: Sequence[int]) -> list[int]:
    """The function return imprints of the given hashes.

    Args:
    ----
        hashes (Sequence[int]): list of hashes.

    Returns:
    -------
        List of each k element in hashes, where k equal log(len(hashes))

    """
    count_hashes = len(hashes)
    k = math.floor(math.log(count_hashes, 2))

    return [hashes[index] for index in range(0, count_hashes, k)]


def value_jakkar_coef(
    tokens_first: Sequence[int], tokens_second: Sequence[int], ngrams_length: int = 3
) -> float:
    """The function returns the value of the Jakkar coefficient.

    Args:
    ----
        tokens_first (Sequence[int]): list of tokens of the first program.
        tokens_second (Sequence[int]): list of tokens of the second program.
        ngrams_length (int): N-grams length.

    """
    ngrams_first: set[tuple[int, ...]] = generate_ngrams(
        tokens_first, ngrams_length, hashit=False, unique=True
    )
    ngrams_second: set[tuple[int, ...]] = generate_ngrams(
        tokens_second, ngrams_length, hashit=False, unique=True
    )

    intersection = len(ngrams_first.intersection(ngrams_second))
    union = len(ngrams_first | ngrams_second)

    if union == 0:
        return 0.0

    return intersection / union


# equal to the Levenshtein length
def lcs(X: Sequence[int], Y: Sequence[int]) -> int:
    """The function returns the length of the longest common subsequence of two sequences X and Y.

    Args:
    ----
        X (Sequence[int]): list of tokens of the first program.
        Y (Sequence[int]): list of tokens of the second program.

    """
    m = len(X)
    n = len(Y)

    if m == 0 or n == 0:
        return 0

    # m + 1 rows
    # n + 1 columns
    L = [[0] * (n + 1) for i in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1] == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    return L[m][n]


def lcs_based_coeff(subseq1: Sequence[int], subseq2: Sequence[int]) -> float:
    """Returns coefficient based on the length of the longest common subsequence.

    Returned coefficient describes how same two sequences.

    Args:
    ----
        subseq1 (Sequence[int]): the first sequence.
        subseq2 (Sequence[int]): the second sequnce.

    """
    count_elem1 = len(subseq1)
    count_elem2 = len(subseq2)

    if (count_elem1 * count_elem2) == 0:
        return 0.0

    return (2 * lcs(subseq1, subseq2)) / (count_elem1 + count_elem2)

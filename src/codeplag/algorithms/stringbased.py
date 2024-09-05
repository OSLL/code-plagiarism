from typing import Literal, Sequence

import numpy as np


class LevenshteinDistance:
    def __init__(self, sequence1: Sequence, sequence2: Sequence):
        self.sequence1 = sequence1
        self.sequence2 = sequence2
        self.s1_length = len(sequence1)
        self.s2_length = len(sequence2)
        self.distance = -1
        self.distance_matrix = np.zeros(
            (self.s1_length + 1, self.s2_length + 1), dtype=np.int64
        )

    @staticmethod
    def m(symbol1: str, symbol2: str) -> Literal[0, 1]:
        return 0 if symbol1 == symbol2 else 1

    def calculate_distance_matrix(self) -> None:
        """Calculates the Levenshtein distance.

        The function calculates the Levenshtein matrix and sets in the distance attribute minimal
        count of operations needed for converting the first sequence to the second.
        """
        for i in range(self.s1_length + 1):
            self.distance_matrix[i][0] = i
        for j in range(self.s2_length + 1):
            self.distance_matrix[0][j] = j

        for row in np.arange(1, self.s1_length + 1):
            for column in np.arange(1, self.s2_length + 1):
                symbol1 = self.sequence1[row - 1]
                symbol2 = self.sequence2[column - 1]
                minimum = min(
                    self.distance_matrix[row - 1][column] + 1,
                    self.distance_matrix[row][column - 1] + 1,
                    self.distance_matrix[row - 1][column - 1]
                    + self.m(symbol1, symbol2),
                )
                self.distance_matrix[row][column] = minimum

        self.distance = self.distance_matrix[self.s1_length][self.s2_length]

    def get_similarity_value(self) -> float:
        """The function returns the resulting fraction of similarity between two sequences."""
        if self.distance == -1:
            self.calculate_distance_matrix()

        return 1.0 - self.distance / max(self.s1_length, self.s2_length)


def is_marked_match(marked_string_list: list[int], begin: int, length: int) -> bool:
    """The function returns true if the match consists in the marked list, else false.

    Args:
    ----
        marked_string_list (list[int]): list with marked indexes.
        begin (int): start index of match.
        length (int): length of match.

    """
    condition = (
        begin in marked_string_list or (begin + length - 1) in marked_string_list
    )

    return condition


def gst(
    sequence1: Sequence, sequence2: Sequence, min_match_len: int = 6
) -> tuple[list[int], list[int]]:
    """The Greedy String Tiling algorithm.

    Args:
    ----
        sequence1 (Sequence): the first string/sequence.
        sequence2 (Sequence): the second string/sequence.
        min_match_len (int): minimal searching length of match.

    """
    matches = []
    max_match = min_match_len + 1
    source_marked = []
    search_marked = []

    while max_match > min_match_len:
        max_match = min_match_len

        for p in range(len(sequence1)):
            for t in range(len(sequence2)):
                j = 0
                while (
                    (p + j) < len(sequence1)
                    and (t + j) < len(sequence2)
                    and sequence1[p + j] == sequence2[t + j]
                    and (p + j) not in source_marked
                    and (t + j) not in search_marked
                ):
                    j += 1

                if j == max_match:
                    matches.append({"p": p, "t": t, "j": j})
                if j > max_match:
                    matches = [{"p": p, "t": t, "j": j}]
                    max_match = j

        for match in matches:
            if not is_marked_match(
                source_marked, match["p"], match["j"]
            ) and not is_marked_match(search_marked, match["t"], match["j"]):
                for k in range(match["j"]):
                    source_marked.append(match["p"] + k)
                    search_marked.append(match["t"] + k)

    return source_marked, search_marked

# fmt: off
import unittest

from typing_extensions import Self

from codeplag.algorithms.stringbased import LevenshteinDistance, gst, is_marked_match


class TestStringbased(unittest.TestCase):
    def test_levenshtein_distance_cls(self: Self) -> None:
        dist_object = LevenshteinDistance('cat', 'dog')
        self.assertEqual(dist_object.distance, -1)
        result1 = dist_object.get_similarity_value()

        self.assertEqual(dist_object.distance_matrix.size, 16)
        self.assertEqual(dist_object.distance, 3)
        self.assertEqual(result1, 0.0)

        self.assertEqual(LevenshteinDistance.m('a', 'b'), 1)
        self.assertEqual(LevenshteinDistance.m('a', 'a'), 0)

        dist_object = LevenshteinDistance([1, 2, 3, 4, 5], [1, 1, 3, 3, 5])
        result2 = dist_object.get_similarity_value()

        self.assertEqual(dist_object.distance_matrix.size, 36)
        self.assertEqual(dist_object.distance, 2)
        self.assertEqual(result2, 0.6)

    def test_is_marked_match(self: Self) -> None:
        self.assertEqual(is_marked_match([1, 2, 3], 1, 5), True)
        self.assertEqual(is_marked_match([2, 3, 4, 5], 1, 5), True)
        self.assertEqual(is_marked_match([2, 3, 4], 1, 5), False)

    def test_gst(self: Self) -> None:
        res1 = gst([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                   [1, 4, 3, 4, 5, 6, 5, 8, 9, 10], 3)
        res2 = gst([1, 2, 3, 4, 8, 6, 7, 8, 9, 10, 11],
                   [1, 2, 3, 4, 5, 6, 5, 8, 6, 7, 9, 10, 11], 3)

        self.assertEqual(res1, ([2, 3, 4, 5, 7, 8, 9],
                                [2, 3, 4, 5, 7, 8, 9]))
        self.assertEqual(res2, ([0, 1, 2, 3, 4, 5, 6, 8, 9, 10],
                                [0, 1, 2, 3, 7, 8, 9, 10, 11, 12]))

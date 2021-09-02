import unittest

from codeplag.algorithms.stringbased import LevenshteinDistance


class TestStringbased(unittest.TestCase):
    def test_levenshtein_distance_cls(self):
        dist_object = LevenshteinDistance('cat', 'dog')
        self.assertEqual(dist_object.distance, -1)
        result1 = dist_object.get_similarity_value()

        self.assertEqual(dist_object.distance_matrix.size, 16)
        self.assertEqual(dist_object.distance, 3)
        self.assertEqual(result1, 0.0)

        self.assertEqual(LevenshteinDistance.m('a', 'b'), 1)
        self.assertEqual(LevenshteinDistance.m(1, 1), 0)

        dist_object = LevenshteinDistance([1, 2, 3, 4, 5], [1, 1, 3, 3, 5])
        result2 = dist_object.get_similarity_value()

        self.assertEqual(dist_object.distance_matrix.size, 36)
        self.assertEqual(dist_object.distance, 2)
        self.assertEqual(result2, 0.6)

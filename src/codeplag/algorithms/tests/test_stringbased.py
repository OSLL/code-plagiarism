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

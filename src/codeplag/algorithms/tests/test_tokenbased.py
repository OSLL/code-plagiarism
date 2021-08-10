import unittest

from numba.typed import List
from codeplag.algorithms.tokenbased import value_jakkar_coef, lcs
from codeplag.algorithms.tokenbased import generate_unique_ngrams


class TestTokenbased(unittest.TestCase):

    def test_value_jakkar_coef(self):
        res1 = value_jakkar_coef([1, 2, 3, 4, 5, 4],
                                 [1, 2, 3, 2, 5, 2])
        res2 = value_jakkar_coef([2, 1, 1, 3, 5, 6, 7],
                                 [1, 3, 5, 3, 5, 6])
        res3 = value_jakkar_coef([3, 1, 2, 7, 4, 5, 1, 2],
                                 [4, 5, 1, 3, 4, 6, 3, 1])

        self.assertAlmostEqual(res1, 0.143, 3)
        self.assertAlmostEqual(res2, 0.286, 3)
        self.assertAlmostEqual(res3, 0.091, 3)

    def test_lcs(self):
        res1 = lcs(List([1, 2, 2, 3, 1, 4]),
                   List([2, 5, 3, 5, 1, 6, 4]))
        res2 = lcs(List([1, 2, 3, 4, 5, 6, 7]),
                   List([1, 3, 4, 4, 5, 7]))
        res3 = lcs(List([2, 4, 2, 5, 6, 10]),
                   List([1, 3, 4, 10, 5, 10]))

        self.assertEqual(res1, 4)
        self.assertEqual(res2, 5)
        self.assertEqual(res3, 3)

    def test_generate_ngrams(self):
        res1 = generate_unique_ngrams([1, 2, 3, 4, 5], 2)
        bigrams = [(1, 2), (2, 3), (3, 4), (4, 5)]
        res2 = generate_unique_ngrams([3, 4, 7, 8, 15, 3], 3)
        trigrams = [(3, 4, 7), (4, 7, 8), (7, 8, 15), (8, 15, 3)]
        res3 = generate_unique_ngrams([1, 3, 5, 7, 9, 7, 5], 4)
        fourgrams = [(1, 3, 5, 7), (3, 5, 7, 9), (5, 7, 9, 7), (7, 9, 7, 5)]

        for el in bigrams:
            self.assertIn(el, res1)

        for el in trigrams:
            self.assertIn(el, res2)

        for el in fourgrams:
            self.assertIn(el, res3)

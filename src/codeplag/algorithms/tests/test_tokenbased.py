import unittest

from codeplag.algorithms.tokenbased import (
    value_jakkar_coef, lcs, generate_unique_ngrams, generate_ngrams,
    generate_ngrams_and_hashit, lcs_based_coeff
)


class TestTokenbased(unittest.TestCase):

    def test_generate_unique_ngrams(self):
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

    def test_generate_ngrams(self):
        res1 = generate_ngrams([1, 1, 1, 2, 3, 4, 5], 2)
        bigrams = [(1, 1), (1, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
        res2 = generate_ngrams([3, 4, 7, 8, 15, 3, 4, 7], 3)
        trigrams = [(3, 4, 7), (4, 7, 8), (7, 8, 15),
                    (8, 15, 3), (15, 3, 4), (3, 4, 7)]
        res3 = generate_ngrams([1, 3, 5, 7, 9, 7, 3, 5, 7, 9], 4)
        fourgrams = [(1, 3, 5, 7), (3, 5, 7, 9), (5, 7, 9, 7), (7, 9, 7, 3),
                     (9, 7, 3, 5), (7, 3, 5, 7), (3, 5, 7, 9)]

        for el in bigrams:
            self.assertIn(el, res1)

        for el in trigrams:
            self.assertIn(el, res2)

        for el in fourgrams:
            self.assertIn(el, res3)

    def test_generate_ngrams_and_hashit(self):
        res1 = generate_ngrams_and_hashit([1, 2, 3, 4, 5], 2)
        wait1 = [3066839698, 3940950471, 1838777637, 1440686964]
        res2 = generate_ngrams_and_hashit([3, 4, 7, 8, 15, 3], 3)
        wait2 = [118437868, 3117575995, 2724747278, 4022584799]
        res3 = generate_ngrams_and_hashit([1, 3, 5, 7, 9, 7, 5], 4)
        wait3 = [2024630214, 61316218, 1551046465, 2355740258]

        for el in wait1:
            self.assertIn(el, res1)

        for el in wait2:
            self.assertIn(el, res2)

        for el in wait3:
            self.assertIn(el, res3)

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
        res1 = lcs([1, 2, 2, 3, 1, 4],
                   [2, 5, 3, 5, 1, 6, 4])
        res2 = lcs([1, 2, 3, 4, 5, 6, 7],
                   [1, 3, 4, 4, 5, 7])
        res3 = lcs([2, 4, 2, 5, 6, 10],
                   [1, 3, 4, 10, 5, 10])

        self.assertEqual(res1, 4)
        self.assertEqual(res2, 5)
        self.assertEqual(res3, 3)

    def test_lcs_based_coeff(self):
        res1 = lcs_based_coeff([1, 2, 2, 3, 1, 4], [1, 1, 2, 2, 3, 4])
        res2 = lcs_based_coeff([1, 2, 1, 0, 1, 4], [1, 1, 2, 2, 3, 4])
        res3 = lcs_based_coeff([5, 7, 5, 4, 1, 2, 2], [1, 1, 2, 2, 3, 4])

        self.assertAlmostEqual(res1, 0.833, 3)
        self.assertEqual(res2, 0.5)
        self.assertAlmostEqual(res3, 0.462, 3)

import unittest

from codeplag.algorithms.tokenbased import (generate_ngrams,
                                            get_imprints_from_hashes, lcs,
                                            lcs_based_coeff, value_jakkar_coef)


class TestTokenbased(unittest.TestCase):

    def test_generate_unique_ngrams(self):
        res1 = generate_ngrams([1, 2, 3, 4, 5], 2, unique=True)
        bigrams = {(1, 2), (2, 3), (3, 4), (4, 5)}
        res2 = generate_ngrams([3, 4, 7, 8, 15, 3], 3, unique=True)
        trigrams = {(3, 4, 7), (4, 7, 8), (7, 8, 15), (8, 15, 3)}
        res3 = generate_ngrams([1, 3, 5, 7, 9, 7, 5], 4, unique=True)
        fourgrams = {(1, 3, 5, 7), (3, 5, 7, 9), (5, 7, 9, 7), (7, 9, 7, 5)}

        self.assertEqual(res1, bigrams)
        self.assertEqual(res2, trigrams)
        self.assertEqual(res3, fourgrams)

    def test_generate_ngrams(self):
        res1 = generate_ngrams([1, 1, 1, 2, 3, 4, 5], 2)
        bigrams = [(1, 1), (1, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
        res2 = generate_ngrams([3, 4, 7, 8, 15, 3, 4, 7], 3)
        trigrams = [(3, 4, 7), (4, 7, 8), (7, 8, 15),
                    (8, 15, 3), (15, 3, 4), (3, 4, 7)]
        res3 = generate_ngrams([1, 3, 5, 7, 9, 7, 3, 5, 7, 9], 4)
        fourgrams = [(1, 3, 5, 7), (3, 5, 7, 9), (5, 7, 9, 7), (7, 9, 7, 3),
                     (9, 7, 3, 5), (7, 3, 5, 7), (3, 5, 7, 9)]

        self.assertEqual(res1, bigrams)
        self.assertEqual(res2, trigrams)
        self.assertEqual(res3, fourgrams)

    def test_generate_ngrams_and_hashit(self):
        res1 = generate_ngrams([1, 2, 3, 4, 5], 2, hashit=True)
        wait1 = [
            -3550055125485641917,
            8409376899596376432,
            1079245023883434373,
            -1009709641759730766
        ]
        res2 = generate_ngrams([3, 4, 7, 8, 15, 3], 3, hashit=True)
        wait2 = [
            5617592821626103454,
            -2108273749650792378,
            -4048189021248499647,
            1798021051504873848
        ]
        res3 = generate_ngrams([1, 3, 5, 7, 9, 7, 5], 4, hashit=True)
        wait3 = [
            2508163325525924145,
            -1561549316688687092,
            -3547738729872137598,
            3728966320797093116
        ]

        self.assertEqual(res1, wait1)
        self.assertEqual(res2, wait2)
        self.assertEqual(res3, wait3)

    def test_generate_unique_ngrams_and_hashit(self):
        res1 = generate_ngrams([1, 2, 2, 2, 5], 2, unique=True, hashit=True)
        wait1 = {
            -8422800446983873125,
            -3550055125485641917,
            1901736143494378007
        }
        res2 = generate_ngrams(
            [3, 4, 3, 3, 3, 3], 3, unique=True, hashit=True
        )
        wait2 = {
            3982697387022336237,
            8890040762135969019,
            -4613898034722827327
        }
        res3 = generate_ngrams(
            [1, 3, 5, 7, 9, 7, 5], 4, unique=True, hashit=True
        )
        wait3 = {
            2508163325525924145,
            -1561549316688687092,
            -3547738729872137598,
            3728966320797093116
        }

        self.assertEqual(res1, wait1)
        self.assertEqual(res2, wait2)
        self.assertEqual(res3, wait3)

    def test_get_imprints_from_hashes(self):
        test_cases = [
            {
                'arguments': {"hashes": [1, 2, 3, 4, 5]},
                'expected_result': [1, 3, 5],
            },
            {
                'arguments': {"hashes": [3, 4, 7, 8, 15, 3]},
                'expected_result': [3, 7, 15],
            },
            {
                'arguments': {"hashes": [1, 3, 5, 7, 9, 7, 5, 9]},
                'expected_result': [1, 7, 5],
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = get_imprints_from_hashes(**test_case['arguments'])
                self.assertEqual(test_case['expected_result'], result)

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

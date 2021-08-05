import context
import unittest
import numpy as np

from src.pyplag.other import find_max_index, matrix_value


class TestOther(unittest.TestCase):
    def test_find_max_index_normal(self):
        res1 = find_max_index(np.array([[[]]], dtype=np.int64))
        res2 = find_max_index(np.array([[[3, 5], [6, 7]],
                                        [[1, 1], [2, 3]]], dtype=np.int64))
        res3 = find_max_index(np.array([[[1, 5], [17, 131]],
                                        [[1, 3], [25, 51]],
                                        [[3, 8], [15, 29]]], dtype=np.int64))

        self.assertEqual(res1[0], 0)
        self.assertEqual(res1[1], 0)
        self.assertEqual(res2[0], 1)
        self.assertEqual(res2[1], 0)
        self.assertEqual(res3[0], 2)
        self.assertEqual(res3[1], 1)

    def test_matrix_value_normal(self):
        value1, ind1 = matrix_value(np.array([[[3, 5], [6, 7]],
                                             [[1, 1], [2, 3]]],
                                             dtype=np.int64))
        value2, ind2 = matrix_value(np.array([[[1, 5], [17, 131]],
                                             [[1, 3], [25, 51]],
                                             [[3, 8], [15, 29]]],
                                             dtype=np.int64))
        value3, ind3 = matrix_value(np.array([[[1, 1], [2, 3], [3, 4]],
                                              [[25, 34], [33, 34], [5, 8]],
                                              [[10, 11], [1, 3], [2, 4]]],
                                             dtype=np.int64))

        self.assertEqual(value1[0], 8)
        self.assertEqual(value1[1], 9)
        self.assertEqual(ind1[0][0], 1)
        self.assertEqual(ind1[0][1], 0)
        self.assertEqual(ind1[1][0], 0)
        self.assertEqual(ind1[1][1], 1)

        self.assertEqual(value2[0], 17)
        self.assertEqual(value2[1], 33)
        self.assertEqual(ind2[0][0], 2)
        self.assertEqual(ind2[0][1], 1)
        self.assertEqual(ind2[1][0], 1)
        self.assertEqual(ind2[1][1], 0)

        self.assertEqual(value3[0], 37)
        self.assertEqual(value3[1], 40)
        self.assertEqual(ind3[0][0], 0)
        self.assertEqual(ind3[0][1], 0)
        self.assertEqual(ind3[1][0], 1)
        self.assertEqual(ind3[1][1], 1)
        self.assertEqual(ind3[2][0], 2)
        self.assertEqual(ind3[2][1], 2)

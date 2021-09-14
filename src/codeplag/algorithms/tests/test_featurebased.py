import unittest
import numpy as np

from codeplag.algorithms.featurebased import (
    op_shift_metric, counter_metric,
    get_children_indexes, struct_compare
)


class TestFeaturebased(unittest.TestCase):

    def test_counter_metric_normal(self):
        example1 = {'a': 2, 'b': 1, 'c': 5, 'd': 7}
        example2 = {'a': 10, 'c': 8, 'e': 2, 'f': 12}
        example3 = {'USub': 3, 'Mor': 3, 'Der': 5}
        example4 = {'USub': 5, 'Mor': 5, 'Ker': 5}

        res1 = counter_metric(example1, example2)
        res2 = counter_metric(example3, example4)
        res3 = counter_metric({}, example4)
        res4 = counter_metric({}, {})

        self.assertEqual(res1, 0.175)
        self.assertEqual(res2, 0.3)
        self.assertEqual(res3, 0.0)
        self.assertEqual(res4, 1.0)

    '''
        Numba forbid bad arguments
    def test_counter_metric_bad_args(self):
        res1 = counter_metric("", [])
        res2 = counter_metric([], [])
    '''

    #    self.assertEqual(TypeError, res1)
    #    self.assertEqual(TypeError, res2)

    # Тут хорошо бы переписать под общий случай, а не под codeplag
    def test_struct_compare_normal(self):
        structure1 = [(1, 0), (2, 1), (3, 2),
                      (3, 2), (2, 3), (3, 4),
                      (4, 5), (3, 6), (3, 4),
                      (4, 7), (2, 8)]
        structure2 = [(1, 0), (2, 1), (2, 2),
                      (3, 3), (4, 4), (5, 5),
                      (4, 1), (4, 1), (4, 1),
                      (1, 6), (2, 7), (3, 8),
                      (3, 8), (3, 8), (2, 9)]
        count_ch1 = (get_children_indexes(structure1))[1]
        count_ch2 = (get_children_indexes(structure2))[1]
        compliance_matrix = np.zeros((count_ch1, count_ch2, 2),
                                     dtype=np.int64)
        res = struct_compare(structure1, structure2,
                             compliance_matrix)
        self.assertEqual(res, [6, 22])
        self.assertEqual(list(compliance_matrix[0][0]), [5, 15])
        self.assertEqual(list(compliance_matrix[0][1]), [5, 12])

        structure1 = [(1, 0), (2, 1), (3, 2),
                      (2, 3), (3, 4), (4, 5),
                      (3, 6), (4, 7), (2, 3),
                      (3, 4), (4, 5), (3, 6),
                      (4, 7), (2, 3), (3, 4)]
        structure2 = [(1, 0), (2, 1), (3, 2), (2, 3),
                      (3, 4), (4, 5), (3, 6), (4, 7),
                      (5, 4), (6, 8), (5, 8), (4, 9),
                      (2, 3), (3, 4), (4, 5), (3, 6),
                      (4, 4), (5, 8), (4, 10), (5, 4)]
        count_ch1 = (get_children_indexes(structure1))[1]
        count_ch2 = (get_children_indexes(structure2))[1]
        compliance_matrix = np.zeros((count_ch1, count_ch2, 2),
                                     dtype=np.int64)
        res = struct_compare(structure1, structure2,
                             compliance_matrix)
        self.assertEqual(res, [14, 23])
        self.assertEqual(compliance_matrix[0][0][0], 13)
        self.assertEqual(compliance_matrix[0][0][1], 22)

    def test_struct_compare_file_empty(self):
        structure1 = [(1, 2)]
        structure1.clear()
        structure2 = [(1, 0), (2, 1), (2, 2), (3, 3),
                      (4, 4), (5, 5), (4, 1), (4, 1),
                      (4, 1), (1, 6), (2, 7), (3, 8),
                      (3, 8), (3, 8), (2, 9), (3, 4),
                      (4, 10), (3, 11), (3, 4), (4, 5),
                      (2, 2), (3, 3), (4, 4), (5, 5), (4, 12),
                      (5, 4), (6, 5), (5, 13), (5, 4), (6, 5),
                      (2, 14), (3, 4), (4, 5)]
        res = struct_compare(structure1, structure2)
        self.assertEqual(res, [1, 34])

        structure3 = [(1, 0), (2, 1), (3, 2), (3, 2),
                      (2, 3), (3, 4), (4, 5), (3, 6),
                      (3, 4), (4, 7), (2, 8), (3, 9),
                      (4, 4), (5, 7), (4, 4), (5, 7),
                      (2, 10), (3, 4), (4, 7), (1, 11),
                      (2, 12), (2, 8), (3, 9), (4, 4),
                      (5, 7), (4, 12), (4, 12)]
        res = struct_compare(structure1, structure3)
        self.assertEqual(res, [1, 28])

    # Numba forbid bad arguments
    # def test_struct_compare_bad_args(self):
    #    tree, tree2 = self.init('empty.py', 'test2.py')
    #    res1 = struct_compare("", "")
    #    res2 = struct_compare(tree, tree2, "")
    #    self.assertEqual(TypeError, res1)
    #    self.assertEqual(TypeError, res2)

    # Numba forbid bad arguments
    # def test_op_shift_metric_bad_args(self):
    #    res1 = op_shift_metric([], 34)
    #    res2 = op_shift_metric(56, [])

    #    self.assertEqual(TypeError, res1)
    #    self.assertEqual(TypeError, res2)

    def test_op_shift_metric_normal(self):
        empty_list = []
        example1 = ['+', '-', '=']
        example2 = ['+', '+=', '/', '%']
        example3 = ['+', '-=', '/', '%']
        example4 = ['-', '+', '%', '*', '+=']
        example5 = ['%', '*', '+=']

        res3 = op_shift_metric(empty_list, empty_list)
        res4 = op_shift_metric(example1, empty_list)
        res5 = op_shift_metric(empty_list, example1)
        res6 = op_shift_metric(example2, example3)
        res7 = op_shift_metric(example4, example5)

        self.assertEqual(res3, (0, 1.0))
        self.assertEqual(res4, (0, 0.0))
        self.assertEqual(res5, (0, 0.0))
        self.assertEqual(res6[0], 0)
        self.assertAlmostEqual(res6[1], 0.6, 2)
        self.assertEqual(res7[0], 2)
        self.assertAlmostEqual(res7[1], 0.6, 2)

    def test_get_children_indexes_normal(self):
        example1 = [(1, 2), (2, 3), (3, 5), (2, 4), (2, 5), (1, 6)]
        example2 = [(3, 4), (3, 2), (4, 5), (3, 1), (4, 8), (3, 8)]
        example3 = [(2, 1), (3, 4), (3, 10), (4, 1), (2, 5), (2, 9)]
        ind1, c_ch1 = get_children_indexes(example1)
        ind2, c_ch2 = get_children_indexes(example2)
        ind3, c_ch3 = get_children_indexes(example3)

        self.assertEqual(c_ch1, 2)
        self.assertEqual(ind1[0], 0)
        self.assertEqual(ind1[1], 5)
        self.assertEqual(c_ch2, 4)
        self.assertEqual(ind2[0], 0)
        self.assertEqual(ind2[1], 1)
        self.assertEqual(ind2[2], 3)
        self.assertEqual(ind2[3], 5)
        self.assertEqual(c_ch3, 3)
        self.assertEqual(ind3[0], 0)
        self.assertEqual(ind3[1], 4)
        self.assertEqual(ind3[2], 5)

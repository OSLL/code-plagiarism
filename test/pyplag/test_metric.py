import context

import unittest
import numba
import numpy as np

from numba.typed import Dict, List
from numba.core import types
from src.pyplag.metric import nodes_metric, struct_compare
from src.pyplag.metric import op_shift_metric, value_jakkar_coef, lcs
from src.pyplag.tfeatures import ASTFeatures, get_children_ind
from src.pyplag.utils import get_AST


class TestMetric(unittest.TestCase):

    def test_nodes_metric_normal(self):
        example1 = Dict.empty(key_type=types.unicode_type,
                              value_type=types.int64)
        for key, value in {'a': 2, 'b': 1, 'c': 5, 'd': 7}.items():
            example1[key] = numba.int64(value)

        example2 = Dict.empty(key_type=types.unicode_type,
                              value_type=types.int64)
        for key, value in {'a': 10, 'c': 8, 'e': 2, 'f': 12}.items():
            example2[key] = numba.int64(value)

        example3 = Dict.empty(key_type=types.unicode_type,
                              value_type=types.int64)
        for key, value in {'USub': 3, 'Mor': 3, 'Der': 5}.items():
            example3[key] = numba.int64(value)

        example4 = Dict.empty(key_type=types.unicode_type,
                              value_type=types.int64)
        for key, value in {'USub': 5, 'Mor': 5, 'Ker': 5}.items():
            example4[key] = numba.int64(value)

        res1 = nodes_metric(example1, example2)
        res2 = nodes_metric(example3, example4)
        res3 = nodes_metric(Dict.empty(key_type=types.unicode_type,
                                       value_type=types.int64),
                            example4)
        res4 = nodes_metric(Dict.empty(key_type=types.unicode_type,
                                       value_type=types.int64),
                            Dict.empty(key_type=types.unicode_type,
                                       value_type=types.int64))

        self.assertEqual(res1, 0.175)
        self.assertEqual(res2, 0.3)
        self.assertEqual(res3, 0.0)
        self.assertEqual(res4, 0.0)

    '''
        Numba forbid bad arguments
    def test_nodes_metric_bad_args(self):
        res1 = nodes_metric("", [])
        res2 = nodes_metric([], [])
    '''

    #    self.assertEqual(TypeError, res1)
    #    self.assertEqual(TypeError, res2)

    def test_struct_compare_normal(self):
        tree1 = get_AST('py/tests/test1.py')
        tree2 = get_AST('py/tests/test2.py')
        features1 = ASTFeatures()
        features2 = ASTFeatures()
        features1.visit(tree1)
        features2.visit(tree2)
        count_ch1 = (get_children_ind(features1.structure,
                                      len(features1.structure)))[1]
        count_ch2 = (get_children_ind(features2.structure,
                                      len(features2.structure)))[1]
        compliance_matrix = np.zeros((count_ch1, count_ch2, 2),
                                     dtype=np.int64)
        res = struct_compare(features1.structure, features2.structure,
                             compliance_matrix)
        self.assertEqual(res, [28, 34])

        tree1 = get_AST('py/tests/sample1.py')
        tree2 = get_AST('py/tests/sample11.py')
        features1 = ASTFeatures()
        features2 = ASTFeatures()
        features1.visit(tree1)
        features2.visit(tree2)
        count_ch1 = (get_children_ind(features1.structure,
                                      len(features1.structure)))[1]
        count_ch2 = (get_children_ind(features2.structure,
                                      len(features2.structure)))[1]
        compliance_matrix = np.zeros((count_ch1, count_ch2, 2),
                                     dtype=np.int64)
        res = struct_compare(features1.structure, features2.structure,
                             compliance_matrix)
        self.assertEqual(res, [275, 336])

    def test_struct_compare_file_empty(self):
        tree1 = get_AST('py/tests/empty.py')
        tree2 = get_AST('py/tests/test2.py')
        features1 = ASTFeatures()
        features2 = ASTFeatures()
        features1.visit(tree1)
        features2.visit(tree2)
        count_ch1 = (get_children_ind(features1.structure,
                                      len(features1.structure)))[1]
        count_ch2 = (get_children_ind(features2.structure,
                                      len(features2.structure)))[1]
        compliance_matrix = np.zeros((count_ch1, count_ch2, 2),
                                     dtype=np.int64)
        res = struct_compare(features1.structure, features2.structure,
                             compliance_matrix)
        self.assertEqual(res, [1, 34])

        tree1 = get_AST('py/tests/empty.py')
        tree2 = get_AST('py/tests/test1.py')
        features1 = ASTFeatures()
        features2 = ASTFeatures()
        features1.visit(tree1)
        features2.visit(tree2)
        count_ch1 = (get_children_ind(features1.structure,
                                      len(features1.structure)))[1]
        count_ch2 = (get_children_ind(features2.structure,
                                      len(features2.structure)))[1]
        compliance_matrix = np.zeros((count_ch1, count_ch2, 2),
                                     dtype=np.int64)
        res = struct_compare(features1.structure, features2.structure,
                             compliance_matrix)
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
        empty_list = List(['tmp'])
        empty_list.clear()
        example1 = List(['+', '-', '='])
        example2 = List(['+', '+=', '/', '%'])
        example3 = List(['+', '-=', '/', '%'])
        example4 = List(['-', '+', '%', '*', '+='])
        example5 = List(['%', '*', '+='])

        res3 = op_shift_metric(empty_list, empty_list)
        res4 = op_shift_metric(example1, empty_list)
        res5 = op_shift_metric(empty_list, example1)
        res6 = op_shift_metric(example2, example3)
        res7 = op_shift_metric(example4, example5)

        self.assertEqual(res3, (0, 0.0))
        self.assertEqual(res4, (0, 0.0))
        self.assertEqual(res5, (0, 0.0))
        self.assertEqual(res6[0], 0)
        self.assertAlmostEqual(res6[1], 0.6, 2)
        self.assertEqual(res7[0], 2)
        self.assertAlmostEqual(res7[1], 0.6, 2)

    def test_value_jakkar_coef(self):
        res1 = value_jakkar_coef([1, 2, 3, 4, 5, 4],
                                 [1, 2, 3, 2, 5, 2])
        res2 = value_jakkar_coef([2, 1, 1, 3, 5, 6, 7],
                                 [5, 6, 1, 3, 4, 2])
        res3 = value_jakkar_coef([3, 1, 2, 7, 4, 5, 1, 2],
                                 [4, 5, 1, 3, 4, 6, 3, 1])

        self.assertEqual(res1, 0.25)
        self.assertAlmostEqual(res2, 0.222, 3)
        self.assertEqual(res3, 0.3)

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

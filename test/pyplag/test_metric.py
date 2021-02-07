from context import *

import unittest

from src.pyplag.metric import *
from test.pyplag.util import prepare_trees

class TestMetric(unittest.TestCase):

    def init(self, file1 = "", file2 = ""):
        return prepare_trees(file1, file2)


    def test_nodes_metric_normal(self):
        res1 = nodes_metric({'a': 2, 'b':1, 'c':5, 'd':7},
                            {'a':10, 'c':8, 'e':2, 'f':12})
        res2 = nodes_metric({'USub':3, 'Mor':3, 'Der':5},
                            {'USub':5, 'Mor':5, 'Ker':5})
        res3 = nodes_metric({}, {'USub':5, 'Mor':5, 'Ker':5})
        res4 = nodes_metric({}, {})

        self.assertEqual(res1, 0.175)
        self.assertEqual(res2, 0.3)
        self.assertEqual(res3, 0.0)
        self.assertEqual(res4, 0.0)


    def test_nodes_metric_bad_args(self):
        res1 = nodes_metric("", [])
        res2 = nodes_metric([], [])

        self.assertEqual(TypeError, res1)
        self.assertEqual(TypeError, res2)


    def test_struct_compare_normal(self):
        tree, tree2 = self.init('test1.py', 'test2.py')
        res = struct_compare(tree, tree2)
        self.assertEqual(res, [28, 34])
        tree, tree2 = self.init('sample1.py', 'sample11.py')
        res = struct_compare(tree, tree2)
        self.assertEqual(res, [275, 336])
   

    def test_struct_compare_file_empty(self):
        tree, tree2 = self.init('empty.py', 'test2.py')
        res = struct_compare(tree, tree2, True)
        tree, tree2 = self.init('empty.py', 'test1.py')
        res2 = struct_compare(tree, tree2, True)
        self.assertEqual(res, [1, 34])
        self.assertEqual(res2, [1, 28])


    def test_struct_compare_bad_args(self):
        tree, tree2 = self.init('empty.py', 'test2.py')
        res1 = struct_compare("", "")
        res2 = struct_compare(tree, tree2, "")
        self.assertEqual(TypeError, res1)
        self.assertEqual(TypeError, res2)


    def test_op_shift_metric_bad_args(self):
        res1 = op_shift_metric([], 34)
        res2 = op_shift_metric(56, [])

        self.assertEqual(TypeError, res1)
        self.assertEqual(TypeError, res2)


    def test_op_shift_metric_normal(self):
        res3 = op_shift_metric([], [])
        res4 = op_shift_metric(['+', '-', '='], [])
        res5 = op_shift_metric([], ['+', '-', '='])
        res6 = op_shift_metric(['+', '+=', '/', '%'],
                               ['+', '-=', '/', '%'])
        res7 = op_shift_metric(['-', '+', '%', '*', '+='],
                               ['%', '*', '+='])

        self.assertEqual(res3, (0, 0))
        self.assertEqual(res4, (0, 0))
        self.assertEqual(res5, (0, 0))
        self.assertEqual(res6, (0, 0.6))
        self.assertEqual(res7, (2, 0.6))
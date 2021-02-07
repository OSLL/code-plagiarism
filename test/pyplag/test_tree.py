from context import *

import unittest
import numpy as np

from src.pyplag.tree import *
from test.pyplag.util import prepare_trees

class TestTree(unittest.TestCase):

    def init(self, file1 = "", file2 = ""):
        return prepare_trees(file1, file2)

    def test_get_nodes_normal(self):
        tree, tree2 = self.init('test1.py', 'sample11.py')
        res1 = get_nodes('')
        res2 = get_nodes(tree)
        res3 = get_nodes(tree2)

        self.assertEqual(TypeError, res1)
        self.assertEqual(type(res2), list)
        self.assertEqual(len(res2), 2)
        self.assertEqual(type(res3), list)
        self.assertEqual(len(res3), 1)


    def test_get_nodes_bad_args(self):
        res4 = get_nodes('Hello')
        res5 = get_nodes(123)

        self.assertEqual(TypeError, res4)
        self.assertEqual(TypeError, res5)

    
    def test_get_count_of_nodes_normal(self):
        tree, tree2 = self.init('test1.py', 'test2.py')
        tree3, tree4 = self.init('sample1.py', 'sample2.py')
        res1 = get_count_of_nodes(tree)
        res2 = get_count_of_nodes(tree2)
        res3 = get_count_of_nodes(tree3)
        res4 = get_count_of_nodes(tree4)

        self.assertEqual(res1, 27)
        self.assertEqual(res2, 33)
        self.assertEqual(res3, 335)
        self.assertEqual(res4, 183)


    def test_get_count_of_nodes_bad_args(self):
        res5 = get_count_of_nodes("")
        res6 = get_count_of_nodes(15)

        self.assertEqual(TypeError, res5)
        self.assertEqual(TypeError, res6)


    def test_find_max_index_bad_args(self):
        res1 = find_max_index([], 5, '')
        res2 = find_max_index([], '', 182)
        res3 = find_max_index(25, 323, 182)

        self.assertEqual(TypeError, res1)
        self.assertEqual(TypeError, res2)
        self.assertEqual(TypeError, res3)

        a = np.array([[[1, 2], [3, 4]],
                     [[2, 3], [2, 5]]])
        res4 = find_max_index(a, 3, 3)
        res5 = find_max_index(a, 2, 5)

        self.assertEqual(IndexError, res4)
        self.assertEqual(IndexError, res5)


    def test_find_max_index_normal(self):
        a = np.array([[[1, 2], [3, 4]],
                     [[2, 3], [2, 5]]])
        res6 = find_max_index(a, 2, 2)
        a[res6] = [1, 5]
        res7 = find_max_index(a, 2, 2)

        self.assertEqual(res6, (0, 1))
        self.assertEqual(res7, (1, 0))
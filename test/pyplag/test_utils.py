from context import *

import unittest
import numpy as np

from src.pyplag.tfeatures import ASTFeatures
from src.pyplag.utils import run_compare, get_AST

class TestUtils(unittest.TestCase):

    def test_run_compare_normal(self):
        tree1 = get_AST('py/tests/test1.py')
        tree2 = get_AST('py/tests/test2.py')
        features1 = ASTFeatures()
        features2 = ASTFeatures()
        features1.visit(tree1)
        features2.visit(tree2)

        metrics, best_shift, matrix = run_compare(features1, features2)

        self.assertAlmostEqual(metrics[0], 0.824, 3)
        self.assertAlmostEqual(metrics[1], 0.667,  3)
        self.assertEqual(metrics[2], 1.)
        self.assertEqual(metrics[3], 0.75)
        self.assertAlmostEqual(metrics[4], 0.667, 3)
        self.assertEqual(best_shift, 0)
        self.assertEqual(matrix.shape, (2, 2, 2))

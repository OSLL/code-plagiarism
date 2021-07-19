import context

import unittest

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

        metrics = run_compare(features1, features2)

        self.assertAlmostEqual(metrics[0], 0.571, 3)
        self.assertAlmostEqual(metrics[1], 0.667,  3)
        self.assertEqual(metrics[2], 1.)
        self.assertEqual(metrics[3], 0.75)

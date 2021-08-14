import unittest
import os

from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.pyplag.utils import run_compare, get_ast_from_filename

pwd = os.path.dirname(os.path.abspath(__file__))


class TestUtils(unittest.TestCase):

    def test_run_compare_normal(self):
        tree1 = get_ast_from_filename(os.path.join(pwd, './data/test1.py'))
        tree2 = get_ast_from_filename(os.path.join(pwd, './data/test2.py'))
        features1 = ASTWalker()
        features2 = ASTWalker()
        features1.visit(tree1)
        features2.visit(tree2)

        metrics = run_compare(features1, features2)

        self.assertAlmostEqual(metrics[0], 0.571, 3)
        self.assertAlmostEqual(metrics[1], 0.667,  3)
        self.assertEqual(metrics[2], 1.)
        self.assertEqual(metrics[3], 0.75)

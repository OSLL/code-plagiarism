import unittest
import os

from codeplag.utils import run_compare, get_files_path_from_directory
from codeplag.pyplag.utils import (get_ast_from_filename,
                                   get_features_from_ast)


pwd = os.path.dirname(os.path.abspath(__file__))


class TestUtils(unittest.TestCase):

    def test_run_compare_normal(self):
        tree1 = get_ast_from_filename(os.path.join(pwd, './data/test1.py'))
        tree2 = get_ast_from_filename(os.path.join(pwd, './data/test2.py'))
        features1 = get_features_from_ast(tree1)
        features2 = get_features_from_ast(tree2)

        metrics = run_compare(features1, features2)

        self.assertAlmostEqual(metrics[0], 0.737, 3)
        self.assertAlmostEqual(metrics[1], 0.667,  3)
        self.assertEqual(metrics[2], 1.)
        self.assertEqual(metrics[3], 0.75)

    def test_get_files_path_from_directory(self):
        files = get_files_path_from_directory(pwd, extensions=[r".py\b"])

        self.assertIn(os.path.join(pwd, 'test_utils.py'), files)
        self.assertIn(os.path.join(pwd, 'data/test1.py'), files)
        self.assertIn(os.path.join(pwd, 'data/test2.py'), files)

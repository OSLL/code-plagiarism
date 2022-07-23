import os
import unittest

import pytest

from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast
from codeplag.utils import (compare_works, fast_compare,
                            get_files_path_from_directory)

CWD = os.path.dirname(os.path.abspath(__file__))


class TestUtils(unittest.TestCase):

    def test_fast_compare_normal(self):
        tree1 = get_ast_from_filename(os.path.join(CWD, './data/test1.py'))
        tree2 = get_ast_from_filename(os.path.join(CWD, './data/test2.py'))
        features1 = get_features_from_ast(tree1)
        features2 = get_features_from_ast(tree2)

        metrics = fast_compare(features1, features2)

        self.assertAlmostEqual(metrics['Jakkar'], 0.737, 3)
        self.assertAlmostEqual(metrics['Operators'], 0.667,  3)
        self.assertEqual(metrics['Keywords'], 1.)
        self.assertEqual(metrics['Literals'], 0.75)

    def test_get_files_path_from_directory(self):
        files = get_files_path_from_directory(CWD, extensions=[r".py\b"])

        self.assertIn(os.path.join(CWD, 'test_utils.py'), files)
        self.assertIn(os.path.join(CWD, 'data/test1.py'), files)
        self.assertIn(os.path.join(CWD, 'data/test2.py'), files)


def test_compare_works():
    tree1 = get_ast_from_filename(os.path.join(CWD, './data/test1.py'))
    tree2 = get_ast_from_filename(os.path.join(CWD, './data/test2.py'))
    tree3 = get_ast_from_filename(os.path.join(CWD, './data/test3.py'))
    features1 = get_features_from_ast(tree1)
    features2 = get_features_from_ast(tree2)
    features3 = get_features_from_ast(tree3)

    metrics = compare_works(features1, features2)
    fast_metrics = metrics['fast']
    structure_metrics = metrics['structure']

    assert fast_metrics['Jakkar'] == pytest.approx(0.737, 0.001)
    assert fast_metrics['Operators'] == pytest.approx(0.667, 0.001)
    assert fast_metrics['Keywords'] == 1.
    assert fast_metrics['Literals'] == 0.75
    assert fast_metrics['WeightedAverage'] == pytest.approx(0.774, 0.001)
    assert structure_metrics['similarity'] == pytest.approx(0.823, 0.001)
    assert structure_metrics['matrix'].tolist() == [
        [[19, 24], [7, 21]],
        [[5, 27], [8, 9]]
    ]

    metrics = compare_works(features1, features3)
    fast_metrics = metrics['fast']

    assert fast_metrics['Jakkar'] == 0.24
    assert fast_metrics['Operators'] == 0.0
    assert fast_metrics['Keywords'] == 0.6
    assert fast_metrics['Literals'] == 0.0
    assert fast_metrics['WeightedAverage'] == pytest.approx(0.218, 0.001)
    assert 'structure' not in metrics

import os
import unittest
from pathlib import Path

import numpy as np

from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.pyplag.utils import get_ast_from_filename
from codeplag.types import ASTFeatures

pwd = Path(os.path.dirname(os.path.abspath(__file__)))


class TestASTWalkers(unittest.TestCase):

    def test_astwalker_class_normal(self):
        path = pwd / './data/test1.py'
        tree = get_ast_from_filename(path)
        features = ASTFeatures(path)
        walker = ASTWalker(features)
        walker.visit(tree)
        operators = {
            'AugAssign': np.int64(1),
            'Add': np.int64(1)
        }
        keywords = {
            'FunctionDef': np.int64(1),
            'Return': np.int64(1),
            'If': np.int64(1)
        }
        literals = {
            # ast.Constant с python >= 3.8 use for all constants
            # before was NameConstant, Num and etc.
            'Constant': np.int64(3)
        }
        file_literals = {
            'Constant': 0,
        }
        if 'Constant' in features.literals:
            file_literals['Constant'] = features.literals['Constant']
            unodes = 13
        else:
            if 'NameConstant' in features.literals:
                file_literals['Constant'] += features.literals['NameConstant']
            if 'Num' in features.literals:
                file_literals['Constant'] += features.literals['Num']
            unodes = 14

        self.assertEqual(features.count_of_nodes, 27)
        self.assertEqual(features.operators, operators)
        self.assertEqual(features.keywords, keywords)
        self.assertEqual(file_literals, literals)
        self.assertEqual(len(features.unodes), unodes)
        self.assertEqual(len(features.from_num), unodes)
        self.assertEqual(features.count_unodes, np.int64(unodes))
        self.assertEqual(len(features.structure), 27)

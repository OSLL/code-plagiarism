import unittest
import numpy as np
import os

from codeplag.astfeatures import ASTFeatures
from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.pyplag.utils import get_ast_from_filename


pwd = os.path.dirname(os.path.abspath(__file__))


class TestASTWalkers(unittest.TestCase):

    def test_astwalker_class_normal(self):
        tree = get_ast_from_filename(os.path.join(pwd, './data/test1.py'))
        features = ASTFeatures()
        walker = ASTWalker(features)
        walker.visit(tree)
        operators = {}
        operators['AugAssign'] = np.int64(1)
        operators['Add'] = np.int64(1)
        keywords = {}
        keywords['FunctionDef'] = np.int64(1)
        keywords['Return'] = np.int64(1)
        keywords['If'] = np.int64(1)
        literals = {}

        # ast.Constant с python >= 3.8 используется для всех констант
        # до этого были NameConstant, Num и др.
        literals['Constant'] = np.int64(3)

        file_literals = {}
        file_literals['Constant'] = 0
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

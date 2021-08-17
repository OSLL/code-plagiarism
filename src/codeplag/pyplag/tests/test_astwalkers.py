import unittest
import numba
import os

from numba.typed import List, Dict
from numba.core import types
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
        operators = Dict.empty(key_type=types.unicode_type,
                               value_type=types.int64)
        operators['AugAssign'] = numba.int64(1)
        operators['Add'] = numba.int64(1)
        keywords = Dict.empty(key_type=types.unicode_type,
                              value_type=types.int64)
        keywords['FunctionDef'] = numba.int64(1)
        keywords['Return'] = numba.int64(1)
        keywords['If'] = numba.int64(1)
        literals = Dict.empty(key_type=types.unicode_type,
                              value_type=types.int64)

        # ast.Constant с python >= 3.8 используется для всех констант
        # до этого были NameConstant, Num и др.
        literals['Constant'] = numba.int64(3)

        file_literals = Dict.empty(key_type=types.unicode_type,
                                   value_type=types.int64)
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
        self.assertEqual(features.operators_sequence,
                         List(['AugAssign', 'Add']))
        self.assertEqual(features.operators, operators)
        self.assertEqual(features.keywords, keywords)
        self.assertEqual(file_literals, literals)
        self.assertEqual(len(features.unodes), unodes)
        self.assertEqual(len(features.from_num), unodes)
        self.assertEqual(features.count_unodes, numba.int64(unodes))
        self.assertEqual(len(features.structure), 27)

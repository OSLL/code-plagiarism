import unittest
import numba
import os

from numba.typed import List, Dict
from numba.core import types
from codeplag.pyplag.astwalkers import ASTWalker
from codeplag.pyplag.utils import get_ast_from_filename


pwd = os.path.dirname(os.path.abspath(__file__))


class TestASTWalkers(unittest.TestCase):

    def test_astwalker_class_normal(self):
        tree1 = get_ast_from_filename(os.path.join(pwd, './data/test1.py'))
        features1 = ASTWalker()
        features1.visit(tree1)
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
        literals['Constant'] = numba.int64(3)

        self.assertEqual(features1.count_of_nodes, 27)
        self.assertEqual(features1.seq_ops, List(['AugAssign', 'Add']))
        self.assertEqual(features1.operators, operators)
        self.assertEqual(features1.keywords, keywords)
        self.assertEqual(features1.literals, literals)
        self.assertEqual(len(features1.unodes), 13)
        self.assertEqual(len(features1.from_num), 13)
        self.assertEqual(features1.cunodes, numba.int64(13))
        self.assertEqual(len(features1.structure), 27)

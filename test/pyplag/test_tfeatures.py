from context import *

import unittest
import numpy as np
import numba

from numba.typed import List, Dict
from numba.core import types
from src.pyplag.tfeatures import get_children_ind, ASTFeatures
from src.pyplag.utils import get_AST

class TestTfeatures(unittest.TestCase):

    def test_astfeatures_class_normal(self):
        tree1 = get_AST('py/tests/test1.py')
        features1 = ASTFeatures()
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


    def test_get_children_ind_normal(self):
        example1 = List([(1, 2), (2, 3), (3, 5), (2, 4), (2, 5), (1, 6)])
        example2 = List([(3, 4), (3, 2), (4, 5), (3, 1), (4, 8), (3, 8)])
        example3 = List([(2, 1), (3, 4), (3, 10), (4, 1), (2, 5), (2, 9)])
        ind1, c_ch1 = get_children_ind(example1, len(example1))
        ind2, c_ch2 = get_children_ind(example2, len(example2))
        ind3, c_ch3 = get_children_ind(example3, len(example3))

        self.assertEqual(c_ch1, 2)
        self.assertEqual(ind1[0], 0)
        self.assertEqual(ind1[1], 5)
        self.assertEqual(c_ch2, 4)
        self.assertEqual(ind2[0], 0)
        self.assertEqual(ind2[1], 1)
        self.assertEqual(ind2[2], 3)
        self.assertEqual(ind2[3], 5)
        self.assertEqual(c_ch3, 3)
        self.assertEqual(ind3[0], 0)
        self.assertEqual(ind3[1], 4)
        self.assertEqual(ind3[2], 5)

import os
import unittest
from pathlib import Path

from clang.cindex import CursorKind

from codeplag.cplag.const import COMPILE_ARGS
from codeplag.cplag.tree import generic_visit, get_features, get_not_ignored
from codeplag.cplag.utils import get_cursor_from_file
from codeplag.types import ASTFeatures


class TestTree(unittest.TestCase):

    def setUp(self):
        self.first_sample_path = Path(
            os.path.abspath(
                "test/unit/codeplag/cplag/data/sample1.cpp"
            )
        )
        self.second_sample_path = Path(
            os.path.abspath(
                "test/unit/codeplag/cplag/data/sample2.cpp"
            )
        )
        if os.path.exists(self.first_sample_path) and \
           os.path.exists(self.second_sample_path):
            self.first_cursor = get_cursor_from_file(
                self.first_sample_path, COMPILE_ARGS
            )
            self.second_cursor = get_cursor_from_file(
                self.second_sample_path, COMPILE_ARGS
            )

    def test_get_not_ignored_normal(self):
        res1 = get_not_ignored(self.first_cursor, self.first_sample_path)
        res2 = get_not_ignored(self.second_cursor, self.second_sample_path)

        main_node = res1[0]
        assert main_node.spelling == 'gcd'
        assert main_node.kind == CursorKind.FUNCTION_DECL

        children = main_node.get_children()
        expected_res = [
            ('l', CursorKind.PARM_DECL),
            ('r', CursorKind.PARM_DECL),
            ('', CursorKind.COMPOUND_STMT)
        ]
        for index, child in enumerate(children):
            assert expected_res[index][0] == child.spelling
            assert expected_res[index][1] == child.kind

        main_node = res2[0]
        assert main_node.spelling == 'gcd'
        assert main_node.kind == CursorKind.FUNCTION_DECL

        children = main_node.get_children()
        expected_res = [
            ('a', CursorKind.PARM_DECL),
            ('b', CursorKind.PARM_DECL),
            ('', CursorKind.COMPOUND_STMT)
        ]
        for index, child in enumerate(children):
            assert expected_res[index][0] == child.spelling
            assert expected_res[index][1] == child.kind

        assert type(res1) == list
        assert type(res2) == list
        assert len(res1) == 1
        assert len(res2) == 1

    def test_generic_visit(self):
        features = ASTFeatures(self.first_sample_path)
        generic_visit(self.first_cursor, features)

        self.assertEqual(features.filepath, self.first_sample_path)
        self.assertEqual(features.count_of_nodes, 0)
        self.assertEqual(features.head_nodes, ['gcd'])
        self.assertEqual(features.operators, {})
        self.assertEqual(features.keywords, {})
        self.assertEqual(features.literals, {})
        self.assertEqual(len(features.unodes), 13)
        self.assertEqual(len(features.from_num), 13)
        self.assertEqual(features.count_unodes, 13)
        self.assertEqual(len(features.structure), 34)
        self.assertEqual(features.tokens, [8, 10, 10, 202, 205, 114, 100,
                                           101, 106, 214, 100, 101, 214,
                                           103, 100, 101, 100, 101, 114,
                                           100, 101, 100, 101])

    def test_get_features(self):
        features = get_features(self.first_cursor, self.first_sample_path)

        self.assertEqual(features.filepath, self.first_sample_path)
        self.assertEqual(features.count_of_nodes, 0)
        self.assertEqual(features.head_nodes, ['gcd'])
        self.assertEqual(features.operators, {'==': 1, '%': 1})
        self.assertEqual(features.keywords, {'int': 3, 'if': 1,
                                             'return': 2})
        self.assertEqual(features.literals, {'0': 1})
        self.assertEqual(len(features.unodes), 13)
        self.assertEqual(len(features.from_num), 13)
        self.assertEqual(features.count_unodes, 13)
        self.assertEqual(len(features.structure), 34)
        self.assertEqual(features.tokens, [8, 10, 10, 202, 205, 114, 100,
                                           101, 106, 214, 100, 101, 214,
                                           103, 100, 101, 100, 101, 114,
                                           100, 101, 100, 101])

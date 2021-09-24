import unittest
from codeplag.cplag.util import prepare_cursors
from codeplag.cplag.tree import get_not_ignored, generic_visit, get_features
from codeplag.astfeatures import ASTFeatures


class TestTree(unittest.TestCase):

    def init(self, file1="", file2=""):
        return prepare_cursors(file1, file2)

    def test_get_not_ignored_normal(self):
        (filename, filename2, cursor, cursor2) = self.init("sample1.cpp",
                                                           "sample2.cpp")
        res1 = get_not_ignored(cursor, filename)
        res2 = get_not_ignored(cursor2, filename2)

        self.assertEqual(type(res1), list)
        self.assertEqual(type(res2), list)
        self.assertEqual(len(res1), 1)
        self.assertEqual(len(res2), 1)

    def test_generic_visit(self):
        (filename, filename2, cursor, cursor2) = self.init("sample1.cpp",
                                                           "sample2.cpp")

        features = ASTFeatures(filename)
        generic_visit(cursor, features)

        self.assertEqual(features.filepath, filename)
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
        (filename, filename2, cursor, cursor2) = self.init("sample1.cpp",
                                                           "sample2.cpp")

        features = get_features(cursor, filename)

        self.assertEqual(features.filepath, filename)
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

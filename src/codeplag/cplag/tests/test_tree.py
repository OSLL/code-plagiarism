import unittest
from codeplag.cplag.util import prepare_cursors
from codeplag.cplag.tree import get_not_ignored, get_count_of_nodes


class TestTree(unittest.TestCase):

    def init(self, file1="", file2=""):
        return prepare_cursors(file1, file2)

    # Tests for get_not_ignored
    def test_get_not_ignored_normal(self):
        (filename, filename2, cursor, cursor2) = self.init("sample1.cpp",
                                                           "sample2.cpp")
        res1 = get_not_ignored(cursor, filename)
        res2 = get_not_ignored(cursor2, filename2)
        self.assertEqual(type(res1), list)
        self.assertEqual(type(res2), list)

    def test_get_not_ignored_bad_file(self):
        (filename, filename2, cursor, cursor2) = self.init("empty.cpp",
                                                           "sample2.cpp")
        res1 = get_not_ignored(cursor, "")
        res2 = get_not_ignored(cursor2, ["w", 'q'])
        self.assertEqual(res1, FileNotFoundError)
        self.assertEqual(res2, TypeError)

    def test_get_not_ignored_bad_cursor(self):
        (filename, filename2, cursor, cursor2) = self.init("empty.cpp",
                                                           "sample2.cpp")
        res1 = get_not_ignored(cursor, filename)
        res2 = get_not_ignored(['h', 'e', 'l', 'l', 'o'], filename2)
        self.assertEqual(res1, None)
        self.assertEqual(res2, TypeError)

    # Tests for get_count_of_nodes
    def test_get_count_of_nodes_normal(self):
        (filename, filename2, cursor, cursor2) = self.init("sample1.cpp",
                                                           "sample2.cpp")
        n1 = get_count_of_nodes(cursor)
        n2 = get_count_of_nodes(cursor2)
        self.assertEqual(n1, 394)
        self.assertEqual(n2, 396)

    def test_get_count_of_nodes_bad_cursor(self):
        n1 = get_count_of_nodes(None)
        n2 = get_count_of_nodes('')
        n3 = get_count_of_nodes([3, 4, 5])
        n4 = get_count_of_nodes({3, 4, 5})
        n5 = get_count_of_nodes(123)
        self.assertEqual(n1, TypeError)
        self.assertEqual(n2, TypeError)
        self.assertEqual(n3, TypeError)
        self.assertEqual(n4, TypeError)
        self.assertEqual(n5, TypeError)

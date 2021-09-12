import unittest
from codeplag.cplag.util import prepare_cursors
from codeplag.cplag.tree import get_not_ignored


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

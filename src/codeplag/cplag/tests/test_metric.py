import unittest
from numba.typed import List
from codeplag.cplag.util import prepare_cursors
from codeplag.cplag.metric import *

class TestMetric(unittest.TestCase):

    def init(self, file1 = "", file2 = ""):
        return prepare_cursors(file1, file2)


    # Tests for smart_compare_nodes
    def test_smart_compare_nodes_normal(self):
        (filename, filename2, cursor, cursor2) = self.init("rw2.cpp", "rw1.cpp")
        parsed_nodes1 = get_not_ignored(cursor, filename)
        parsed_nodes2 = get_not_ignored(cursor2, filename2)
        res = smart_compare_nodes(parsed_nodes1[0], parsed_nodes2[0])
        self.assertEqual(res, [146, 158])
    
    def test_smart_compare_nodes_bad_cursor(self):
        (filename, filename2, cursor, cursor2) = self.init("rw2.cpp", "rw1.cpp")
        res = smart_compare_nodes("cursor", None)
        self.assertEqual(res, TypeError)


    # Tests for ast_compare
    def test_ast_compare_normal(self):
        (filename, filename2, cursor, cursor2) = self.init("rw1.cpp", "rw2.cpp")
        res = ast_compare(cursor, cursor2, filename, filename2)
        self.assertEqual(res, [147,159])

    def test_ast_compare_file_error(self):
        (filename, filename2, cursor, cursor2) = self.init()
        res1 = ast_compare(cursor, cursor2, "", "")
        res2 = ast_compare(cursor, cursor2, [1,2,3], {'a', 'b', 'c'})
        self.assertEqual(FileNotFoundError, res1)
        self.assertEqual(TypeError, res2)

    def test_ast_compare_file_empty(self):
        (filename, filename2, cursor, cursor2) = self.init('empty.cpp')
        res = ast_compare(cursor, cursor2, "", "")
        self.assertEqual(FileNotFoundError, res)

    def test_ast_compare_bad_cursor(self):
        (filename, filename2, cursor, cursor2) = self.init()
        res1 = ast_compare("", "", filename, filename2)
        self.assertEqual(TypeError, res1)


    # Tests for get_operators_frequency
    def test_get_operators_frequency_normal(self):
        (filename, filename2, cursor, cursor2) = self.init("rw2.cpp", "rw1.cpp")
        (op, fr, co, ck, seq) = get_operators_frequency(cursor, cursor2)
               
        fr_std = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 14, 3, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 14, 3, 0]]
        co_std = [22, 21]
        ck_std = [{'using': 1, 'namespace': 1, 'int': 1, 'char': 1, 'if': 2, 'return': 3}, {'using': 1, 'namespace': 1, 'int': 1, 'char': 1, 'if': 0, 'return': 1}]
        seq_std = [List(['<', '>', '<', '>', '!', '<<', '<<', '<<', '<<', '<<', '<<', '>>', '<<', '<<', '<<', '<<', '>>', '<<', '<<', '>>', '<<', '<<']),
                   List(['<', '>', '<', '>', '<<', '<<', '<<', '<<', '<<', '<<', '>>', '<<', '<<', '<<', '<<', '>>', '<<', '<<', '>>', '<<', '<<'])]

        self.assertEqual(fr, fr_std)
        self.assertEqual(co, co_std)
        self.assertEqual(ck, ck_std)
        self.assertEqual(seq, seq_std)

    def test_get_operators_frequency_bad_cursor(self):
        (filename, filename2, cursor, cursor2) = self.init("rw2.cpp", "rw1.cpp")
        res = get_operators_frequency(cursor, [1,2,3])
        self.assertEqual(res, TypeError)
        res = get_operators_frequency({1,2,3}, cursor2)
        self.assertEqual(res, TypeError)
        res = get_operators_frequency(None, "string")
        self.assertEqual(res, TypeError)


    # Test for get_op_freq_percent
    def test_get_op_freq_percent(self):
        (filename, filename2, cursor, cursor2) = self.init("rw2.cpp", "rw1.cpp")
        (op, fr, co, ck, seq) = get_operators_frequency(cursor, cursor2)
        res = get_op_freq_percent(op, fr, co)
        self.assertAlmostEqual(res, 0.95, 2)

        (filename, filename2, cursor, cursor2) = self.init("empty.cpp", "same1.cpp")
        (op, fr, co, ck, seq) = get_operators_frequency(cursor, cursor2)
        res = get_op_freq_percent(op, fr, co)
        self.assertAlmostEqual(res, 0, 2)

        (filename, filename2, cursor, cursor2) = self.init("sample4.cpp", "sample7.cpp")
        (op, fr, co, ck, seq) = get_operators_frequency(cursor, cursor2)
        res = get_op_freq_percent(op, fr, co)
        self.assertAlmostEqual(res, 0.95, 2)

        res = get_op_freq_percent(None, "12", {13, 11})
        self.assertEqual(res, TypeError)


    # Tests for get_kw_freq_percent
    def test_get_kw_freq_percent_normal(self):
        (filename, filename2, cursor, cursor2) = self.init("sample4.cpp", "sample7.cpp")
        (op, fr, co, ck, seq) = get_operators_frequency(cursor, cursor2)
        res = get_kw_freq_percent(ck)
        self.assertEqual(res, 1)

    def test_get_kw_freq_percent_bad(self):
        res = get_kw_freq_percent([])
        self.assertEqual(res, 0)
        res = get_kw_freq_percent({})
        self.assertEqual(res, TypeError)
        res = get_kw_freq_percent("hello")
        self.assertEqual(res, TypeError)
        res = get_kw_freq_percent(12)
        self.assertEqual(res, TypeError)
        res = get_kw_freq_percent([1,2,3])
        self.assertEqual(res, 0)

from pyanalyze import *
import unittest
import warnings

class TestPyanalyze(unittest.TestCase):

    def init(self, file1 = "", file2 = ""):
        # warnings.simplefilter("ignore", ResourceWarning)
        directory = 'py/tests/'
        files = list(filter(lambda x: (x.endswith('.py')),
                     os.listdir(directory)))

        if(len(files) < 2):
            raise FileNotFoundError('At least 2 files in /tests folder are needed') 
        else:
            if(file1 == ""):
                filename = directory + 'rw1.py'
            else:
                filename = directory + file1

            if(file2 == ""):
                filename2 = directory + 'rw2.py'
            else:
                filename2 = directory + file2

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename + ' not exists.')

        if not os.path.isfile(filename2):
            raise FileNotFoundError(filename2 + ' not exists.')

        with open(filename) as f:
            tree = ast.parse(f.read())

        with open(filename2) as f:
            tree2 = ast.parse(f.read())

        return (tree, tree2)


    def test_nodes_metric(self):
        res1 = nodes_metric("", [])
        res2 = nodes_metric([], [])
        self.assertEqual(TypeError, res1)
        self.assertEqual(TypeError, res2)

        res1 = nodes_metric({'a': 2, 'b':1, 'c':5, 'd':7},
                            {'a':10, 'c':8, 'e':2, 'f':12})
        res2 = nodes_metric({'USub':3, 'Mor':3, 'Der':5},
                            {'USub':5, 'Mor':5, 'Ker':5})
        self.assertEqual(res1, 0.175)
        self.assertEqual(res2, 0.3)


    def test_get_nodes(self):
        tree, tree2 = self.init('test1.py', 'sample11.py')
        res1 = get_nodes("")
        res2 = get_nodes(tree)
        res3 = get_nodes(tree2)
        self.assertEqual(TypeError, res1)
        self.assertEqual(type(res2), list)
        self.assertEqual(len(res2), 2)
        self.assertEqual(type(res3), list)
        self.assertEqual(len(res3), 1)


    def test_get_count_of_nodes(self):
        pass


    def test_struct_compare_normal(self):
        tree, tree2 = self.init('test1.py', 'test2.py')
        res = struct_compare(tree, tree2)
        self.assertEqual(res, [28, 34])
        tree, tree2 = self.init('sample1.py', 'sample11.py')
        res = struct_compare(tree, tree2)
        self.assertEqual(res, [275, 336])
   

    def test_struct_compare_file_empty(self):
        tree, tree2 = self.init('empty.py', 'test2.py')
        res = struct_compare(tree, tree2, True)
        tree, tree2 = self.init('empty.py', 'test1.py')
        res2 = struct_compare(tree, tree2, True)
        self.assertEqual(res, [1, 34])
        self.assertEqual(res2, [1, 28])


    def test_struct_compare_bad_args(self):
        tree, tree2 = self.init('empty.py', 'test2.py')
        res1 = struct_compare("", "")
        res2 = struct_compare(tree, tree2, "")
        self.assertEqual(TypeError, res1)
        self.assertEqual(TypeError, res2)

# Executing the tests in the above test case class
if __name__ == "__main__":
    unittest.main()
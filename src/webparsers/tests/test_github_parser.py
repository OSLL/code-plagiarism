import unittest
from unittest.mock import patch, Mock, call

from webparsers.github_parser import GitHubParser

class TestGitHubParser(unittest.TestCase):

    def test_check_github_url(self):
        test_cases = [
            {
                'arguments': {"github_url" : "https://github.com/index"},
                'expected_result': ["https:", "", "github.com", "index"],
            },
            {
                'arguments': {"github_url" : "http://github.com/OSLL/test.py"},
                'expected_result': ["http:", "", "github.com", "OSLL", "test.py"],
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = GitHubParser.check_github_url(**test_case['arguments'])
                self.assertEqual(test_case['expected_result'], result)

    def test_check_github_url_bad(self):
        test_cases = [
            {
                'arguments': {"github_url" : "ttps://github.com/index"},
            },
            {
                'arguments': {"github_url" : "http:/j/github.com/OSLL/test.py"},
            },
            {
                'arguments': {"github_url" : "http://githUb.com/OSLL/test.py"},
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                with self.assertRaises(ValueError):
                    GitHubParser.check_github_url(**test_case['arguments'])

    def test_parse_repo_url(self):
        test_cases = [
            {
                'arguments': {"repo_url" : "https://github.com/OSLL/code-plagiarism"},
                'expected_result': ("OSLL", "code-plagiarism"),
            },
            {
                'arguments': {"repo_url" : "http://github.com/OSLL/test.py"},
                'expected_result': ("OSLL", "test.py"),
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = GitHubParser.parse_repo_url(**test_case['arguments'])
                self.assertEqual(test_case['expected_result'], result)

    def test_parse_repo_url_bad(self):
        test_cases = [
            {
                'arguments': {"repo_url" : "ttps://github.com/index"},
            },
            {
                'arguments': {"repo_url" : "http:/j/github.com/OSLL/test.py"},
            },
            {
                'arguments': {"repo_url" : "http://githUb.com/OSLL/test.py"},
            },
            {
                'arguments': {"repo_url" : "http://github.com/OSLL"},
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                with self.assertRaises(ValueError):
                    GitHubParser.parse_repo_url(**test_case['arguments'])


if __name__ == '__main__':
    unittest.main()
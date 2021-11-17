import unittest

from webparsers.github_parser import GitHubParser


class TestGitHubParser(unittest.TestCase):

    def test_check_github_url(self):
        test_cases = [
            {
                'arguments': {
                    "github_url": "https://github.com/OSLL"
                },
                'expected_result': ["https:", "", "github.com", "OSLL"],
            },
            {
                'arguments': {
                    "github_url": "http://github.com/OSLL/code-plagiarism/"
                },
                'expected_result': ["http:", "", "github.com",
                                    "OSLL", "code-plagiarism"],
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = GitHubParser.check_github_url(**test_case['arguments'])
                self.assertEqual(test_case['expected_result'], result)

    def test_check_github_url_bad(self):
        test_cases = [
            {
                'arguments': {
                    "github_url": "ttps://github.com/OSLL"
                },
            },
            {
                'arguments': {
                    "github_url": "https:/j/github.com/OSLL"
                },
            },
            {
                'arguments': {
                    "github_url": "https://githUb.com/OSLL"
                },
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                with self.assertRaises(ValueError):
                    GitHubParser.check_github_url(**test_case['arguments'])

    def test_parse_repo_url(self):
        test_cases = [
            {
                'arguments': {
                    "repo_url": "https://github.com/OSLL/code-plagiarism"
                },
                'expected_result': ("OSLL", "code-plagiarism"),
            },
            {
                'arguments': {
                    "repo_url": "http://github.com/OSLL/test.py"
                },
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
                'arguments': {
                    "repo_url": "ttps://github.com/index"
                },
            },
            {
                'arguments': {
                    "repo_url": "http:/j/github.com/OSLL/test.py"
                },
            },
            {
                'arguments': {
                    "repo_url": "http://githUb.com/OSLL/test.py"
                },
            },
            {
                'arguments': {"repo_url": "http://github.com/OSLL"},
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                with self.assertRaises(ValueError):
                    GitHubParser.parse_repo_url(**test_case['arguments'])

    def test_parse_content_url(self):
        test_cases = [
            {
                'arguments': {
                    "content_url": "https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/astfeatures.py"
                },
                'expected_result': ('OSLL', 'code-plagiarism', 'main', 'src/codeplag/astfeatures.py'),
            },
            {
                'arguments': {
                    "content_url": "https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/logger.py"
                },
                'expected_result': ('OSLL', 'code-plagiarism', 'main', 'src/codeplag/logger.py'),
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = GitHubParser.parse_content_url(**test_case['arguments'])
                self.assertEqual(result, test_case['expected_result'])

    def test_parse_content_url_bad(self):
        test_cases = [
            {
                'arguments': {
                    'content_url': 'ttps://github.com/index'
                },
            },
            {
                'arguments': {
                    'content_url': 'http:/j/github.com/OSLL/test.py'
                },
            },
            {
                'arguments': {
                    'content_url': 'http://githUb.com/OSLL/test.py'
                },
            },
            {
                'arguments': {
                    'content_url': 'http://github.com/OSLL'
                },
            },
            {
                'arguments': {
                    'content_url': 'http://github.com/OSLL/test/tmp'
                },
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                with self.assertRaises(ValueError):
                    GitHubParser.parse_content_url(**test_case['arguments'])

    def test_is_accepted_extension(self):
        test_cases = [
            {
                'arguments': {
                    'path': 'some/path/module.py'
                },
                'parser': GitHubParser(),
                'expected_result': True
            },
            {
                'arguments': {
                    'path': 'some/path/module.cpp'
                },
                'parser': GitHubParser(),
                'expected_result': True
            },
            {
                'arguments': {
                    'path': 'some/path/module.c'
                },
                'parser': GitHubParser(),
                'expected_result': True
            },
            {
                'arguments': {
                    'path': 'some/path/module.in.py'
                },
                'parser': GitHubParser(),
                'expected_result': True
            },
            {
                'arguments': {
                    'path': 'some/path/module.c'
                },
                'parser': GitHubParser(file_extensions=['py']),
                'expected_result': False
            },
            {
                'arguments': {
                    'path': 'some/path/module.in'
                },
                'parser': GitHubParser(file_extensions=['cpp', 'c']),
                'expected_result': False
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                rv = test_case['parser'].is_accepted_extension(**test_case['arguments'])
                self.assertEqual(rv, test_case['expected_result'])


if __name__ == '__main__':
    unittest.main()

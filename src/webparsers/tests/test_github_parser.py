import unittest

from unittest.mock import patch
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

    @patch('webparsers.github_parser.requests.get')
    def test_send_get_request(self, mock_get):
        class Response:
            def __init__(self, status_code, message=None):
                self.status_code = status_code

            def raise_for_status(self):
                return None

        test_cases = [
            {
                'arguments': {
                    'api_url': 'users/moevm/repos',
                    'params': {}
                },
                'get_arguments': [

                ],
                'get_posargs': ['https://api.github.com/users/moevm/repos'],
                'get_kwargs': {
                    'headers': {'accept': 'application/vnd.github.v3+json'},
                    'params': {}
                },
                'response': Response(200)
            }
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_get.reset_mock()
            mock_get.return_value = test_case['response']

            with self.subTest(test_case=test_case):
                rv = parser.send_get_request(**test_case['arguments'])
                self.assertEqual(rv, test_case['response'])

                mock_get.assert_called_once_with(*test_case['get_posargs'],
                                                 **test_case['get_kwargs'])

    @patch('webparsers.github_parser.requests.get')
    def test_send_get_request_bad(self, mock_get):
        class Response:
            def __init__(self, status_code, message=None):
                self.status_code = status_code
                self.message = message

            def json(self):
                return {'message': self.message} if self.message else {}

        test_cases = [
            {
                'arguments': {
                    'api_url': 'Test/url',
                    'params': {}
                },
                'get_arguments': [

                ],
                'get_posargs': ['https://api.github.com/Test/url'],
                'get_kwargs': {
                    'headers': {'accept': 'application/vnd.github.v3+json'},
                    'params': {}
                },
                'response': Response(403, "Not Found"),
                'raised': Exception
            },
            {
                'arguments': {
                    'api_url': 'bad/link',
                    'params': {}
                },
                'get_posargs': ['https://api.github.com/bad/link'],
                'get_kwargs': {
                    'headers': {'accept': 'application/vnd.github.v3+json'},
                    'params': {}
                },
                'response': Response(403),
                'raised': KeyError
            },
            {
                'arguments': {
                    'api_url': 'bad/link',
                    'params': {
                        'per_page': 100,
                        'page': 5
                    }
                },
                'get_posargs': ['https://api.github.com/bad/link'],
                'get_kwargs': {
                    'headers': {'accept': 'application/vnd.github.v3+json'},
                    'params': {
                        'per_page': 100,
                        'page': 5
                    }
                },
                'response': Response(403),
                'raised': KeyError
            },
            {
                'arguments': {
                    'api_url': 'bad/link',
                    'params': {}
                },
                'token': 'test_token',
                'get_posargs': ['https://api.github.com/bad/link'],
                'get_kwargs': {
                    'headers': {
                        'accept': 'application/vnd.github.v3+json',
                        'Authorization': 'token test_token'
                    },
                    'params': {}
                },
                'response': Response(403),
                'raised': KeyError
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            if test_case.get('token'):
                parser = GitHubParser(access_token=test_case['token'])

            mock_get.reset_mock()
            mock_get.return_value = test_case['response']

            with self.subTest(test_case=test_case):
                with self.assertRaises(test_case['raised']):
                    parser.send_get_request(**test_case['arguments'])

                mock_get.assert_called_once_with(*test_case['get_posargs'],
                                                 **test_case['get_kwargs'])


if __name__ == '__main__':
    unittest.main()

import unittest
import io
import base64

from contextlib import redirect_stdout
from unittest.mock import patch, call
from webparsers.github_parser import GitHubParser


class TestGitHubParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

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

    def test_decode_file_content(self):
        test_cases = [
            {
                'arguments': {
                    'file_in_bytes': 'Good message'.encode('utf-8')
                },
                'expected_result': 'Good message',
            },
            {
                'arguments': {
                    'file_in_bytes': bytearray(b'Bad\xee\xeemessage')
                },
                'expected_result': 'Bad  message',
            }
        ]

        for test_case in test_cases:
            buf = io.StringIO()
            with redirect_stdout(buf):
                with self.subTest(test_case=test_case):
                    result = GitHubParser.decode_file_content(**test_case['arguments'])
                    self.assertEqual(result, test_case['expected_result'])

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

    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_list_of_repos(self, mock_send_get_request):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'owner': 'OSLL',
                    'per_page': 50,
                    'reg_exp': None
                },
                'send_calls': [
                    call(
                        '/users/OSLL/repos',
                        params={
                            'per_page': 50,
                            'page': 1
                        }
                    )
                ],
                'send_rvs': [Response([])],
                'expected_result': {}
            },
            {
                'arguments': {
                    'owner': 'OSLL',
                    'per_page': 20,
                    'reg_exp': None
                },
                'send_calls': [
                    call(
                        '/users/OSLL/repos',
                        params={
                            'per_page': 20,
                            'page': 1
                        }
                    ),
                    call(
                        '/users/OSLL/repos',
                        params={
                            'per_page': 20,
                            'page': 2
                        }
                    ),
                    call(
                        '/users/OSLL/repos',
                        params={
                            'per_page': 20,
                            'page': 3
                        }
                    )
                ],
                'send_rvs': [
                    Response(
                        [
                            {
                                'name': 'asm_web_debug',
                                'html_url': 'https://github.com/OSLL/asm_web_debug'
                            },
                            {
                                'name': 'aido-auto-feedback',
                                'html_url': 'https://github.com/OSLL/aido-auto-feedback'
                            }
                        ]
                    ),
                    Response(
                        [
                            {
                                'name': 'MD-Code_generator',
                                'html_url': 'https://github.com/OSLL/MD-Code_generator'
                            },
                            {
                                'name': 'code-plagiarism',
                                'html_url': 'https://github.com/OSLL/code-plagiarism'
                            }
                        ]
                    ),
                    Response([])
                ],
                'expected_result': {
                    'aido-auto-feedback': 'https://github.com/OSLL/aido-auto-feedback',
                    'asm_web_debug': 'https://github.com/OSLL/asm_web_debug',
                    'MD-Code_generator': 'https://github.com/OSLL/MD-Code_generator',
                    'code-plagiarism': 'https://github.com/OSLL/code-plagiarism'
                }
            },
            {
                'arguments': {
                    'owner': 'OSLL',
                    'per_page': 20,
                    'reg_exp': r'\ba'
                },
                'send_calls': [
                    call(
                        '/users/OSLL/repos',
                        params={
                            'per_page': 20,
                            'page': 1
                        }
                    ),
                    call(
                        '/users/OSLL/repos',
                        params={
                            'per_page': 20,
                            'page': 2
                        }
                    ),
                    call(
                        '/users/OSLL/repos',
                        params={
                            'per_page': 20,
                            'page': 3
                        }
                    )
                ],
                'send_rvs': [
                    Response(
                        [
                            {
                                'name': 'asm_web_debug',
                                'html_url': 'https://github.com/OSLL/asm_web_debug'
                            },
                            {
                                'name': 'aido-auto-feedback',
                                'html_url': 'https://github.com/OSLL/aido-auto-feedback'
                            }
                        ]
                    ),
                    Response(
                        [
                            {
                                'name': 'MD-Code_generator',
                                'html_url': 'https://github.com/OSLL/MD-Code_generator'
                            },
                            {
                                'name': 'code-plagiarism',
                                'html_url': 'https://github.com/OSLL/code-plagiarism'
                            }
                        ]
                    ),
                    Response([])
                ],
                'expected_result': {
                    'aido-auto-feedback': 'https://github.com/OSLL/aido-auto-feedback',
                    'asm_web_debug': 'https://github.com/OSLL/asm_web_debug',
                }
            }
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case['send_rvs']

            with self.subTest(test_case=test_case):
                rv = parser.get_list_of_repos(**test_case['arguments'])
                self.assertEqual(rv, test_case['expected_result'])

                self.assertEqual(mock_send_get_request.mock_calls, test_case['send_calls'])

    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_name_default_branch(self, mock_send_get_request):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'owner': 'OSLL',
                    'repo': 'aido-auto-feedback'
                },
                'send_calls': [
                    call('/repos/OSLL/aido-auto-feedback')
                ],
                'send_rv': Response({'default_branch': 'main'}),
                'expected_result': 'main'
            },
            {
                'arguments': {
                    'owner': 'moevm',
                    'repo': 'asm_web_debug'
                },
                'send_calls': [
                    call('/repos/moevm/asm_web_debug')
                ],
                'send_rv': Response({'default_branch': 'issue2'}),
                'expected_result': 'issue2'
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.return_value = test_case['send_rv']

            with self.subTest(test_case=test_case):
                rv = parser.get_name_default_branch(**test_case['arguments'])
                self.assertEqual(rv, test_case['expected_result'])

                self.assertEqual(mock_send_get_request.mock_calls, test_case['send_calls'])

    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_sha_last_branch_commit(self, mock_send_get_request):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'owner': 'OSLL',
                    'repo': 'aido-auto-feedback',
                },
                'send_calls': [
                    call('/repos/OSLL/aido-auto-feedback/branches/main')
                ],
                'send_rv': Response(
                    {
                        'commit': {
                            'sha': 'jal934304'
                        }
                    }
                ),
                'expected_result': 'jal934304'
            },
            {
                'arguments': {
                    'owner': 'moevm',
                    'repo': 'asm_web_debug',
                    'branch': 'iss76'
                },
                'send_calls': [
                    call('/repos/moevm/asm_web_debug/branches/iss76')
                ],
                'send_rv': Response(
                    {
                        'commit': {
                            'sha': 'xyuwr934hsd'
                        }
                    }
                ),
                'expected_result': 'xyuwr934hsd'
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.return_value = test_case['send_rv']

            with self.subTest(test_case=test_case):
                rv = parser.get_sha_last_branch_commit(**test_case['arguments'])
                self.assertEqual(rv, test_case['expected_result'])

                self.assertEqual(mock_send_get_request.mock_calls, test_case['send_calls'])

    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_file_content_from_sha(self, mock_send_get_request):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'owner': 'OSLL',
                    'repo': 'aido-auto-feedback',
                    'sha': 'kljsdfkiwe0341',
                    'file_path': 'http://api.github.com/repos'
                },
                'send_calls': [
                    call('/repos/OSLL/aido-auto-feedback/git/blobs/kljsdfkiwe0341')
                ],
                'send_rv': Response(
                    {
                        'content': base64.b64encode(b'Good message')
                    }
                ),
                'expected_result': ('Good message', 'http://api.github.com/repos')
            },
            {
                'arguments': {
                    'owner': 'moevm',
                    'repo': 'asm_web_debug',
                    'sha': 'jsadlkf3904',
                    'file_path': 'http://api.github.com/test'
                },
                'send_calls': [
                    call('/repos/moevm/asm_web_debug/git/blobs/jsadlkf3904')
                ],
                'send_rv': Response(
                    {
                        'content': base64.b64encode(b'Bad\xee\xeemessage')
                    }
                ),
                'expected_result': ('Bad  message', 'http://api.github.com/test')
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.return_value = test_case['send_rv']

            buf = io.StringIO()
            with redirect_stdout(buf):
                with self.subTest(test_case=test_case):
                    rv = parser.get_file_content_from_sha(**test_case['arguments'])
                    self.assertEqual(rv, test_case['expected_result'])

                    self.assertEqual(mock_send_get_request.mock_calls, test_case['send_calls'])

    @patch('webparsers.github_parser.GitHubParser.get_file_content_from_sha')
    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_files_generator_from_sha_commit(self, mock_send_get_request,
                                                 mock_get_file_content_from_sha):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'owner': 'OSLL',
                    'repo': 'aido-auto-feedback',
                    'branch': 'iss76',
                    'sha': 'kljsdfkiwe0341',
                },
                'send_calls': [
                    call(
                        '/repos/OSLL/aido-auto-feedback/git/trees/kljsdfkiwe0341'
                    ),
                    call(
                        '/repos/OSLL/aido-auto-feedback/git/trees/jslkfjjeuwijsdmvd'
                    )
                ],
                'send_se': [
                    Response(
                        {
                            'tree': [
                                {
                                    'type': 'tree',
                                    'path': 'src',
                                    'sha': 'jslkfjjeuwijsdmvd'
                                },
                                {
                                    'type': 'blob',
                                    'path': 'main.py',
                                    'sha': 'ixiuerjs9430',
                                }
                            ],
                        }
                    ),
                    Response(
                        {
                            'tree': [
                                {
                                    'type': 'blob',
                                    'path': 'utils.py',
                                    'sha': 'uwrcbasrew94'
                                },
                                {
                                    'type': 'blob',
                                    'path': 'tests.py',
                                    'sha': 'vbuqcvxpiwe'
                                }
                            ]
                        }
                    )
                ],
                'get_file_content_calls': [
                    call(
                        'OSLL',
                        'aido-auto-feedback',
                        'uwrcbasrew94',
                        'https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/utils.py'
                    ),
                    call(
                        'OSLL',
                        'aido-auto-feedback',
                        'vbuqcvxpiwe',
                        'https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/tests.py'
                    ),
                    call(
                        'OSLL',
                        'aido-auto-feedback',
                        'ixiuerjs9430',
                        'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py'
                    ),
                ],
                'get_file_content_se': [
                    ('Some code 2', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/utils.py'),
                    ('Some code 3', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/tests.py'),
                    ('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py'),
                ],
                'expected_result': [
                    ('Some code 2', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/utils.py'),
                    ('Some code 3', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/tests.py'),
                    ('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py'),
                ]
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case['send_se']
            mock_get_file_content_from_sha.reset_mock()
            mock_get_file_content_from_sha.side_effect = test_case['get_file_content_se']

            with self.subTest(test_case=test_case):
                rv = list(parser.get_files_generator_from_sha_commit(**test_case['arguments']))
                self.assertEqual(rv, test_case['expected_result'])

                self.assertEqual(mock_send_get_request.mock_calls, test_case['send_calls'])
                self.assertEqual(mock_get_file_content_from_sha.mock_calls, test_case['get_file_content_calls'])

    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_list_repo_branches(self, mock_send_get_request):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'owner': 'OSLL',
                    'repo': 'aido-auto-feedback',
                    'per_page': 50
                },
                'send_calls': [
                    call(
                        '/repos/OSLL/aido-auto-feedback/branches',
                        params={
                            'per_page': 50,
                            'page': 1
                        }
                    ),
                    call(
                        '/repos/OSLL/aido-auto-feedback/branches',
                        params={
                            'per_page': 50,
                            'page': 2
                        }
                    ),
                ],
                'send_se': [
                    Response(
                        [
                            {
                                'name': 'main',
                                'commit': {
                                    'sha': '0928jlskdfj'
                                }
                            },
                            {
                                'name': 'iss76',
                                'commit': {
                                    'sha': 'kjsadfwi'
                                }
                            },
                        ]
                    ),
                    Response([])
                ],
                'expected_result': {
                    'main': '0928jlskdfj',
                    'iss76': 'kjsadfwi'
                }
            },
            {
                'arguments': {
                    'owner': 'moevm',
                    'repo': 'asm_web_debug',
                    'per_page': 1
                },
                'send_calls': [
                    call(
                        '/repos/moevm/asm_web_debug/branches',
                        params={
                            'per_page': 1,
                            'page': 1
                        }
                    ),
                    call(
                        '/repos/moevm/asm_web_debug/branches',
                        params={
                            'per_page': 1,
                            'page': 2
                        }
                    ),
                    call(
                        '/repos/moevm/asm_web_debug/branches',
                        params={
                            'per_page': 1,
                            'page': 3
                        }
                    ),
                ],
                'send_se': [
                    Response(
                        [
                            {
                                'name': 'main',
                                'commit': {
                                    'sha': '0928jlskdfj'
                                }
                            },
                        ]
                    ),
                    Response(
                        [
                            {
                                'name': 'iss76',
                                'commit': {
                                    'sha': 'kjsadfwi'
                                }
                            },
                        ]
                    ),
                    Response([])
                ],
                'expected_result': {
                    'main': '0928jlskdfj',
                    'iss76': 'kjsadfwi'
                }
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case['send_se']

            buf = io.StringIO()
            with redirect_stdout(buf):
                with self.subTest(test_case=test_case):
                    rv = parser.get_list_repo_branches(**test_case['arguments'])
                    self.assertEqual(rv, test_case['expected_result'])

                    self.assertEqual(mock_send_get_request.mock_calls, test_case['send_calls'])

    @patch('webparsers.github_parser.GitHubParser.get_name_default_branch')
    @patch('webparsers.github_parser.GitHubParser.get_list_repo_branches')
    @patch('webparsers.github_parser.GitHubParser.get_sha_last_branch_commit')
    @patch('webparsers.github_parser.GitHubParser.get_files_generator_from_sha_commit')
    def test_get_files_generator_from_repo_url(self, mock_get_files_generator_from_sha_commit,
                                               mock_get_sha_last_branch_commit,
                                               mock_get_list_repo_branches,
                                               mock_get_name_default_branch):
        test_cases = [
            {
                'check_policy': 0,
                'arguments': {
                    'repo_url': 'https://github.com/OSLL/code-plagiarism',
                },
                'name_default_branch': 'iss76',
                'branch_sha': 'uixbwupreiljlsdf',
                'branches_dict': None,
                'files': [('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py')],
                'expected_result': [
                    ('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py'),
                ]
            },
            {
                'check_policy': 1,
                'arguments': {
                    'repo_url': 'https://github.com/OSLL/code-plagiarism',
                },
                'name_default_branch': None,
                'branch_sha': None,
                'branches_dict': {
                    'master': 'iobiqirsad',
                    'iss76': 'iobxzewqrsf'
                },
                'files': [('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py')],
                'expected_result': [
                    ('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py'),
                    ('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py')
                ]
            },
        ]

        for test_case in test_cases:
            parser = GitHubParser(check_policy=test_case['check_policy'])
            mock_get_files_generator_from_sha_commit.reset_mock()
            mock_get_list_repo_branches.reset_mock()
            mock_get_sha_last_branch_commit.reset_mock()
            mock_get_name_default_branch.reset_mock()

            mock_get_name_default_branch.return_value = test_case['name_default_branch']
            mock_get_sha_last_branch_commit.return_value = test_case['branch_sha']
            mock_get_files_generator_from_sha_commit.return_value = test_case['files']
            mock_get_list_repo_branches.return_value = test_case['branches_dict']

            with self.subTest(test_case=test_case):
                rv = list(parser.get_files_generator_from_repo_url(**test_case['arguments']))
                self.assertEqual(rv, test_case['expected_result'])

    @patch('webparsers.github_parser.GitHubParser.get_file_content_from_sha')
    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_file_from_url(self, mock_send_get_request,
                               mock_get_file_content_from_sha):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'file_url': 'https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/astfeatures.py'
                },
                'send_rv': Response({'sha': 'ioujxbwurqer'}),
                'get_file_content_rv': ('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py'),
                'expected_result': ('Some code 1', 'https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py'),
            }
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.return_value = test_case['send_rv']
            mock_get_file_content_from_sha.return_value = test_case['get_file_content_rv']

            with self.subTest(test_case=test_case):
                rv = parser.get_file_from_url(**test_case['arguments'])
                self.assertEqual(rv, test_case['expected_result'])

    @patch('webparsers.github_parser.GitHubParser.get_file_content_from_sha')
    @patch('webparsers.github_parser.GitHubParser.get_files_generator_from_sha_commit')
    @patch('webparsers.github_parser.GitHubParser.send_get_request')
    def test_get_files_generator_from_dir_url(self, mock_send_get_request,
                                              mock_get_files_generator_from_sha_commit,
                                              mock_get_file_content_from_sha):
        class Response:
            def __init__(self, response):
                self.response_json = response

            def json(self):
                return self.response_json

        test_cases = [
            {
                'arguments': {
                    'dir_url': 'https://github.com/OSLL/code-plagiarism/tree/main/src'
                },
                'send_rv': Response(
                    [
                        {
                            'path': 'src',
                            'type': 'dir',
                            'sha': 'xvbupqrjdf',
                        },
                        {
                            'path': 'src',
                            'name': 'main.py',
                            'type': 'file',
                            'sha': 'iouxpoewre',
                        }
                    ]
                ),
                'files_gen': ['dummy 1', 'dummy 2'],
                'file_gen': 'dummy 3',
                'expected_result': ['dummy 1', 'dummy 2', 'dummy 3']
            }
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.return_value = test_case['send_rv']
            mock_get_files_generator_from_sha_commit.return_value = test_case['files_gen']
            mock_get_file_content_from_sha.return_value = test_case['file_gen']

            with self.subTest(test_case=test_case):
                rv = list(parser.get_files_generator_from_dir_url(**test_case['arguments']))
                self.assertEqual(rv, test_case['expected_result'])

if __name__ == '__main__':
    unittest.main()

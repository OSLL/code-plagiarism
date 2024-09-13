import base64
import io
import re
import unittest
from contextlib import redirect_stdout
from typing import Final
from unittest.mock import MagicMock, call, patch

from webparsers.github_parser import GitHubParser
from webparsers.types import Branch, Commit, PullRequest, Repository, WorkInfo

_REQUEST_PARAMS_1 = {"per_page": 100, "page": 1}
_REQUEST_PARAMS_3 = {"per_page": 100, "page": 3}

_COMMIT1: Final[Commit] = Commit("zkueqwrkjsalu", "2022-12-20T20:13:58Z")
_COMMIT2: Final[Commit] = Commit("xuwerlkjlsaoewerl", "2022-12-20T20:13:58Z")

_COMMIT1_RESP = [{"sha": _COMMIT1.sha, "commit": {"author": {"date": _COMMIT1.date}}}]
_COMMIT2_RESP = [{"sha": _COMMIT2.sha, "commit": {"author": {"date": _COMMIT2.date}}}]

_BRANCH1: Final[Branch] = Branch("iss76", _COMMIT1)
_BRANCH2: Final[Branch] = Branch("iss78", _COMMIT2)

_GET_FILE_CONTENT_RES: Final[list[WorkInfo]] = [
    WorkInfo(
        "Some code 2",
        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/utils.py",
        _BRANCH1.last_commit,
    ),
    WorkInfo(
        "Some code 3",
        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/tests.py",
        _BRANCH1.last_commit,
    ),
    WorkInfo(
        "Some code 1",
        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py",
        _BRANCH1.last_commit,
    ),
]


class Response:
    def __init__(
        self,
        response_json: list | dict | None = None,
        status_code: int = 200,
        message: str | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.response_json = response_json if response_json else {}
        if self.message and isinstance(self.response_json, dict):
            self.response_json.update({"message": self.message})

    def json(self):
        return self.response_json

    def raise_for_status(self):
        return None


class TestGitHubParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    def test__is_accepted_extension(self):
        test_cases = [
            {
                "arguments": {"path": "some/path/module.py"},
                "parser": GitHubParser(),
                "expected_result": True,
            },
            {
                "arguments": {"path": "some/path/module.cpp"},
                "parser": GitHubParser(),
                "expected_result": True,
            },
            {
                "arguments": {"path": "some/path/module.c"},
                "parser": GitHubParser(),
                "expected_result": True,
            },
            {
                "arguments": {"path": "some/path/module.in.py"},
                "parser": GitHubParser(),
                "expected_result": True,
            },
            {
                "arguments": {"path": "some/path/module.c"},
                "parser": GitHubParser(file_extensions=(re.compile("py"),)),
                "expected_result": False,
            },
            {
                "arguments": {"path": "some/path/module.in"},
                "parser": GitHubParser(
                    file_extensions=(
                        re.compile("cpp"),
                        re.compile("c"),
                    )
                ),
                "expected_result": False,
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                rv = test_case["parser"]._is_accepted_extension(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

    @patch("webparsers.github_parser.requests.get")
    def test_send_get_request(self, mock_get: MagicMock):
        test_cases = [
            {
                "arguments": {"api_url": "users/moevm/repos", "params": {}},
                "get_arguments": [],
                "get_posargs": ["https://api.github.com/users/moevm/repos"],
                "get_kwargs": {
                    "headers": {"accept": "application/vnd.github.v3+json"},
                    "params": {},
                },
                "response": Response(status_code=200),
            }
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_get.reset_mock()
            mock_get.return_value = test_case["response"]

            with self.subTest(test_case=test_case):
                rv = parser.send_get_request(**test_case["arguments"])
                self.assertEqual(rv, test_case["response"])

                mock_get.assert_called_once_with(
                    *test_case["get_posargs"], **test_case["get_kwargs"]
                )

    @patch("webparsers.github_parser.requests.get")
    def test_send_get_request_bad(self, mock_get: MagicMock):
        test_cases = [
            {
                "arguments": {"api_url": "Test/url", "params": {}},
                "get_arguments": [],
                "get_posargs": ["https://api.github.com/Test/url"],
                "get_kwargs": {
                    "headers": {"accept": "application/vnd.github.v3+json"},
                    "params": {},
                },
                "response": Response(status_code=403, message="Not Found"),
                "raised": SystemExit,
            },
            {
                "arguments": {"api_url": "bad/link", "params": {}},
                "get_posargs": ["https://api.github.com/bad/link"],
                "get_kwargs": {
                    "headers": {"accept": "application/vnd.github.v3+json"},
                    "params": {},
                },
                "response": Response(status_code=403),
                "raised": KeyError,
            },
            {
                "arguments": {"api_url": "bad/link", "params": _REQUEST_PARAMS_3},
                "get_posargs": ["https://api.github.com/bad/link"],
                "get_kwargs": {
                    "headers": {"accept": "application/vnd.github.v3+json"},
                    "params": _REQUEST_PARAMS_3,
                },
                "response": Response(status_code=403),
                "raised": KeyError,
            },
            {
                "arguments": {"api_url": "bad/link", "params": {}},
                "token": "test_token",
                "get_posargs": ["https://api.github.com/bad/link"],
                "get_kwargs": {
                    "headers": {
                        "accept": "application/vnd.github.v3+json",
                        "Authorization": "token test_token",
                    },
                    "params": {},
                },
                "response": Response(status_code=403),
                "raised": KeyError,
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            if test_case.get("token"):
                parser = GitHubParser(access_token=test_case["token"])

            mock_get.reset_mock()
            mock_get.return_value = test_case["response"]

            with self.subTest(test_case=test_case):
                with self.assertRaises(test_case["raised"]):
                    parser.send_get_request(**test_case["arguments"])

                mock_get.assert_called_once_with(
                    *test_case["get_posargs"], **test_case["get_kwargs"]
                )

    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_list_of_repos(self, mock_send_get_request: MagicMock):
        test_cases = [
            {
                "arguments": {"owner": "OSLL", "reg_exp": None},
                "send_calls": [
                    call("/users/OSLL"),
                    call("/users/OSLL/repos", params=_REQUEST_PARAMS_1),
                ],
                "send_rvs": [Response({"type": "User"}), Response([])],
                "expected_result": [],
            },
            {
                "arguments": {"owner": "OSLL", "reg_exp": None},
                "send_calls": [
                    call("/users/OSLL"),
                    call("/orgs/OSLL/repos", params=_REQUEST_PARAMS_1),
                ],
                "send_rvs": [
                    Response({"type": "Organization"}),
                    Response(
                        [
                            {
                                "name": "asm_web_debug",
                                "html_url": "https://github.com/OSLL/asm_web_debug",
                            },
                            {
                                "name": "aido-auto-feedback",
                                "html_url": "https://github.com/OSLL/aido-auto-feedback",
                            },
                            {
                                "name": "MD-Code_generator",
                                "html_url": "https://github.com/OSLL/MD-Code_generator",
                            },
                            {
                                "name": "code-plagiarism",
                                "html_url": "https://github.com/OSLL/code-plagiarism",
                            },
                        ]
                    ),
                ],
                "expected_result": [
                    Repository("asm_web_debug", "https://github.com/OSLL/asm_web_debug"),
                    Repository(
                        "aido-auto-feedback",
                        "https://github.com/OSLL/aido-auto-feedback",
                    ),
                    Repository("MD-Code_generator", "https://github.com/OSLL/MD-Code_generator"),
                    Repository("code-plagiarism", "https://github.com/OSLL/code-plagiarism"),
                ],
            },
            {
                "arguments": {"owner": "OSLL", "reg_exp": r"\ba"},
                "send_calls": [
                    call("/users/OSLL"),
                    call("/orgs/OSLL/repos", params=_REQUEST_PARAMS_1),
                ],
                "send_rvs": [
                    Response({"type": "Organization"}),
                    Response(
                        [
                            {
                                "name": "asm_web_debug",
                                "html_url": "https://github.com/OSLL/asm_web_debug",
                            },
                            {
                                "name": "aido-auto-feedback",
                                "html_url": "https://github.com/OSLL/aido-auto-feedback",
                            },
                            {
                                "name": "MD-Code_generator",
                                "html_url": "https://github.com/OSLL/MD-Code_generator",
                            },
                            {
                                "name": "code-plagiarism",
                                "html_url": "https://github.com/OSLL/code-plagiarism",
                            },
                        ]
                    ),
                ],
                "expected_result": [
                    Repository("asm_web_debug", "https://github.com/OSLL/asm_web_debug"),
                    Repository(
                        "aido-auto-feedback",
                        "https://github.com/OSLL/aido-auto-feedback",
                    ),
                ],
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case["send_rvs"]

            with self.subTest(test_case=test_case):
                rv = parser.get_list_of_repos(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

                self.assertEqual(mock_send_get_request.mock_calls, test_case["send_calls"])

    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_list_of_repos_bad(self, mock_send_get_request: MagicMock):
        test_cases = [
            {
                "arguments": {"owner": "OSLL", "reg_exp": None},
                "send_calls": [call("/users/OSLL")],
                "send_rvs": [Response({"type": "BadType"})],
                "raised": SystemExit,
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case["send_rvs"]

            with self.subTest(test_case=test_case):
                with self.assertRaises(test_case["raised"]):
                    parser.get_list_of_repos(**test_case["arguments"])

                self.assertEqual(mock_send_get_request.mock_calls, test_case["send_calls"])

    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_pulls_info(self, mock_send_get_request: MagicMock):
        test_cases = [
            {
                "arguments": {"owner": "OSLL", "repo": "code-plagiarism"},
                "send_calls": [
                    call("/repos/OSLL/code-plagiarism/pulls", params=_REQUEST_PARAMS_1)
                ],
                "send_rvs": [Response([])],
                "expected_result": [],
            },
            {
                "arguments": {"owner": "OSLL", "repo": "code-plagiarism"},
                "send_calls": [
                    call("/repos/OSLL/code-plagiarism/pulls", params=_REQUEST_PARAMS_1),
                    call(
                        "https://api.github.com/repos/OSLL/code-plagiarism/pulls/1/commits",
                        address="",
                    ),
                    call(
                        "https://api.github.com/repos/OSLL/code-plagiarism/pulls/2/commits",
                        address="",
                    ),
                    call(
                        "https://api.github.com/repos/OSLL/code-plagiarism/pulls/3/commits",
                        address="",
                    ),
                    call(
                        "https://api.github.com/repos/OSLL/code-plagiarism/pulls/4/commits",
                        address="",
                    ),
                ],
                "send_rvs": [
                    Response(
                        [
                            {
                                "commits_url": "https://api.github.com/repos/OSLL/code-plagiarism/pulls/1/commits",
                                "number": 1,
                                "head": {"label": "code-plagiarism:cp_130"},
                                "state": "Open",
                                "draft": False,
                            },
                            {
                                "commits_url": "https://api.github.com/repos/OSLL/code-plagiarism/pulls/2/commits",
                                "number": 2,
                                "head": {"label": "code-plagiarism:cp_110"},
                                "state": "Open",
                                "draft": True,
                            },
                            {
                                "commits_url": "https://api.github.com/repos/OSLL/code-plagiarism/pulls/3/commits",
                                "number": 3,
                                "head": {"label": "code-plagiarism:bag_fix"},
                                "state": "Open",
                                "draft": False,
                            },
                            {
                                "commits_url": "https://api.github.com/repos/OSLL/code-plagiarism/pulls/4/commits",
                                "number": 4,
                                "head": {"label": "code-plagiarism:lite"},
                                "state": "Open",
                                "draft": True,
                            },
                        ]
                    ),
                    Response([{"sha": "jskfjsjskjfl"}]),
                    Response([{"sha": "jzxvjipwerknmzxvj"}]),
                    Response([{"sha": "jskfjsjskjfl"}]),
                    Response([{"sha": "jzxvjipwerknmzxvj"}]),
                ],
                "expected_result": [
                    PullRequest(
                        number=1,
                        last_commit_sha="jskfjsjskjfl",
                        owner="code-plagiarism",
                        branch="cp_130",
                        state="Open",
                        draft=False,
                    ),
                    PullRequest(
                        number=2,
                        last_commit_sha="jzxvjipwerknmzxvj",
                        owner="code-plagiarism",
                        branch="cp_110",
                        state="Open",
                        draft=True,
                    ),
                    PullRequest(
                        number=3,
                        last_commit_sha="jskfjsjskjfl",
                        owner="code-plagiarism",
                        branch="bag_fix",
                        state="Open",
                        draft=False,
                    ),
                    PullRequest(
                        number=4,
                        last_commit_sha="jzxvjipwerknmzxvj",
                        owner="code-plagiarism",
                        branch="lite",
                        state="Open",
                        draft=True,
                    ),
                ],
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case["send_rvs"]
            with self.subTest(test_case=test_case):
                rv = parser.get_pulls_info(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

                assert len(mock_send_get_request.mock_calls) == len(test_case["send_calls"])
                for actual_call, expected_call in zip(
                    mock_send_get_request.mock_calls,
                    test_case["send_calls"],
                    strict=True,
                ):
                    assert actual_call == expected_call

    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_name_default_branch(self, mock_send_get_request: MagicMock):
        test_cases = [
            {
                "arguments": {"owner": "OSLL", "repo": "aido-auto-feedback"},
                "send_calls": [call("/repos/OSLL/aido-auto-feedback")],
                "send_rv": Response({"default_branch": "main"}),
                "expected_result": "main",
            },
            {
                "arguments": {"owner": "moevm", "repo": "asm_web_debug"},
                "send_calls": [call("/repos/moevm/asm_web_debug")],
                "send_rv": Response({"default_branch": "issue2"}),
                "expected_result": "issue2",
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.return_value = test_case["send_rv"]

            with self.subTest(test_case=test_case):
                rv = parser.get_name_default_branch(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

                self.assertEqual(mock_send_get_request.mock_calls, test_case["send_calls"])

    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test__get_branch_last_commit_info(self, mock_send_get_request: MagicMock):
        _COMMIT1 = {
            "sha": "jal934304",
            "commit": {"author": {"name": "OSLL", "date": "2022-12-29T10:10:41Z"}},
        }
        _COMMIT2 = {
            "sha": "xyuwr934h",
            "commit": {"author": {"name": "OSLL", "date": "2022-11-13T10:15:41Z"}},
        }

        test_cases = [
            {
                "arguments": {"owner": "OSLL", "repo": "aido-auto-feedback"},
                "send_calls": [call("/repos/OSLL/aido-auto-feedback/branches/main")],
                "send_rv": Response({"commit": _COMMIT1}),
                "expected_result": _COMMIT1,
            },
            {
                "arguments": {
                    "owner": "moevm",
                    "repo": "asm_web_debug",
                    "branch": "iss76",
                },
                "send_calls": [call("/repos/moevm/asm_web_debug/branches/iss76")],
                "send_rv": Response({"commit": _COMMIT2}),
                "expected_result": _COMMIT2,
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.return_value = test_case["send_rv"]

            with self.subTest(test_case=test_case):
                rv = parser._get_branch_last_commit_info(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

                self.assertEqual(mock_send_get_request.mock_calls, test_case["send_calls"])

    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_file_content_by_sha(self, mock_send_get_request: MagicMock):
        test_cases = [
            {
                "arguments": {
                    "owner": "OSLL",
                    "repo": "aido-auto-feedback",
                    "blob_sha": "kljsdfkiwe0341",
                    "commit_info": _COMMIT1,
                    "file_path": "http://api.github.com/repos",
                },
                "send_calls": [call("/repos/OSLL/aido-auto-feedback/git/blobs/kljsdfkiwe0341")],
                "send_rv": Response({"content": base64.b64encode(b"Good message")}),
                "expected_result": WorkInfo(
                    "Good message", "http://api.github.com/repos", _COMMIT1
                ),
            },
            {
                "arguments": {
                    "owner": "moevm",
                    "repo": "asm_web_debug",
                    "blob_sha": "jsadlkf3904",
                    "commit_info": _COMMIT2,
                    "file_path": "http://api.github.com/test",
                },
                "send_calls": [call("/repos/moevm/asm_web_debug/git/blobs/jsadlkf3904")],
                "send_rv": Response({"content": base64.b64encode(b"Bad\xee\xeemessage")}),
                "expected_result": WorkInfo("Badmessage", "http://api.github.com/test", _COMMIT2),
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.return_value = test_case["send_rv"]

            buf = io.StringIO()
            with redirect_stdout(buf), self.subTest(test_case=test_case):
                rv = parser.get_file_content_by_sha(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

                self.assertEqual(mock_send_get_request.mock_calls, test_case["send_calls"])

    @patch("webparsers.github_parser.GitHubParser.get_file_content_by_sha")
    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_files_generator_from_sha_commit(
        self, mock_send_get_request: MagicMock, mock_get_file_content_by_sha: MagicMock
    ):
        test_cases = [
            {
                "arguments": {
                    "owner": "OSLL",
                    "repo": "aido-auto-feedback",
                    "branch": _BRANCH1,
                    "sha": _BRANCH1.last_commit.sha,
                },
                "send_calls": [
                    call("/repos/OSLL/aido-auto-feedback/git/trees/zkueqwrkjsalu"),
                    call(
                        api_url="/repos/OSLL/aido-auto-feedback/commits",
                        params={
                            "path": "/src",
                            "page": 1,
                            "per_page": 1,
                            "sha": _BRANCH1.name,
                        },
                    ),
                    call("/repos/OSLL/aido-auto-feedback/git/trees/jslkfjjeuwijsdmvd"),
                    call(
                        api_url="/repos/OSLL/aido-auto-feedback/commits",
                        params={
                            "path": "/src/utils.py",
                            "page": 1,
                            "per_page": 1,
                            "sha": _BRANCH1.name,
                        },
                    ),
                    call(
                        api_url="/repos/OSLL/aido-auto-feedback/commits",
                        params={
                            "path": "/src/tests.py",
                            "page": 1,
                            "per_page": 1,
                            "sha": _BRANCH1.name,
                        },
                    ),
                    call(
                        api_url="/repos/OSLL/aido-auto-feedback/commits",
                        params={
                            "path": "/main.py",
                            "page": 1,
                            "per_page": 1,
                            "sha": _BRANCH1.name,
                        },
                    ),
                ],
                "send_se": [
                    Response(
                        {
                            "tree": [
                                {
                                    "type": "tree",
                                    "path": "src",
                                    "sha": "jslkfjjeuwijsdmvd",
                                },
                                {
                                    "type": "blob",
                                    "path": "main.py",
                                    "sha": "ixiuerjs9430",
                                },
                            ],
                        }
                    ),
                    Response(_COMMIT1_RESP),
                    Response(
                        {
                            "tree": [
                                {
                                    "type": "blob",
                                    "path": "utils.py",
                                    "sha": "uwrcbasrew94",
                                },
                                {
                                    "type": "blob",
                                    "path": "tests.py",
                                    "sha": "vbuqcvxpiwe",
                                },
                            ]
                        }
                    ),
                    Response(_COMMIT2_RESP),
                    Response(_COMMIT1_RESP),
                    Response(_COMMIT2_RESP),
                ],
                "get_file_content_calls": [
                    call(
                        "OSLL",
                        "aido-auto-feedback",
                        "uwrcbasrew94",
                        _COMMIT2,
                        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/utils.py",
                    ),
                    call(
                        "OSLL",
                        "aido-auto-feedback",
                        "vbuqcvxpiwe",
                        _COMMIT1,
                        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/tests.py",
                    ),
                    call(
                        "OSLL",
                        "aido-auto-feedback",
                        "ixiuerjs9430",
                        _COMMIT2,
                        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/main.py",
                    ),
                ],
                "get_file_content_se": _GET_FILE_CONTENT_RES,
                "expected_result": _GET_FILE_CONTENT_RES,
            },
            {
                "arguments": {
                    "owner": "OSLL",
                    "repo": "aido-auto-feedback",
                    "branch": _BRANCH1,
                    "sha": _BRANCH1.last_commit.sha,
                    "path_regexp": re.compile("s[.]py"),
                },
                "send_calls": [
                    call("/repos/OSLL/aido-auto-feedback/git/trees/zkueqwrkjsalu"),
                    call(
                        api_url="/repos/OSLL/aido-auto-feedback/commits",
                        params={
                            "path": "/src",
                            "page": 1,
                            "per_page": 1,
                            "sha": _BRANCH1.name,
                        },
                    ),
                    call("/repos/OSLL/aido-auto-feedback/git/trees/jslkfjjeuwijsdmvd"),
                    call(
                        api_url="/repos/OSLL/aido-auto-feedback/commits",
                        params={
                            "path": "/src/utils.py",
                            "page": 1,
                            "per_page": 1,
                            "sha": _BRANCH1.name,
                        },
                    ),
                    call(
                        api_url="/repos/OSLL/aido-auto-feedback/commits",
                        params={
                            "path": "/src/tests.py",
                            "page": 1,
                            "per_page": 1,
                            "sha": _BRANCH1.name,
                        },
                    ),
                ],
                "send_se": [
                    Response(
                        {
                            "tree": [
                                {
                                    "type": "tree",
                                    "path": "src",
                                    "sha": "jslkfjjeuwijsdmvd",
                                },
                                {
                                    "type": "blob",
                                    "path": "main.py",
                                    "sha": "ixiuerjs9430",
                                },
                            ],
                        }
                    ),
                    Response(_COMMIT1_RESP),
                    Response(
                        {
                            "tree": [
                                {
                                    "type": "blob",
                                    "path": "utils.py",
                                    "sha": "uwrcbasrew94",
                                },
                                {
                                    "type": "blob",
                                    "path": "tests.py",
                                    "sha": "vbuqcvxpiwe",
                                },
                            ]
                        }
                    ),
                    Response(_COMMIT2_RESP),
                    Response(_COMMIT1_RESP),
                    Response(_COMMIT2_RESP),
                ],
                "get_file_content_calls": [
                    call(
                        "OSLL",
                        "aido-auto-feedback",
                        "uwrcbasrew94",
                        _COMMIT2,
                        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/utils.py",
                    ),
                    call(
                        "OSLL",
                        "aido-auto-feedback",
                        "vbuqcvxpiwe",
                        _COMMIT1,
                        "https://github.com/OSLL/aido-auto-feedback/blob/iss76/src/tests.py",
                    ),
                ],
                "get_file_content_se": _GET_FILE_CONTENT_RES[:2],
                "expected_result": _GET_FILE_CONTENT_RES[:2],
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case["send_se"]
            mock_get_file_content_by_sha.reset_mock()
            mock_get_file_content_by_sha.side_effect = test_case["get_file_content_se"]

            with self.subTest(test_case=test_case):
                rv = list(parser.get_files_generator_from_sha_commit(**test_case["arguments"]))
                self.assertEqual(rv, test_case["expected_result"])

                assert mock_send_get_request.mock_calls == test_case["send_calls"]
                assert (
                    mock_get_file_content_by_sha.mock_calls == test_case["get_file_content_calls"]
                )

    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_list_repo_branches(self, mock_send_get_request: MagicMock):
        _COMMIT_DATE = "2022-12-29T10:10:41Z"
        _BRANCH_INFO1 = {
            "name": "main",
            "commit": {
                "sha": "0928jlskdfj",
                "commit": {"author": {"date": _COMMIT_DATE}},
            },
        }
        _BRANCH_INFO2 = {
            "name": "iss76",
            "commit": {"sha": "kjsadfwi", "commit": {"author": {"date": _COMMIT_DATE}}},
        }

        test_cases = [
            {
                "arguments": {"owner": "OSLL", "repo": "aido-auto-feedback"},
                "send_calls": [
                    call(
                        "/repos/OSLL/aido-auto-feedback/branches",
                        params=_REQUEST_PARAMS_1,
                    ),
                ],
                "send_se": [
                    Response([_BRANCH_INFO1, _BRANCH_INFO2]),
                ],
                "expected_result": [
                    Branch("main", Commit("0928jlskdfj", "2022-12-29T10:10:41Z")),
                    Branch("iss76", Commit("kjsadfwi", "2022-12-29T10:10:41Z")),
                ],
            },
            {
                "arguments": {
                    "owner": "moevm",
                    "repo": "asm_web_debug",
                },
                "send_calls": [
                    call("/repos/moevm/asm_web_debug/branches", params=_REQUEST_PARAMS_1),
                ],
                "send_se": [
                    Response([_BRANCH_INFO1, _BRANCH_INFO2]),
                ],
                "expected_result": [
                    Branch("main", Commit("0928jlskdfj", _COMMIT_DATE)),
                    Branch("iss76", Commit("kjsadfwi", _COMMIT_DATE)),
                ],
            },
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.reset_mock()
            mock_send_get_request.side_effect = test_case["send_se"]

            buf = io.StringIO()
            with redirect_stdout(buf), self.subTest(test_case=test_case):
                rv = parser.get_list_repo_branches(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

                self.assertEqual(mock_send_get_request.mock_calls, test_case["send_calls"])

    @patch("webparsers.github_parser.GitHubParser.get_name_default_branch")
    @patch("webparsers.github_parser.GitHubParser.get_list_repo_branches")
    @patch("webparsers.github_parser.GitHubParser._get_branch_last_commit_info")
    @patch("webparsers.github_parser.GitHubParser.get_files_generator_from_sha_commit")
    def test_get_files_generator_from_repo_url(
        self,
        mock_get_files_generator_from_sha_commit: MagicMock,
        mock_get_sha_last_branch_commit: MagicMock,
        mock_get_list_repo_branches: MagicMock,
        mock_get_name_default_branch: MagicMock,
    ):
        test_cases = [
            {
                "check_all": 0,
                "arguments": {
                    "repo_url": "https://github.com/OSLL/code-plagiarism",
                },
                "name_default_branch": "iss76",
                "last_branch_commit": _COMMIT1_RESP[0],
                "branches": None,
                "files": [_GET_FILE_CONTENT_RES[2]],
                "expected_result": [_GET_FILE_CONTENT_RES[2]],
            },
            {
                "check_all": 1,
                "arguments": {
                    "repo_url": "https://github.com/OSLL/code-plagiarism",
                },
                "name_default_branch": None,
                "last_branch_commit": None,
                "branches": [_BRANCH1, _BRANCH2],
                "files": [_GET_FILE_CONTENT_RES[2]],
                "expected_result": [
                    _GET_FILE_CONTENT_RES[2],
                    _GET_FILE_CONTENT_RES[2],
                ],
            },
        ]

        for test_case in test_cases:
            parser = GitHubParser(check_all=test_case["check_all"])
            mock_get_files_generator_from_sha_commit.reset_mock()
            mock_get_list_repo_branches.reset_mock()
            mock_get_sha_last_branch_commit.reset_mock()
            mock_get_name_default_branch.reset_mock()

            mock_get_name_default_branch.return_value = test_case["name_default_branch"]
            mock_get_sha_last_branch_commit.return_value = test_case["last_branch_commit"]
            mock_get_files_generator_from_sha_commit.return_value = test_case["files"]
            mock_get_list_repo_branches.return_value = test_case["branches"]

            with self.subTest(test_case=test_case):
                rv = list(parser.get_files_generator_from_repo_url(**test_case["arguments"]))
                self.assertEqual(rv, test_case["expected_result"])

    @patch("webparsers.github_parser.GitHubParser.get_file_content_by_sha")
    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_file_from_url(
        self, mock_send_get_request: MagicMock, mock_get_file_content_by_sha: MagicMock
    ):
        test_cases = [
            {
                "arguments": {
                    "file_url": "https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/astfeatures.py"
                },
                "send_se": [
                    Response({"sha": "ioujxbwurqer"}),
                    Response(_COMMIT1_RESP),
                ],
                "get_file_content_rv": _GET_FILE_CONTENT_RES[2],
                "expected_result": _GET_FILE_CONTENT_RES[2],
            }
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.side_effect = test_case["send_se"]
            mock_get_file_content_by_sha.return_value = test_case["get_file_content_rv"]

            with self.subTest(test_case=test_case):
                rv = parser.get_file_from_url(**test_case["arguments"])
                self.assertEqual(rv, test_case["expected_result"])

    @patch("webparsers.github_parser.GitHubParser.get_file_content_by_sha")
    @patch("webparsers.github_parser.GitHubParser.get_files_generator_from_sha_commit")
    @patch("webparsers.github_parser.GitHubParser.send_get_request")
    def test_get_files_generator_from_dir_url(
        self,
        mock_send_get_request: MagicMock,
        mock_get_files_generator_from_sha_commit: MagicMock,
        mock_get_file_content_by_sha: MagicMock,
    ):
        test_cases = [
            {
                "arguments": {"dir_url": "https://github.com/OSLL/code-plagiarism/tree/main/src"},
                "send_se": [
                    Response(
                        [
                            {"path": "src", "type": "dir", "sha": "xvbupqrjdf"},
                            {
                                "path": "src",
                                "name": "main.py",
                                "type": "file",
                                "sha": "iouxpoewre",
                            },
                        ]
                    ),
                    Response(_COMMIT1_RESP),
                    Response(_COMMIT2_RESP),
                ],
                "files_gen": _GET_FILE_CONTENT_RES[:2],
                "file_gen": _GET_FILE_CONTENT_RES[2],
                "expected_result": _GET_FILE_CONTENT_RES,
            }
        ]

        parser = GitHubParser()
        for test_case in test_cases:
            mock_send_get_request.side_effect = test_case["send_se"]
            mock_get_files_generator_from_sha_commit.return_value = test_case["files_gen"]
            mock_get_file_content_by_sha.return_value = test_case["file_gen"]

            with self.subTest(test_case=test_case):
                rv = list(parser.get_files_generator_from_dir_url(**test_case["arguments"]))
                self.assertEqual(rv, test_case["expected_result"])


if __name__ == "__main__":
    unittest.main()

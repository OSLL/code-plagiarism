import pytest
from webparsers.types import GitHubContentUrl, GitHubRepoUrl, GitHubUrl


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("https://github.com/OSLL", ["https:", "", "github.com", "OSLL"]),
        (
            "http://github.com/OSLL/code-plagiarism/",
            ["http:", "", "github.com", "OSLL", "code-plagiarism"],
        ),
        ("ttps://github.com/OSLL", ValueError),
        ("https:/j/github.com/OSLL", ValueError),
        ("https://githUb.com/OSLL", ValueError),
        ("https:/", ValueError),
    ],
)
def test_github_url(arg, expected):
    if type(expected) == type and issubclass(expected, Exception):
        with pytest.raises(expected):
            GitHubUrl(arg)
    else:
        gh_url = GitHubUrl(arg)
        assert gh_url.url_parts == expected
        assert gh_url.protocol == expected[0][:-1]
        assert gh_url.host == expected[2]


@pytest.mark.parametrize(
    "arg, expected",
    [
        (
            "http://github.com/OSLL/code-plagiarism/",
            ["http:", "", "github.com", "OSLL", "code-plagiarism"],
        ),
        (
            "http://github.com/OSLL/samples",
            ["http:", "", "github.com", "OSLL", "samples"],
        ),
        ("https://github.com/OSLL", ValueError),
        ("ttps://github.com/OSLL", ValueError),
        ("https:/j/github.com/OSLL", ValueError),
        ("https://githUb.com/OSLL", ValueError),
        ("https:/", ValueError),
    ],
)
def test_github_repo_url(arg, expected):
    if type(expected) == type and issubclass(expected, Exception):
        with pytest.raises(expected):
            GitHubRepoUrl(arg)
    else:
        gh_repo_url = GitHubRepoUrl(arg)
        assert gh_repo_url.url_parts == expected
        assert gh_repo_url.protocol == expected[0][:-1]
        assert gh_repo_url.host == expected[2]
        assert gh_repo_url.owner == expected[3]
        assert gh_repo_url.repo == expected[4]


@pytest.mark.parametrize(
    "arg, expected, path",
    [
        (
            "https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/astfeatures.py",
            ["https:", "", "github.com", "OSLL", "code-plagiarism", "blob", "main"],
            "src/codeplag/astfeatures.py",
        ),
        (
            "https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/logger.py",
            ["https:", "", "github.com", "OSLL", "code-plagiarism", "blob", "main"],
            "src/codeplag/logger.py",
        ),
        ("https://github.com/OSLL", ValueError, ""),
        ("http://github.com/OSLL/code-plagiarism/", ValueError, ""),
        ("ttps://github.com/OSLL", ValueError, ""),
        ("https:/j/github.com/OSLL", ValueError, ""),
        ("https://githUb.com/OSLL", ValueError, ""),
        ("https:/", ValueError, ""),
    ],
)
def test_github_content_url(arg, expected, path):
    if type(expected) == type and issubclass(expected, Exception):
        with pytest.raises(expected):
            GitHubContentUrl(arg)
    else:
        gh_content_url = GitHubContentUrl(arg)
        for value in expected:
            assert value in gh_content_url.url_parts
        assert gh_content_url.protocol == expected[0][:-1]
        assert gh_content_url.host == expected[2]
        assert gh_content_url.owner == expected[3]
        assert gh_content_url.repo == expected[4]
        assert gh_content_url.branch == expected[6]
        assert gh_content_url.path == path

import pytest

from webparsers.types import GitHubContentUrl, GitHubRepoUrl, GitHubUrl


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://github.com/OSLL", ["https:", "", "github.com", "OSLL"]),
        (
            "http://github.com/OSLL/code-plagiarism/",
            ["http:", "", "github.com", "OSLL", "code-plagiarism"],
        ),
    ],
)
def test_github_url(url: str, expected: list[str]) -> None:
    gh_url = GitHubUrl(url)
    assert gh_url.url_parts == expected
    assert gh_url.protocol == expected[0][:-1]
    assert gh_url.host == expected[2]


@pytest.mark.parametrize(
    "url",
    [
        "ttps://github.com/OSLL",
        "https:/j/github.com/OSLL",
        "https://githUb.com/OSLL",
        "https:/",
    ],
)
def test_github_url_bad(url: str) -> None:
    with pytest.raises(ValueError):
        GitHubUrl(url)


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "http://github.com/OSLL/code-plagiarism/",
            ["http:", "", "github.com", "OSLL", "code-plagiarism"],
        ),
        (
            "http://github.com/OSLL/samples",
            ["http:", "", "github.com", "OSLL", "samples"],
        ),
    ],
)
def test_github_repo_url(url: str, expected: list[str]) -> None:
    gh_repo_url = GitHubRepoUrl(url)
    assert gh_repo_url.url_parts == expected
    assert gh_repo_url.protocol == expected[0][:-1]
    assert gh_repo_url.host == expected[2]
    assert gh_repo_url.owner == expected[3]
    assert gh_repo_url.repo == expected[4]


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/OSLL",
        "ttps://github.com/OSLL",
        "https:/j/github.com/OSLL",
        "https://githUb.com/OSLL",
        "https:/",
    ],
)
def test_github_repo_url_bad(url: str) -> None:
    with pytest.raises(ValueError):
        GitHubRepoUrl(url)


@pytest.mark.parametrize(
    "url, expected, path",
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
    ],
)
def test_github_content_url(url: str, expected: list[str], path: str) -> None:
    gh_content_url = GitHubContentUrl(url)
    for value in expected:
        assert value in gh_content_url.url_parts
    assert gh_content_url.protocol == expected[0][:-1]
    assert gh_content_url.host == expected[2]
    assert gh_content_url.owner == expected[3]
    assert gh_content_url.repo == expected[4]
    assert gh_content_url.branch == expected[6]
    assert gh_content_url.path == path


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/OSLL",
        "http://github.com/OSLL/code-plagiarism/",
        "ttps://github.com/OSLL",
        "https:/j/github.com/OSLL",
        "https://githUb.com/OSLL",
        "https:/",
    ],
)
def test_github_content_url_bad(url: str) -> None:
    with pytest.raises(ValueError):
        GitHubContentUrl(url)

from typing import List, NamedTuple, Pattern, Tuple, Type, TypeVar

from typing_extensions import Self

T = TypeVar("T", bound="GitHubUrl")


class GitHubUrl(str):
    protocol: str
    host: str = 'github.com'
    url_parts: List[str]

    def __new__(cls: Type[T], url: str) -> T:
        url_parts = url.rstrip('/').split('/')
        error_msg = f"'{url}' is incorrect link to GitHub"
        if (
            len(url_parts) < 3 or
            (url_parts[0] != 'https:' and url_parts[0] != 'http:') or
            url_parts[1] != '' or
            url_parts[2] != 'github.com'
        ):
            raise ValueError(error_msg)

        obj = str.__new__(cls, url)
        obj.protocol = url_parts[0][:-1]
        obj.url_parts = url_parts
        return obj


class GitHubRepoUrl(GitHubUrl):
    owner: str
    repo: str

    def __new__(cls: Type[Self], url: str) -> Self:
        obj = GitHubUrl.__new__(cls, url)
        if len(obj.url_parts) != 5:
            error_msg = f"'{url}' is incorrect link to GitHub repository"
            raise ValueError(error_msg)

        obj.owner = obj.url_parts[3]
        obj.repo = obj.url_parts[4]
        return obj


class GitHubContentUrl(GitHubUrl):
    owner: str
    repo: str
    branch: str
    path: str

    def __new__(cls: Type[Self], url: str) -> Self:
        obj = GitHubUrl.__new__(cls, url)
        if len(obj.url_parts) <= 7:
            error_msg = (
                f"'{url}' is incorrect link to content of GitHub repository"
            )
            raise ValueError(error_msg)

        obj.owner = obj.url_parts[3]
        obj.repo = obj.url_parts[4]
        obj.branch = obj.url_parts[6]
        obj.path = '/'.join(obj.url_parts[7:])
        return obj


class Repository(NamedTuple):
    name: str
    html_url: str


class Branch(NamedTuple):
    name: str
    last_commit_sha: str


class PullRequest(NamedTuple):
    number: int
    last_commit_sha: str
    owner: str
    branch: str
    state: str
    draft: bool


class WorkInfo(NamedTuple):
    code: str
    link: str  # TODO: use urlib for type or requests


Extensions = Tuple[Pattern, ...]

import base64
import logging
import re
import sys
from typing import Any, Final, Iterator

import requests
from typing_extensions import Self

from webparsers.types import (
    BranchInfo,
    Commit,
    Extensions,
    GitHubContentUrl,
    GitHubRepoUrl,
    PullRequest,
    Repository,
    WorkInfo,
)

_API_URL: Final[str] = "https://api.github.com"
_GH_URL: Final[str] = "https://github.com/"


class GitHubParser:
    def __init__(
        self: Self,
        file_extensions: Extensions | None = None,
        check_all: bool = False,
        access_token: str = "",
        logger: logging.Logger | None = None,
        session: requests.Session | None = None,
    ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.__session = session
        self.__file_extensions = file_extensions
        self.__check_all_branches = check_all
        self.__headers = {
            # Recommended
            "accept": "application/vnd.github.v3+json"
        }
        if access_token != "":
            self.__headers.update({"Authorization": "token " + access_token})

    def _is_accepted_extension(self: Self, path: str) -> bool:
        if self.__file_extensions is None:
            return True

        return any(re.search(extension, path) for extension in self.__file_extensions)

    def close_session(self: Self) -> None:
        if self.__session:
            self.__session.close()
            self.__session = None

    def send_get_request(
        self: Self, api_url: str, params: dict | None = None, address: str = _API_URL
    ) -> requests.Response:
        if params is None:
            params = {}

        if address and len(api_url) and api_url[0] != "/":
            address += "/"

        url = address + api_url

        # Check Ethernet connection and requests limit
        try:
            if self.__session is not None:
                response = self.__session.get(url, headers=self.__headers, params=params)
            else:
                response = requests.get(url, headers=self.__headers, params=params)
        except requests.exceptions.ConnectionError as err:
            self.logger.error("Connection error. Please check the Internet connection.")
            self.logger.debug(str(err))
            sys.exit(1)

        if response.status_code in [400, 403, 404]:
            self.logger.error(f"GitHub error: '{response.json()['message']}' for url '{url}'.")
            sys.exit(1)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error("The access token is bad.")
            self.logger.debug(str(err))
            sys.exit(1)

        return response

    def get_list_of_repos(
        self: Self, owner: str, reg_exp: re.Pattern | None = None
    ) -> list[Repository]:
        repos: list[Repository] = []
        response_json = self.send_get_request(f"/users/{owner}").json()
        user_type = response_json.get("type", "").lower()
        # TODO: classify yourself /user/repos
        if user_type == "user":
            api_url = f"/users/{owner}/repos"
        elif user_type == "organization":
            api_url = f"/orgs/{owner}/repos"
        else:
            self.logger.error("Not supported user type %s.", user_type)
            sys.exit(1)

        params = {"per_page": 100, "page": 1}
        while True:
            response_json = self.send_get_request(api_url, params=params).json()

            cnt = 0  # noqa: SIM113
            for repo in response_json:
                cnt += 1
                if (reg_exp is None) or re.search(reg_exp, repo["name"]) is not None:
                    repos.append(Repository(name=repo["name"], html_url=repo["html_url"]))
            if cnt < params["per_page"]:
                break

            params["page"] += 1

        return repos

    def get_pulls_info(self: Self, owner: str, repo: str) -> list[PullRequest]:
        pulls: list[PullRequest] = []
        api_url = f"/repos/{owner}/{repo}/pulls"
        params: dict[str, int] = {"per_page": 100, "page": 1}
        while True:
            response_json = self.send_get_request(api_url, params=params).json()

            cnt = 0  # noqa: SIM113
            for pull in response_json:
                cnt += 1
                commits = self.send_get_request(pull["commits_url"], address="").json()
                pull_owner, owner_branch = pull["head"]["label"].split(":", maxsplit=1)
                pulls.append(
                    PullRequest(
                        number=pull["number"],
                        last_commit_sha=commits[0]["sha"],
                        owner=pull_owner,
                        branch=owner_branch,
                        state=pull["state"],
                        draft=pull["draft"],
                    )
                )
            if cnt < params["per_page"]:
                break

            params["page"] += 1

        return pulls

    def get_name_default_branch(self: Self, owner: str, repo: str) -> str:
        api_url = f"/repos/{owner}/{repo}"
        response: dict[str, Any] = self.send_get_request(api_url).json()

        return response["default_branch"]

    def _get_branch_last_commit_info(
        self: Self, owner: str, repo: str, branch: str = "main"
    ) -> dict:
        api_url = f"/repos/{owner}/{repo}/branches/{branch}"
        response: dict[str, Any] = self.send_get_request(api_url).json()

        return response["commit"]

    def get_file_content_by_sha(
        self: Self, owner: str, repo: str, blob_sha: str, commit_info: Commit, file_path: str
    ) -> WorkInfo:
        api_url = f"/repos/{owner}/{repo}/git/blobs/{blob_sha}"
        response: dict[str, Any] = self.send_get_request(api_url).json()

        file_in_bytes: bytearray = bytearray(base64.b64decode(response["content"]))
        code = file_in_bytes.decode("utf-8", errors="ignore")

        return WorkInfo(code, file_path, commit_info)

    def _get_commit_info(self: Self, owner: str, repo: str, branch: str, path: str) -> Commit:
        commit_info: dict[str, Any] = self.send_get_request(
            api_url=f"/repos/{owner}/{repo}/commits",
            params={"path": path, "page": 1, "per_page": 1, "sha": branch},
        ).json()[0]

        return Commit(commit_info["sha"], commit_info["commit"]["author"]["date"])

    def get_files_generator_from_sha_commit(
        self: Self,
        owner: str,
        repo: str,
        branch: BranchInfo,
        sha: str,
        path: str = "",
        path_regexp: re.Pattern | None = None,
    ) -> Iterator[WorkInfo]:
        api_url = f"/repos/{owner}/{repo}/git/trees/{sha}"
        jresponse: dict[str, Any] = self.send_get_request(api_url).json()
        tree: list[dict[str, Any]] = jresponse["tree"]
        for node in tree:
            current_path = f"{path}/{node['path']}"
            full_link = f"{_GH_URL}{owner}/{repo}/blob/{branch.name}{current_path}"
            node_type = node["type"]
            if node_type == "tree":
                commit_info = self._get_commit_info(owner, repo, branch.name, current_path)
                yield from self.get_files_generator_from_sha_commit(
                    owner=owner,
                    repo=repo,
                    branch=BranchInfo(branch.name, commit_info),
                    sha=node["sha"],
                    path=current_path,
                    path_regexp=path_regexp,
                )
                continue
            elif (
                node_type != "blob"
                or not self._is_accepted_extension(current_path)
                or (path_regexp is not None and path_regexp.search(full_link) is None)
            ):
                continue

            commit_info = self._get_commit_info(owner, repo, branch.name, current_path)

            yield self.get_file_content_by_sha(owner, repo, node["sha"], commit_info, full_link)

    def get_list_repo_branches(self: Self, owner: str, repo: str) -> list[BranchInfo]:
        branches: list[BranchInfo] = []
        api_url: str = f"/repos/{owner}/{repo}/branches"
        params: dict[str, int] = {"per_page": 100, "page": 1}
        while True:
            response_json = self.send_get_request(api_url, params=params).json()

            cnt = 0  # noqa: SIM113
            for node in response_json:
                cnt += 1
                branch_name = node["name"]
                last_commit_sha = node["commit"]["sha"]
                commit_info = self._get_branch_last_commit_info(owner, repo, branch_name)
                branches.append(
                    BranchInfo(
                        name=branch_name,
                        last_commit=Commit(
                            last_commit_sha,
                            commit_info["commit"]["author"]["date"],
                        ),
                    )
                )
            if cnt < params["per_page"]:
                break

            params["page"] += 1

        return branches

    def get_files_generator_from_repo_url(
        self: Self, repo_url: str, path_regexp: re.Pattern | None = None
    ) -> Iterator[WorkInfo]:
        try:
            repo_url = GitHubRepoUrl(repo_url)
        except ValueError as error:
            self.logger.error(f"{repo_url} is incorrect link to GitHub repository")
            raise error

        if self.__check_all_branches:
            branches = self.get_list_repo_branches(repo_url.owner, repo_url.repo)
        else:
            default_branch = self.get_name_default_branch(repo_url.owner, repo_url.repo)
            commit_info = self._get_branch_last_commit_info(
                repo_url.owner, repo_url.repo, default_branch
            )
            branches = [
                BranchInfo(
                    name=default_branch,
                    last_commit=Commit(
                        commit_info["sha"],
                        commit_info["commit"]["author"]["date"],
                    ),
                )
            ]

        for branch in branches:
            yield from self.get_files_generator_from_sha_commit(
                owner=repo_url.owner,
                repo=repo_url.repo,
                branch=branch,
                sha=branch.last_commit.sha,
                path_regexp=path_regexp,
            )

    def _get_file_from_node(self: Self, node: dict, file_url: GitHubContentUrl) -> WorkInfo:
        return self.get_file_content_by_sha(
            file_url.owner,
            file_url.repo,
            node["sha"],
            self._get_commit_info(file_url.owner, file_url.repo, file_url.branch, file_url.path),
            file_url,
        )

    def _get_files_generator_from_node_list(
        self: Self,
        node_list: list[dict],
        dir_url: GitHubContentUrl,
        path_regexp: re.Pattern | None = None,
    ) -> Iterator[WorkInfo]:
        for node in node_list:
            current_path = f"/{node['path']}"
            full_link = (
                f"{_GH_URL}{dir_url.owner}/{dir_url.repo}/tree/{dir_url.branch}/{current_path[2:]}"
            )
            node_type = node["type"]
            if node_type == "dir":
                commit_info = self._get_commit_info(
                    dir_url.owner, dir_url.repo, dir_url.branch, current_path
                )
                yield from self.get_files_generator_from_sha_commit(
                    owner=dir_url.owner,
                    repo=dir_url.repo,
                    branch=BranchInfo(dir_url.branch, commit_info),
                    sha=node["sha"],
                    path=current_path,
                    path_regexp=path_regexp,
                )
            if (
                node_type != "file"
                or not self._is_accepted_extension(node["name"])
                or (path_regexp is not None and path_regexp.search(full_link) is None)
            ):
                continue

            commit_info = self._get_commit_info(
                dir_url.owner, dir_url.repo, dir_url.branch, current_path
            )

            yield self.get_file_content_by_sha(
                owner=dir_url.owner,
                repo=dir_url.repo,
                blob_sha=node["sha"],
                commit_info=commit_info,
                file_path=full_link,
            )

    def get_files_generator_from_url(
        self: Self, url: str, path_regexp: re.Pattern | None = None
    ) -> Iterator[WorkInfo]:
        try:
            url = GitHubContentUrl(url)
        except ValueError as error:
            self.logger.error(f"{url} is incorrect link to content of GitHub repository")
            raise error

        api_url = f"/repos/{url.owner}/{url.repo}/contents/{url.path}"
        params = {"ref": url.branch}
        response_json = self.send_get_request(api_url, params=params).json()

        if isinstance(response_json, list):
            yield from self._get_files_generator_from_node_list(response_json, url, path_regexp)
        elif isinstance(response_json, dict):
            yield self._get_file_from_node(response_json, url)
        else:
            err_msg = f"unexpected request type from {url}, expected: list or dict, got {type(response_json)}"
            self.logger.error(err_msg)
            raise TypeError(err_msg)

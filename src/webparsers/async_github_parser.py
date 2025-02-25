import base64
import logging
import re
import sys
from typing import Any, AsyncGenerator, Final

import aiohttp
import aiohttp.client_exceptions
import cachetools
import gidgethub.aiohttp
from typing_extensions import Self
from uritemplate import variable

from webparsers.types import (
    BranchInfo,
    Commit,
    GitHubContentUrl,
    GitHubRepoUrl,
    PullRequest,
    Repository,
    WorkInfo,
)

_GH_URL: Final[str] = "https://github.com/"


class AsyncGithubParser:
    """Asynchronous parser which works with GitHub REST API.

    Example:
    -------
        >>> import asyncio
        >>> import aiohttp
        >>> async def requests():
        ...     timeout = ClientTimeout(total=5)
        ...     async with aiohttp.ClientSession(timeout=timeout) as session:
        ...         gh_parser = AsyncGithubParser(session, token=<token>)
        ...         tasks = []
        ...         for _ in range(3):
        ...             tasks.append(asyncio.create_task(gh_parser.<some_func_call>))
        ...     return await asyncio.gather(*tasks)
        ...
        >>> asyncio.run(requests())
        >>> async def loop():
        ...     async for ... in gh_parser.<some_async_gen_func_call>:
        ...         ...
        ...
        >>> asynio.run(loop())

    """

    USER_INFO = "/users/{username}"
    USER_REPOS = "/users/{username}/repos{?per_page,page}"

    REPO_GET = "/repos/{username}/{repo}"

    BRANCH_GET = "/repos/{username}/{repo}/branches{/branch}"

    GIT_BLOB = "/repos/{username}/{repo}/git/blobs/{sha}"
    GIT_TREE = "/repos/{username}/{repo}/git/trees/{sha}"

    FILE_CONTENT = "/repos/{username}/{repo}/contents/{path}{?ref}"

    COMMITS_INFO = "/repos/{username}/{repo}/commits{?per_page,page,sha,path}"

    PULLS = "/repos/{username}/{repo}/pulls{/number}{?head,base,state}"
    PULL_COMMITS = "/repos/{username}/{repo}/pulls/{number}/commits"

    ORG_REPOS = "/orgs/{org}/repos{?per_page,page}"

    def __init__(
        self: Self,
        session: aiohttp.ClientSession,
        file_extensions: str | None = None,
        check_all: bool = False,
        logger: logging.Logger | None = None,
        token: str | None = None,
    ) -> None:
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.__file_extensions = file_extensions
        self.__check_all_branches = check_all
        self.__api = gidgethub.aiohttp.GitHubAPI(
            session,
            "codeplag",
            oauth_token=token,
            cache=cachetools.LRUCache(maxsize=500),
        )

    def _is_accepted_extension(self: Self, path: str) -> bool:
        if self.__file_extensions is None:
            return True

        return any(re.search(extension, path) for extension in self.__file_extensions)

    async def send_get_request(
        self: Self,
        api_url: str,
        url_vars: variable.VariableValueDict | None = None,
    ) -> Any:
        try:
            return await self.__api.getitem(api_url, url_vars)
        except aiohttp.client_exceptions.ClientConnectionError as err:
            self.logger.error("Connection error. Please check the Internet connection.")
            self.logger.debug(str(err))
            sys.exit(1)

    async def get_list_of_repos(
        self: Self, owner: str, reg_exp: re.Pattern | None = None
    ) -> list[Repository]:
        repos: list[Repository] = []
        response = await self.send_get_request(self.USER_INFO, {"username": owner})
        user_type = response.get("type", "").lower()
        # TODO: classify yourself /user/repos
        url_vars: dict[str, Any] = {"per_page": 100, "page": 1}
        if user_type == "user":
            api_url = self.USER_REPOS
            url_vars["username"] = owner
        elif user_type == "organization":
            api_url = self.ORG_REPOS
            url_vars["org"] = owner
        else:
            self.logger.error("Not supported user type %s.", user_type)
            sys.exit(1)

        while True:
            response = await self.send_get_request(api_url, url_vars)
            cnt = 0  # noqa: SIM113
            for repo in response:
                cnt += 1
                if (reg_exp is None) or reg_exp.search(repo["name"]):
                    repos.append(Repository(repo["name"], repo["html_url"]))
            if cnt < url_vars["per_page"]:
                break
            url_vars["page"] += 1

        return repos

    async def get_pulls_info(self: Self, owner: str, repo: str) -> list[PullRequest]:
        pulls: list[PullRequest] = []
        url_vars = {"username": owner, "repo": repo, "page": 1, "per_page": 100}
        while True:
            response = await self.send_get_request(self.PULLS, url_vars)

            cnt = 0  # noqa: SIM113
            for pull in response:
                cnt += 1
                pull_url_vars = {
                    "username": owner,
                    "repo": repo,
                    "number": pull["number"],
                }
                commits = await self.send_get_request(self.PULL_COMMITS, pull_url_vars)
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
            if cnt < url_vars["per_page"]:
                break

            url_vars["page"] += 1

        return pulls

    async def get_name_default_branch(self: Self, owner: str, repo: str) -> str:
        response = await self.send_get_request(self.REPO_GET, {"username": owner, "repo": repo})

        return response["default_branch"]

    async def _get_branch_last_commit_info(
        self: Self, owner: str, repo: str, branch: str = "main"
    ) -> dict:
        response = await self.send_get_request(
            self.BRANCH_GET, {"username": owner, "repo": repo, "branch": branch}
        )

        return response["commit"]

    async def get_list_repo_branches(self: Self, owner: str, repo: str) -> list[BranchInfo]:
        branches: list[BranchInfo] = []
        url_vars = {"per_page": 100, "page": 1, "username": owner, "repo": repo}
        while True:
            response = await self.send_get_request(self.BRANCH_GET, url_vars)

            cnt = 0  # noqa: SIM113
            for branch_info in response:
                cnt += 1
                branch_name = branch_info["name"]
                commit_info = await self.send_get_request(branch_info["commit"]["url"])
                branches.append(
                    BranchInfo(
                        name=branch_name,
                        last_commit=Commit(
                            commit_info["sha"],
                            commit_info["commit"]["author"]["date"],
                        ),
                    )
                )
            if cnt < url_vars["per_page"]:
                break

            url_vars["page"] += 1

        return branches

    async def get_file_content_by_sha(
        self: Self,
        owner: str,
        repo: str,
        blob_sha: str,
    ) -> str:
        response = await self.send_get_request(
            self.GIT_BLOB, {"username": owner, "repo": repo, "sha": blob_sha}
        )

        file_in_bytes = bytearray(base64.b64decode(response["content"]))
        return file_in_bytes.decode("utf-8", errors="ignore")

    async def _get_commit_info(
        self: Self, owner: str, repo: str, branch: str, path: str
    ) -> Commit:
        response: list[dict] = await self.send_get_request(
            self.COMMITS_INFO,
            url_vars={
                "page": 1,
                "per_page": 1,
                "username": owner,
                "repo": repo,
                "path": path,
                "sha": branch,
            },
        )
        commit_info: dict[str, Any] = response[0]

        return Commit(commit_info["sha"], commit_info["commit"]["author"]["date"])

    async def get_files_generator_from_sha_commit(
        self: Self,
        owner: str,
        repo: str,
        branch: BranchInfo,
        sha: str,
        path: str = "",
        path_regexp: re.Pattern | None = None,
    ) -> AsyncGenerator[WorkInfo, None]:
        response: dict[str, Any] = await self.send_get_request(
            self.GIT_TREE, {"username": owner, "repo": repo, "sha": sha}
        )
        tree: list[dict[str, Any]] = response["tree"]
        for node in tree:
            current_path = f"{path}/{node['path']}"
            full_link = f"{_GH_URL}{owner}/{repo}/blob/{branch.name}{current_path}"
            node_type = node["type"]
            if node_type == "tree":
                commit_info = await self._get_commit_info(owner, repo, branch.name, current_path)
                async for file_gen in self.get_files_generator_from_sha_commit(
                    owner=owner,
                    repo=repo,
                    branch=BranchInfo(branch.name, commit_info),
                    sha=node["sha"],
                    path=current_path,
                    path_regexp=path_regexp,
                ):
                    yield file_gen
                continue
            elif (
                node_type != "blob"
                or not self._is_accepted_extension(current_path)
                or (path_regexp is not None and path_regexp.search(full_link) is None)
            ):
                continue

            commit_info = await self._get_commit_info(owner, repo, branch.name, current_path)

            file_content = await self.get_file_content_by_sha(
                owner,
                repo,
                node["sha"],
            )

            yield WorkInfo(file_content, full_link, commit_info)

    async def get_files_generator_from_repo_url(
        self: Self, repo_url: str, path_regexp: re.Pattern | None = None
    ) -> AsyncGenerator[WorkInfo, None]:
        try:
            repo_url = GitHubRepoUrl(repo_url)
        except ValueError as error:
            self.logger.error(f"{repo_url} is incorrect link to GitHub repository")
            raise error

        if self.__check_all_branches:
            branches = await self.get_list_repo_branches(repo_url.owner, repo_url.repo)
        else:
            default_branch = await self.get_name_default_branch(repo_url.owner, repo_url.repo)
            commit_info = await self._get_branch_last_commit_info(
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
            async for file in self.get_files_generator_from_sha_commit(
                owner=repo_url.owner,
                repo=repo_url.repo,
                branch=branch,
                sha=branch.last_commit.sha,
                path_regexp=path_regexp,
            ):
                yield file

    async def get_file_from_url(self: Self, file_url: str) -> WorkInfo:
        try:
            file_url = GitHubContentUrl(file_url)
        except ValueError as error:
            self.logger.error(f"{file_url} is incorrect link to content of GitHub repository")
            raise error

        response = await self.send_get_request(
            self.FILE_CONTENT,
            {
                "username": file_url.owner,
                "repo": file_url.repo,
                "path": file_url.path,
                "ref": file_url.branch,
            },
        )

        return WorkInfo(
            await self.get_file_content_by_sha(file_url.owner, file_url.repo, response["sha"]),
            file_url,
            await self._get_commit_info(
                file_url.owner, file_url.repo, file_url.branch, file_url.path
            ),
        )

    async def get_files_generator_from_dir_url(
        self: Self, dir_url: str, path_regexp: re.Pattern | None = None
    ) -> AsyncGenerator[WorkInfo, None]:
        try:
            dir_url = GitHubContentUrl(dir_url)
        except ValueError as error:
            self.logger.error(f"{dir_url} is incorrect link to content of GitHub repository")
            raise error

        response = await self.send_get_request(
            self.FILE_CONTENT,
            {
                "username": dir_url.owner,
                "repo": dir_url.repo,
                "path": dir_url.path,
                "ref": dir_url.branch,
            },
        )

        for node in response:
            current_path = f"/{node['path']}"
            full_link = (
                f"{_GH_URL}{dir_url.owner}/{dir_url.repo}/tree/{dir_url.branch}/{current_path[2:]}"
            )
            node_type = node["type"]
            if node_type == "dir":
                commit_info = await self._get_commit_info(
                    dir_url.owner, dir_url.repo, dir_url.branch, current_path
                )
                async for work_info in self.get_files_generator_from_sha_commit(
                    owner=dir_url.owner,
                    repo=dir_url.repo,
                    branch=BranchInfo(dir_url.branch, commit_info),
                    sha=node["sha"],
                    path=current_path,
                    path_regexp=path_regexp,
                ):
                    yield work_info
            if (
                node_type != "file"
                or not self._is_accepted_extension(node["name"])
                or (path_regexp is not None and path_regexp.search(full_link) is None)
            ):
                continue

            commit_info = await self._get_commit_info(
                dir_url.owner, dir_url.repo, dir_url.branch, current_path
            )

            file_content = await self.get_file_content_by_sha(
                owner=dir_url.owner,
                repo=dir_url.repo,
                blob_sha=node["sha"],
            )

            yield WorkInfo(file_content, full_link, commit_info)

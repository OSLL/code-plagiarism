import base64
import logging
import re
import sys
from typing import Any, Dict, Final, Iterator, List, Optional

import requests

from webparsers.types import (
    Branch,
    Commit,
    Extensions,
    GitHubContentUrl,
    GitHubRepoUrl,
    PullRequest,
    Repository,
    WorkInfo,
)

_API_URL: Final[str] = 'https://api.github.com'
_GH_URL: Final[str] = 'https://github.com/'


class GitHubParser:
    def __init__(
        self,
        file_extensions: Optional[Extensions] = None,
        check_all: bool = False,
        access_token: str = '',
        logger: Optional[logging.Logger] = None,
        session: Optional[requests.Session] = None,
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
            'accept': 'application/vnd.github.v3+json'
        }
        if access_token != '':
            self.__headers.update({'Authorization': 'token ' + access_token})

    def _is_accepted_extension(self, path: str) -> bool:
        if self.__file_extensions is None:
            return True

        return any(
            re.search(extension, path) for extension in self.__file_extensions
        )

    def send_get_request(
        self,
        api_url: str,
        params: Optional[dict] = None,
        address: str = _API_URL
    ) -> requests.Response:
        if params is None:
            params = {}

        if address and len(api_url) and api_url[0] != "/":
            address += "/"

        url = address + api_url

        # Check Ethernet connection and requests limit
        try:
            if self.__session is not None:
                response = self.__session.get(
                    url,
                    headers=self.__headers,
                    params=params
                )
            else:
                response = requests.get(url, headers=self.__headers, params=params)
        except requests.exceptions.ConnectionError as err:
            self.logger.error(
                "Connection error. Please check the Internet connection."
            )
            self.logger.debug(str(err))
            sys.exit(1)

        if response.status_code in [400, 403, 404]:
            self.logger.error(
                f"GitHub error: '{response.json()['message']}' for url '{url}'."
            )
            sys.exit(1)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error("The access token is bad.")
            self.logger.debug(str(err))
            sys.exit(1)

        return response

    def get_list_of_repos(
        self,
        owner: str,
        reg_exp: Optional[re.Pattern] = None
    ) -> List[Repository]:
        '''
            Function returns dict in which keys characterize repository names
            and values characterize repositories links
        '''

        repos: List[Repository] = []
        response_json = self.send_get_request(f'/users/{owner}').json()
        user_type = response_json.get('type', '').lower()
        # TODO: classify yourself /user/repos
        if user_type == 'user':
            api_url = f'/users/{owner}/repos'
        elif user_type == 'organization':
            api_url = f'/orgs/{owner}/repos'
        else:
            self.logger.error("Not supported user type %s.", user_type)
            sys.exit(1)

        params = {'per_page': 100, 'page': 1}
        while True:
            response_json = self.send_get_request(
                api_url,
                params=params
            ).json()

            cnt = 0  # noqa: SIM113
            for repo in response_json:
                cnt += 1
                if (
                    (reg_exp is None) or
                    re.search(reg_exp, repo['name']) is not None
                ):
                    repos.append(
                        Repository(
                            name=repo['name'],
                            html_url=repo['html_url']
                        )
                    )
            if cnt < params['per_page']:
                break

            params['page'] += 1

        return repos

    def get_pulls_info(
        self,
        owner: str,
        repo: str
    ) -> List[PullRequest]:
        pulls: List[PullRequest] = []
        api_url = f'/repos/{owner}/{repo}/pulls'
        params: Dict[str, int] = {'per_page': 100, 'page': 1}
        while True:
            response_json = self.send_get_request(
                api_url,
                params=params
            ).json()

            cnt = 0  # noqa: SIM113
            for pull in response_json:
                cnt += 1
                commits = self.send_get_request(
                    pull['commits_url'],
                    address=''
                ).json()
                pull_owner, owner_branch = pull['head']['label'].split(
                    ':',
                    maxsplit=1
                )
                pulls.append(
                    PullRequest(
                        number=pull['number'],
                        last_commit_sha=commits[0]['sha'],
                        owner=pull_owner,
                        branch=owner_branch,
                        state=pull['state'],
                        draft=pull['draft']
                    )
                )
            if cnt < params['per_page']:
                break

            params['page'] += 1

        return pulls

    def get_name_default_branch(self, owner: str, repo: str) -> str:
        api_url = f'/repos/{owner}/{repo}'
        response: Dict[str, Any] = self.send_get_request(api_url).json()

        return response['default_branch']

    def _get_branch_last_commit_info(
        self,
        owner: str,
        repo: str,
        branch: str = 'main'
    ) -> dict:
        api_url = f'/repos/{owner}/{repo}/branches/{branch}'
        response: Dict[str, Any] = self.send_get_request(api_url).json()

        return response['commit']

    def get_file_content_by_sha(
        self,
        owner: str,
        repo: str,
        blob_sha: str,
        commit_info: Commit,
        file_path: str
    ) -> WorkInfo:
        api_url = f'/repos/{owner}/{repo}/git/blobs/{blob_sha}'
        response: Dict[str, Any] = self.send_get_request(api_url).json()

        file_in_bytes: bytearray = bytearray(
            base64.b64decode(response['content'])
        )
        code = file_in_bytes.decode('utf-8', errors='ignore')

        return WorkInfo(code, file_path, commit_info)

    def _get_commit_info(
        self,
        owner: str,
        repo: str,
        branch: str,
        path: str
    ) -> Commit:
        commit_info: Dict[str, Any] = self.send_get_request(
            api_url=f'/repos/{owner}/{repo}/commits',
            params={
                'path': path,
                'page': 1,
                'per_page': 1,
                'sha': branch
            }
        ).json()[0]

        return Commit(
            commit_info['sha'],
            commit_info['commit']['author']['date']
        )

    def get_files_generator_from_sha_commit(
        self,
        owner: str,
        repo: str,
        branch: Branch,
        sha: str,
        path: str = '',
        path_regexp: Optional[re.Pattern] = None
    ) -> Iterator[WorkInfo]:
        api_url = f'/repos/{owner}/{repo}/git/trees/{sha}'
        jresponse: Dict[str, Any] = self.send_get_request(api_url).json()
        tree: list[Dict[str, Any]] = jresponse['tree']
        for node in tree:
            current_path = f"{path}/{node['path']}"
            full_link = (
                f"{_GH_URL}{owner}/{repo}/blob/{branch.name}{current_path}"
            )
            node_type = node["type"]
            if node_type == "tree":
                commit_info = self._get_commit_info(
                    owner,
                    repo,
                    branch.name,
                    current_path
                )
                yield from self.get_files_generator_from_sha_commit(
                    owner=owner,
                    repo=repo,
                    branch=Branch(branch.name, commit_info),
                    sha=node['sha'],
                    path=current_path,
                    path_regexp=path_regexp
                )
                continue
            elif (
                node_type != "blob"
                or not self._is_accepted_extension(current_path)
                or (path_regexp is not None and path_regexp.search(full_link) is None)
            ):
                continue

            commit_info = self._get_commit_info(
                owner,
                repo,
                branch.name,
                current_path
            )

            yield self.get_file_content_by_sha(
                owner,
                repo,
                node['sha'],
                commit_info,
                full_link
            )

    def get_list_repo_branches(
        self,
        owner: str,
        repo: str
    ) -> List[Branch]:
        branches: List[Branch] = []
        api_url: str = f'/repos/{owner}/{repo}/branches'
        params: Dict[str, int] = {"per_page": 100, "page": 1}
        while True:
            response_json = self.send_get_request(
                api_url,
                params=params
            ).json()

            cnt = 0  # noqa: SIM113
            for node in response_json:
                cnt += 1
                commit_info = node['commit']
                branches.append(
                    Branch(
                        name=node["name"],
                        last_commit=Commit(
                            commit_info['sha'],
                            commit_info['commit']['author']['date'],
                        )
                    )
                )
            if cnt < params['per_page']:
                break

            params['page'] += 1

        return branches

    def get_files_generator_from_repo_url(
        self,
        repo_url: str,
        path_regexp: Optional[re.Pattern] = None
    ) -> Iterator[WorkInfo]:
        try:
            repo_url = GitHubRepoUrl(repo_url)
        except ValueError as error:
            self.logger.error(
                f'{repo_url} is incorrect link to GitHub repository'
            )
            raise error

        if self.__check_all_branches:
            branches = self.get_list_repo_branches(
                repo_url.owner, repo_url.repo
            )
        else:
            default_branch = self.get_name_default_branch(
                repo_url.owner, repo_url.repo
            )
            commit_info = self._get_branch_last_commit_info(
                repo_url.owner,
                repo_url.repo,
                default_branch
            )
            branches = [
                Branch(
                    name=default_branch,
                    last_commit=Commit(
                        commit_info['sha'],
                        commit_info['commit']['author']['date'],
                    )
                )
            ]

        for branch in branches:
            yield from self.get_files_generator_from_sha_commit(
                owner=repo_url.owner,
                repo=repo_url.repo,
                branch=branch,
                sha=branch.last_commit.sha,
                path_regexp=path_regexp
            )

    def get_file_from_url(self, file_url: str) -> WorkInfo:
        try:
            file_url = GitHubContentUrl(file_url)
        except ValueError as error:
            self.logger.error(
                f'{file_url} is incorrect link to content of GitHub repository'
            )
            raise error

        api_url = (
            f'/repos/{file_url.owner}/{file_url.repo}/contents/{file_url.path}'
        )
        params = {
            'ref': file_url.branch
        }
        response_json = self.send_get_request(api_url, params=params).json()

        return self.get_file_content_by_sha(
            file_url.owner,
            file_url.repo,
            response_json['sha'],
            self._get_commit_info(
                file_url.owner,
                file_url.repo,
                file_url.branch,
                file_url.path
            ),
            file_url
        )

    def get_files_generator_from_dir_url(
        self,
        dir_url: str,
        path_regexp: Optional[re.Pattern] = None
    ) -> Iterator[WorkInfo]:
        try:
            dir_url = GitHubContentUrl(dir_url)
        except ValueError as error:
            self.logger.error(
                f'{dir_url} is incorrect link to content of GitHub repository'
            )
            raise error

        api_url = (
            f'/repos/{dir_url.owner}/{dir_url.repo}/contents/{dir_url.path}'
        )
        params = {'ref': dir_url.branch}
        response_json = self.send_get_request(api_url, params=params).json()

        for node in response_json:
            current_path = f'/{node["path"]}'
            full_link = (
                f'{_GH_URL}{dir_url.owner}/{dir_url.repo}'
                f'/tree/{dir_url.branch}/{current_path[2:]}'
            )
            node_type = node["type"]
            if node_type == "dir":
                commit_info = self._get_commit_info(
                    dir_url.owner,
                    dir_url.repo,
                    dir_url.branch,
                    current_path
                )
                yield from self.get_files_generator_from_sha_commit(
                    owner=dir_url.owner,
                    repo=dir_url.repo,
                    branch=Branch(dir_url.branch, commit_info),
                    sha=node['sha'],
                    path=current_path,
                    path_regexp=path_regexp
                )
            if (
                node_type != "file"
                or not self._is_accepted_extension(node["name"])
                or (path_regexp is not None and path_regexp.search(full_link) is None)
            ):
                continue

            commit_info = self._get_commit_info(
                dir_url.owner,
                dir_url.repo,
                dir_url.branch,
                current_path
            )

            yield self.get_file_content_by_sha(
                owner=dir_url.owner,
                repo=dir_url.repo,
                blob_sha=node['sha'],
                commit_info=commit_info,
                file_path=full_link,
            )

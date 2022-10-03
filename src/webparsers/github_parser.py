import base64
import logging
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

import requests

from webparsers.types import (Branch, Extensions, GitHubContentUrl,
                              GitHubRepoUrl, PullRequest, Repository)


class GitHubParser:
    def __init__(self, file_extensions: Optional[Extensions] = None,
                 check_all: bool = False, access_token: str = '',
                 logger: Optional[logging.Logger] = None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.__file_extensions = file_extensions
        self.__access_token = access_token
        self.__check_all_branches = check_all

    def decode_file_content(self, file_in_bytes: bytearray) -> str:
        attempt = 1
        code = None
        while code is None:
            try:
                code = file_in_bytes.decode('utf-8')
            except UnicodeDecodeError as error:
                attempt += 1
                if attempt % 25 == 0:
                    self.logger.debug(
                        f"Trying to decode content, attempt - {attempt}"
                    )
                file_in_bytes[error.args[2]] = 32

        return code

    def is_accepted_extension(self, path: str) -> bool:
        if self.__file_extensions is None:
            return True

        return any(
            re.search(extension, path) for extension in self.__file_extensions
        )

    def send_get_request(self,
                         api_url: str,
                         params: Optional[dict] = None,
                         address: str = 'https://api.github.com') -> requests.Response:
        if params is None:
            params = {}

        if address and len(api_url) and api_url[0] != "/":
            address += "/"

        headers = {
            # Recommended
            'accept': 'application/vnd.github.v3+json'
        }
        if self.__access_token != '':
            headers.update({
                'Authorization': 'token ' + self.__access_token,
            })

        # Check Ethernet connection and requests limit
        try:
            response = requests.get(address + api_url, headers=headers,
                                    params=params)
        except requests.exceptions.ConnectionError as err:
            self.logger.error(
                "Connection error. Please check the Internet connection."
            )
            self.logger.debug(str(err))
            sys.exit(1)

        if response.status_code == 403:
            if 'message' in response.json():
                self.logger.error(
                    "GitHub " + response.json()['message']
                )
                sys.exit(1)

            raise KeyError

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error("The access token is bad")
            self.logger.debug(str(err))
            sys.exit(1)

        return response

    def get_list_of_repos(self,
                          owner: str,
                          reg_exp: Optional[str] = None) -> List[Repository]:
        '''
            Function returns dict in which keys characterize repository names
            and values characterize repositories links
        '''
        repos: List[Repository] = []
        page: int = 1
        api_url: str = f'/users/{owner}/repos'
        while True:
            params: Dict[str, int] = {
                'per_page': 100,
                'page': page
            }
            response_json = self.send_get_request(
                api_url,
                params=params
            ).json()

            if len(response_json) == 0:
                break

            for repo in response_json:
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

            page += 1

        return repos

    def get_pulls_info(self,
                       owner: str,
                       repo: str) -> List[PullRequest]:
        pulls: List[PullRequest] = []
        page: int = 1
        api_url: str = f'/repos/{owner}/{repo}/pulls'
        while True:
            params: Dict[str, int] = {
                'per_page': 100,
                'page': page
            }
            response_json = self.send_get_request(
                api_url,
                params=params
            ).json()

            if len(response_json) == 0:
                break

            for pull in response_json:
                commits = self.send_get_request(
                    pull['commits_url'],
                    address=''
                ).json()
                pull_owner, owner_branch = pull['head']['label'].split(':')
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

            page += 1

        return pulls

    def get_name_default_branch(self, owner: str, repo: str) -> str:
        api_url: str = f'/repos/{owner}/{repo}'
        response: Dict[str, Any] = self.send_get_request(api_url).json()

        return response['default_branch']

    def get_sha_last_branch_commit(self,
                                   owner: str,
                                   repo: str,
                                   branch: str = 'main') -> str:
        api_url: str = f'/repos/{owner}/{repo}/branches/{branch}'
        response: Dict[str, Any] = self.send_get_request(api_url).json()

        return response['commit']['sha']

    def get_file_content_from_sha(self,
                                  owner: str,
                                  repo: str,
                                  sha: str,
                                  file_path: str) -> Tuple[str, str]:
        api_url: str = f'/repos/{owner}/{repo}/git/blobs/{sha}'
        response: Dict[str, Any] = self.send_get_request(api_url).json()

        file_in_bytes: bytearray = bytearray(
            base64.b64decode(response['content'])
        )
        code: str = self.decode_file_content(file_in_bytes)

        return code, file_path

    def get_files_generator_from_sha_commit(self,
                                            owner: str,
                                            repo: str,
                                            branch: str,
                                            sha: str,
                                            path: str = ''):
        api_url: str = f'/repos/{owner}/{repo}/git/trees/{sha}'
        response: Dict[str, Any] = self.send_get_request(api_url).json()
        tree = response['tree']
        for node in tree:
            current_path = f"{path}/{node['path']}"
            if node["type"] == "tree":
                yield from self.get_files_generator_from_sha_commit(
                    owner,
                    repo,
                    branch,
                    node['sha'],
                    current_path
                )

            if node["type"] == "blob" and self.is_accepted_extension(
                current_path
            ):
                file_link = (
                    "https://github.com/"
                    f"{owner}/{repo}/blob/{branch}{current_path}"
                )
                yield self.get_file_content_from_sha(owner, repo,
                                                     node["sha"],
                                                     file_link)

    def get_list_repo_branches(self,
                               owner: str,
                               repo: str) -> List[Branch]:
        branches: List[Branch] = []
        page: int = 1
        api_url: str = f'/repos/{owner}/{repo}/branches'
        while True:
            params: Dict[str, int] = {
                "per_page": 100,
                "page": page
            }
            response_json = self.send_get_request(
                api_url,
                params=params
            ).json()

            if len(response_json) == 0:
                break

            for node in response_json:
                branches.append(
                    Branch(
                        name=node["name"],
                        last_commit_sha=node['commit']['sha']
                    )
                )

            page += 1

        return branches

    def get_files_generator_from_repo_url(self, repo_url: str):
        try:
            repo_url = GitHubRepoUrl(repo_url)
        except ValueError as error:
            self.logger.error(
                f'{repo_url} is incorrect link to GitHub repository'
            )
            raise error

        default_branch = self.get_name_default_branch(
            repo_url.owner, repo_url.repo
        )
        if self.__check_all_branches:
            branches = self.get_list_repo_branches(
                repo_url.owner, repo_url.repo
            )
        else:
            branches = [
                Branch(
                    name=default_branch,
                    last_commit_sha=self.get_sha_last_branch_commit(
                        repo_url.owner,
                        repo_url.repo,
                        default_branch
                    )
                )
            ]

        for branch in branches:
            yield from self.get_files_generator_from_sha_commit(
                repo_url.owner,
                repo_url.repo,
                branch.name,
                branch.last_commit_sha
            )

    def get_file_from_url(self, file_url: str):
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

        return self.get_file_content_from_sha(
            file_url.owner,
            file_url.repo,
            response_json['sha'],
            file_url
        )

    def get_files_generator_from_dir_url(self, dir_url: str):
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
        params = {
            'ref': dir_url.branch
        }
        response_json = self.send_get_request(api_url, params=params).json()

        for node in response_json:
            current_path = "./" + node["path"]
            if node["type"] == "dir":
                yield from self.get_files_generator_from_sha_commit(
                    dir_url.owner,
                    dir_url.repo,
                    dir_url.branch,
                    node['sha'],
                    current_path
                )
            if node["type"] == "file" and self.is_accepted_extension(
                node["name"]
            ):
                file_link = (
                    'https://github.com/'
                    f'{dir_url.owner}/{dir_url.repo}'
                    f'/tree/{dir_url.branch}/{current_path[2:]}'
                )
                yield self.get_file_content_from_sha(
                    dir_url.owner,
                    dir_url.repo,
                    node["sha"],
                    file_link
                )

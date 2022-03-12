import requests
import base64
import re

from webparsers.logger import get_logger
from webparsers.consts import LOG_PATH


class GitHubParser:
    logger = get_logger(__name__, LOG_PATH)

    def __init__(self, file_extensions=[r'.py$', r'.cpp$', r'.c$', r'.h$'],
                 check_policy=0, access_token=''):
        self.__access_token = access_token
        self.__check_all_branches = check_policy
        self.__file_extensions = file_extensions

    @staticmethod
    def check_github_url(github_url):
        url_parts = github_url.rstrip('/').split('/')
        if len(url_parts) < 3:
            GitHubParser.logger.error(f'{github_url} is incorrect link to GitHub')
            raise ValueError('Incorrect link to GitHub')
        if url_parts[0] != 'https:' and url_parts[0] != 'http:':
            GitHubParser.logger.error(f'{github_url} is incorrect link to GitHub')
            raise ValueError('Incorrect link to GitHub')
        elif url_parts[1] != '':
            GitHubParser.logger.error(f'{github_url} is incorrect link to GitHub')
            raise ValueError('Incorrect link to GitHub')
        elif url_parts[2] != 'github.com':
            GitHubParser.logger.error(f'{github_url} is incorrect link to GitHub')
            raise ValueError('Incorrect link to GitHub')

        return url_parts

    @staticmethod
    def parse_repo_url(repo_url):
        url_parts = GitHubParser.check_github_url(repo_url)

        if len(url_parts) != 5:
            GitHubParser.logger.error(f'{repo_url} is incorrect link to GitHub repository')
            raise ValueError('Incorrect link to GitHub repository')

        return url_parts[3], url_parts[4]

    @staticmethod
    def parse_content_url(content_url):
        # If the branch name contains '/' like 'dev/example' then behave
        # of this funciton won't be similar to what expect
        url_parts = GitHubParser.check_github_url(content_url)

        if len(url_parts) <= 7:
            GitHubParser.logger.error(f'{content_url} is incorrect link to content of GitHub repository')
            raise ValueError('Incorrect link to content of GitHub repository')

        return (url_parts[3], url_parts[4],
                url_parts[6], '/'.join(url_parts[7:]))

    @staticmethod
    def decode_file_content(file_in_bytes):
        attempt = 1
        code = None
        while code is None:
            try:
                code = file_in_bytes.decode('utf-8')
            except UnicodeDecodeError as error:
                attempt += 1
                if attempt % 25 == 0:
                    GitHubParser.logger.debug(f"Trying to decode content, attempt - {attempt}")
                file_in_bytes[error.args[2]] = 32

        return code

    def is_accepted_extension(self, path):
        for extension in self.__file_extensions:
            if re.search(extension, path):
                return True

        return False

    def send_get_request(self, api_url, params={}):
        address = 'https://api.github.com'
        if api_url[0] != "/":
            address += "/"

        headers = {
            # Recommended
            'accept': 'application/vnd.github.v3+json'
        }
        if self.__access_token != '':
            headers.update({
                'Authorization': 'token ' + self.__access_token,
            })

        # TODO: Check Ethernet connection and requests limit
        # requests.exceptions.ConnectionError
        try:
            response = requests.get(address + api_url, headers=headers,
                                    params=params)
        except requests.exceptions.ConnectionError as err:
            GitHubParser.logger.error("Connection error. Please check the Internet connection")
            GitHubParser.logger.debug(str(err))
            exit(1)

        if response.status_code == 403:
            if 'message' in response.json():
                GitHubParser.logger.error("GitHub " + response.json()['message'])
                exit(1)

            raise KeyError

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            GitHubParser.logger.error("The access token is bad")
            GitHubParser.logger.debug(str(err))
            exit(1)

        return response

    def get_list_of_repos(self, owner, per_page=100, reg_exp=None):
        '''
            Function returns dict in which keys characterize repository names
            and values characterize repositories links
        '''
        repos = {}
        page = 1
        while True:
            api_url = '/users/{}/repos'.format(owner)
            params = {
                'per_page': per_page,
                'page': page
            }
            response_json = self.send_get_request(
                                api_url,
                                params=params
                            ).json()

            if len(response_json) == 0:
                break

            for repo in response_json:
                if reg_exp is None:
                    repos[repo['name']] = repo['html_url']
                elif re.search(reg_exp, repo['name']) is not None:
                    repos[repo['name']] = repo['html_url']

            page += 1

        return repos

    def get_name_default_branch(self, owner, repo):
        api_url = '/repos/{}/{}'.format(owner, repo)
        response_json = self.send_get_request(api_url).json()

        return response_json['default_branch']

    def get_sha_last_branch_commit(self, owner, repo, branch='main'):
        api_url = '/repos/{}/{}/branches/{}'.format(owner, repo, branch)
        response_json = self.send_get_request(api_url).json()

        return response_json['commit']['sha']

    def get_file_content_from_sha(self, owner, repo, sha, file_path):
        api_url = '/repos/{}/{}/git/blobs/{}'.format(owner, repo, sha)
        response_json = self.send_get_request(api_url).json()

        file_in_bytes = bytearray(base64.b64decode(response_json['content']))
        code = self.decode_file_content(file_in_bytes)

        return code, file_path

    def get_files_generator_from_sha_commit(self, owner, repo, branch,
                                            sha, path=''):
        api_url = '/repos/{}/{}/git/trees/{}'.format(owner, repo, sha)
        response_json = self.send_get_request(api_url).json()
        tree = response_json['tree']
        for node in tree:
            current_path = "{}/{}".format(path, node["path"])
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
                file_link = "https://github.com/{}/{}/blob/{}{}".format(
                                owner,
                                repo,
                                branch,
                                current_path
                            )
                yield self.get_file_content_from_sha(owner, repo,
                                                     node["sha"],
                                                     file_link)

    def get_list_repo_branches(self, owner, repo, per_page=100):
        branches = {}
        page = 1
        while True:
            api_url = '/repos/{}/{}/branches'.format(owner, repo)
            params = {
                "per_page": per_page,
                "page": page
            }
            response_json = self.send_get_request(api_url,
                                                  params=params).json()

            if len(response_json) == 0:
                break

            for node in response_json:
                branches[node["name"]] = node['commit']['sha']

            page += 1

        return branches

    def get_files_generator_from_repo_url(self, repo_url):
        owner, repo = self.parse_repo_url(repo_url)

        default_branch = self.get_name_default_branch(owner, repo)
        if self.__check_all_branches:
            branches = self.get_list_repo_branches(owner, repo)
        else:
            branches = {default_branch: self.get_sha_last_branch_commit(
                                            owner,
                                            repo,
                                            default_branch
                                        )
                        }

        for branch in branches.items():
            yield from self.get_files_generator_from_sha_commit(
                           owner,
                           repo,
                           branch[0],
                           branch[1]
                        )

    def get_file_from_url(self, file_url):
        owner, repo, branch, path = self.parse_content_url(file_url)
        api_url = '/repos/{}/{}/contents/{}'.format(owner, repo, path)
        params = {
            'ref': branch
        }
        response_json = self.send_get_request(api_url, params=params).json()

        return self.get_file_content_from_sha(
                    owner,
                    repo,
                    response_json['sha'],
                    file_url
                )

    def get_files_generator_from_dir_url(self, dir_url):
        owner, repo, branch, path = GitHubParser.parse_content_url(dir_url)
        api_url = '/repos/{}/{}/contents/{}'.format(owner, repo, path)
        params = {
            'ref': branch
        }
        response_json = self.send_get_request(api_url, params=params).json()

        for node in response_json:
            current_path = "./" + node["path"]
            if node["type"] == "dir":
                yield from self.get_files_generator_from_sha_commit(
                               owner,
                               repo,
                               branch,
                               node['sha'],
                               current_path
                           )
            if node["type"] == "file" and self.is_accepted_extension(
                                              node["name"]
                                          ):
                file_link = 'https://github.com/{}/{}/tree/{}/{}'.format(
                                owner,
                                repo,
                                branch,
                                current_path[2:]
                             )
                yield self.get_file_content_from_sha(
                          owner,
                          repo,
                          node["sha"],
                          file_link
                      )

import requests
import base64
import re

from src.github_helper.const import HEADERS, OWNER
from termcolor import colored


def get_list_of_repos():
    '''
        Function return list of repos which belongs to user
        defined in const.py in field OWNER and list of urls to this repos
        Also required to define ACCESS_TOKEN
    '''
    repos = []
    repos_url = []

    page_num = 1
    url = f"https://api.github.com/users/{OWNER}/repos?page={page_num}"
    page = requests.get(url, headers=HEADERS).json()
    while page != []:
        if type(page) == dict:
            if 'message' in page.keys():
                print()
                print(colored(page['message']), 'red')
                print()
                exit()

        for repo in page:
            repos.append(repo['name'])
            repos_url.append(repo['url'])

        page_num += 1
        url = f"https://api.github.com/users/{OWNER}/repos?page={page_num}"
        page = requests.get(url, headers=HEADERS).json()

    return repos, repos_url


def get_python_files_links(start_link):
    '''
        Function return list of urls to all python files in repository

        start_link: str - link to repository contents in api.github.com
    '''
    url_links = []
    req = requests.get(start_link, headers=HEADERS)
    req = req.json()
    if type(req) == dict:
        if 'message' in req.keys():
            print()
            print(start_link)
            print(colored(req['message'], 'red'))
            print()
            exit()
    elif type(req) == list:
        for el in req:
            if (el['size'] != 0 and el['name'].endswith('.py') and
               len(el['name']) > 3):
                url_links.append(el['url'])
                continue
            if 'size' in el.keys() and el['size'] == 0:
                url_links.extend(get_python_files_links(el['url']))

    return url_links


def get_code(link):
    '''
        Function return code of python file which located at the link

        link: str - link to python file in api.github.com
    '''
    req = requests.get(link, headers=HEADERS)
    req = req.json()
    if type(req) == dict:
        if 'message' in req.keys():
            print()
            print(link)
            print(colored(req['message'], 'red'))
            print()
            exit()

    file_bytes = base64.b64decode(req['content'])
    file_str = file_bytes.decode('utf-8')

    return file_str


def select_repos(repos, repos_url, reg_exp):
    upprooved_repos = []
    upprooved_repos_links = []
    for repo, repo_url in zip(repos, repos_url):
        if(re.search(reg_exp, repo) is not None):
            upprooved_repos.append(repo)
            upprooved_repos_links.append(repo_url)

    return upprooved_repos, upprooved_repos_links

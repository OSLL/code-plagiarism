import requests
import numpy as np
import base64
from src.github_helper.const import HEADERS, OWNER


def get_list_of_repos():
    repos = []
    repos_url = []

    page_num = 1
    url = f"https://api.github.com/users/{OWNER}/repos?page={page_num}"
    page = requests.get(url, headers=HEADERS).json()
    while page != []:
        if type(page) == dict:
            if 'message' in page.keys():
                print(page['message'])
                exit()

        for repo in page:
            repos.append(repo['name'])
            repos_url.append(repo['url'])

        page_num += 1
        url = f"https://api.github.com/users/{OWNER}/repos?page={page_num}"
        page = requests.get(url, headers=HEADERS).json()

    return repos, repos_url


def get_python_files_links(start_link):
    url_links = []
    req = requests.get(start_link, headers=HEADERS)
    req = req.json()
    if type(req) == dict:
        if 'message' in req.keys():
            print(req['message'])
            exit()
    elif type(req) == list:
        for el in req:
            if el['size'] != 0 and el['name'].endswith('.py') and len(el['name']) > 3:
                url_links.append(el['url'])
                continue
            url_links.extend(get_python_files_links(el['url']))
    elif 'size' in req.keys() and req['size'] == 0:
        url_links.extend(get_python_files_links(req['url']))

    return url_links


def get_code(link):
    req = requests.get(link, headers=HEADERS)
    req = req.json()
    if type(req) == dict:
        if 'message' in req.keys():
            print(req['message'])
            exit()

    file_bytes = base64.b64decode(req['content'])
    file_str = file_bytes.decode('utf-8')

    return file_str
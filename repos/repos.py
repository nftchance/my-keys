import os
import requests

# Get environment variable for the GitHub API key
# This is a personal access token

GITHUB_API_KEY = os.environ.get('GITHUB_API_KEY')


class RepoManager:
    TAGS = [
        'solidity',
        'hardhat',
    ]

    LANGUAGES = [
        'solidity',
        'javascript',
    ]

    FILE_NAMES = [
        'hardhat.config.js',
        'truffle-config.js',
        'truffle.js',
        'hardhat.config.ts',
        'truffle-config.ts',
        'truffle.ts',
    ]

    # Regex to find any string that is 0x followed by 40 hex characters
    HEX_KEY_REGEX = r'0x[0-9a-fA-F]{40}'

    def __init__(self):
        self.repos = []
        self.repo_count = 0

    def start(self):
        print("RepoManager started")

        # self.get_repos_by_tag('hardhat')
        # self.get_repos_by_language('solidity')
        # self.get_files("grumbach/ft_ping")
        # self.get_file("grumbach/ft_ping", "srcs/gen_ip_header.c")

    def _get_repo(self, url):
        r = requests.get(url)
        res = r.json()

        for item in res["items"]:
            print(item["default_branch"])
            print(item["full_name"])

        return res

    def get_repos_by_tag(self, tag):
        url = f"https://api.github.com/search/repositories?q=topic:{tag}&sort=-stars&order=desc"

        print('Getting repos tagged as: ' + tag)

        return self._get_repo(url)

    def get_repos_by_language(self, language):
        url = f"https://api.github.com/search/repositories?q=language:{language}&sort=-stars&order=desc"

        print('Getting repos tagged as: ' + language)

        return self._get_repo(url)

    def get_files(self, full_name):
        url = f"https://api.github.com/repos/{full_name}/git/trees/master?recursive=1"

        print('Getting content of repo: http://github.com/' + full_name)

        r = requests.get(url)
        res = r.json()

        for file in res["tree"]:
            print(file["path"])

    # get the raw file contents from github content
    def get_file(self, full_name, branch, filename):
        url = f"https://raw.githubusercontent.com/repos/{full_name}/{branch}/{filename}"

        print('Getting content of file: ' + filename)

        r = requests.get(url)

        return r.text

    def get_contacts(self, full_name):
        url = f"https://api.github.com/repos/{full_name}/stargazers"

        print('Getting contacts of repo: ' + full_name)

        r = requests.get(url)
        res = r.json()

        for contact in res:
            print(contact["login"])
            print(contact["html_url"])
            print(contact["organizations_url"])
            print(contact["site_admin"])

import os
import re
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
        self.repos = {}
        self.repo_count = 0

    def start(self):
        print("RepoManager started")

    def _get_repo(self, full_name):
        if full_name in self.repos: return self.repos[full_name]

        url = f"https://api.github.com/repos/{full_name}"

        r = requests.get(url)
        res = r.json()

        return res

    # DRY component used to get the content of a repository
    def _get_repos(self, url):
        r = requests.get(url)
        res = r.json()

        for item in res["items"]:
            self.repos[item["full_name"]] = item

        return res["items"]

    # Search all repos by tag
    def get_repos_by_tag(self, tag):
        url = f"https://api.github.com/search/repositories?q=topic:{tag}&sort=-stars&order=desc"

        return self._get_repos(url)

    # Search all repos by language
    def get_repos_by_language(self, language):
        url = f"https://api.github.com/search/repositories?q=language:{language}&sort=-stars&order=desc"

        return self._get_repos(url)

    # Get all the files in the repository
    def get_files(self, full_name, branch=None):
        if not branch:
            branch = self._get_repo(full_name)["default_branch"]

        url = f"https://api.github.com/repos/{full_name}/git/trees/{branch}?recursive=1"

        r = requests.get(url)
        res = r.json()

        return res["tree"]

    # Filter down to only the files that we are looking for
    def get_filtered_files(self, files=None, full_name=None):
        if not files:
            if not full_name:
                raise Exception("Must provide either files or full_name")

            files = self.get_files(full_name)

        filtered_files = []

        for file in files:
            if file["type"] == "blob":
                if file["path"] in self.FILE_NAMES:
                    filtered_files.append(file)

        return filtered_files

    # get the raw file contents from github content
    def get_file(self, full_name, branch, filename):
        url = f"https://raw.githubusercontent.com/{full_name}/{branch}/{filename}"

        r = requests.get(url)

        # get raw file contents
        return r.text

    def get_keys_in_file(self, file_content):
        # find all keys in the file
        keys = re.findall(self.HEX_KEY_REGEX, file_content)

        return keys

    def get_contacts(self, full_name):
        url = f"https://api.github.com/repos/{full_name}/stargazers"

        r = requests.get(url)
        res = r.json()

        return res

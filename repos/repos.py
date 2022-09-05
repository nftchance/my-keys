import os
import re
import requests

from repos.models import Repo, RepoFile, RepoKey

# Get environment variable for the GitHub API key
# This is a personal access token
GITHUB_API_KEY = os.environ.get('GITHUB_API_KEY')

# TODO: Handle pagination.

class RepoManager:
    TAGS = [
        'solidity',
        'hardhat',
    ]

    LANGUAGES = [
        'solidity',
        'javascript',
    ]

    # FILE_NAMES = [
    #     'hardhat.config.js',
    #     'truffle-config.js',
    #     'truffle.js',
    #     'hardhat.config.ts',
    #     'truffle-config.ts',
    #     'truffle.ts',
    # ]

    # Regex to find any string that is 0x followed by 40 hex characters
    HEX_KEY_REGEX = r'0x[0-9a-fA-F]{40}'

    def __init__(self):
        self.repo_calls = {}
        self.repos = {}

    def start(self):
        print("RepoManager started")

        self.sync_repos(self.get_repos_by_tag("hardhat"))

        # for tag in self.TAGS:
        #     self.get_repos_by_tag(tag)

        # for language in self.LANGUAGES:
        #     self.get_repos_by_language(language)


    def _sync_repo(self, repo):
        repo, created = Repo.objects.get_or_create(
            full_name=repo["full_name"],
            default_branch=repo["default_branch"]
        )

        files = self.get_files(repo.full_name, repo.default_branch)        
        if repo.last_commit != files[0]["sha"]:
            print("Checking files for: ", repo.full_name, repo.default_branch)

            for file in files:
                if file["type"] == "blob":
                    # if file["path"] in self.FILE_NAMES:
                    file_content = self.get_file(repo.full_name, repo.default_branch, file["path"])
                    keys = self.get_keys_in_file(file_content)

                    repo_file, created = RepoFile.objects.get_or_create(
                        commit=file["sha"],
                        file_name=file["path"],
                    )

                    repo.last_commit = file["sha"]

                    for key in keys:
                        repo_key, created = RepoKey.objects.get_or_create(key=key)
                        repo_file.keys.add(repo_key)

                    repo_file.save()

                    repo.files.add(repo_file)

                    repo.save()

        return repo
    
    def sync_repos(self, repos):
        for repo in repos:
            self._sync_repo(repo)

    def _get_repo(self, full_name):
        if full_name in self.repos:
            return self.repos[full_name]

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

    def get_repo_by_name(self, full_name):
        return self._get_repo(full_name)

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

import os
import re
import requests
import time

from django.conf import settings

from repos.models import Repo, RepoFile, RepoKey

# Get environment variable for the GitHub API key
# This is a personal access token
GITHUB_AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN

class RepoManager:
    TAGS = [
        'solidity',
        'hardhat',
    ]

    LANGUAGES = [
        'solidity',
        'javascript',
    ]

    # Regex to find any string that is 0x followed by only 40 hex characters without include anymore
    HEX_KEY_REGEX = r'0x[a-fA-F0-9]{40}'

    def __init__(self):
        self.repo_calls = {}
        self.repos = {}

    def start(self):
        print("RepoManager started")

        # self.get_repos_by_tag("solidity")
        self.sync_repos(self.get_repos_by_tag("hardhat"))

        for tag in self.TAGS:
            self.sync_repos(self.get_repos_by_tag(tag))

        for language in self.LANGUAGES:
            self.sync_repos(self.get_repos_by_language(language))

    def _sync_repo(self, repo):
        repo, created = Repo.objects.get_or_create(
            full_name=repo["full_name"],
            default_branch=repo["default_branch"]
        )

        files = self.get_files(repo.full_name, repo.default_branch)
        if repo.last_commit != files[0]["sha"]:
            repo.last_commit = files[0]["sha"]

            for file in files:
                if file["type"] == "blob":
                    file_content = self.get_file(
                        repo.full_name, repo.default_branch, file["path"])
                    keys = self.get_keys_in_file(file_content)

                    repo_file, created = RepoFile.objects.get_or_create(
                        commit=file["sha"],
                        file_name=file["path"],
                    )

                    for key in keys:
                        repo_key, created = RepoKey.objects.get_or_create(
                            key=key)
                        repo_file.keys.add(repo_key)

                    repo.files.add(repo_file)

        return repo

    def sync_repos(self, repos):
        for repo in repos:
            self._sync_repo(repo)

    def _authorized_get_request(self, url):
        r = requests.get(url, headers={
            "Authorization": f"token {GITHUB_AUTH_TOKEN}"
        })

        return r

    def _get_repo(self, full_name):
        print("Getting repo %s" % (full_name))

        if full_name in self.repos:
            return self.repos[full_name]

        url = f"https://api.github.com/repos/{full_name}"

        r = self._authorized_get_request(url)
        res = r.json()

        return res

    # DRY component used to get the content of a repository
    def _get_repos(self, url):
        r = self._authorized_get_request(url)
        res = r.json()

        for item in res["items"]:
            self.repos[item["full_name"]] = item

        return res["items"], r.links

    def _get_or_make_call(self, url):
        if url not in self.repo_calls:
            _repos, _links = self._get_repos(url)

            self.repo_calls[url] = (_repos, _links)

            return _repos, _links

        return self.repo_calls[url]

    def get_repos_by_url(self, url, cap, arg1, arg2):
        querying = True

        repos = []

        page = 0
        while querying and (page <= cap or cap == 0):
            _url = url % (arg1, arg2 + page)

            _repos, _links = self._get_or_make_call(_url)

            repos.append(_repos)

            if 'next' in _links:
                page += 1
            else:
                querying = False

        return [_repo for _repo in _repos for repo in repos]

    # Search all repos by tag
    def get_repos_by_tag(self, tag, cap=0):
        return self.get_repos_by_url(
            "https://api.github.com/search/repositories?q=topic:%s&sort=-stars&order=desc&per_page=100&page=%s",
            cap,
            tag,
            1
        )

    # Search all repos by language
    def get_repos_by_language(self, language, cap=0):
        return self.get_repos_by_url(
            "https://api.github.com/search/repositories?q=language:%s&sort=-stars&order=desc&per_page=100&page=%s",
            cap,
            language,
            1
        )

    def get_repo_by_name(self, full_name):
        return self._get_repo(full_name)

    # Get all the files in the repository
    def get_files(self, full_name, branch=None):
        if not branch:
            branch = self._get_repo(full_name)["default_branch"]

        url = f"https://api.github.com/repos/{full_name}/git/trees/{branch}?recursive=1"

        r = self._authorized_get_request(url)
        res = r.json()

        if "message" in res and "API rate limit exceeded" in res["message"]:
            print("API rate limit exceeded")
            time.sleep(60)
            return []

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

        r = self._authorized_get_request(url)

        return r.text

    def get_keys_in_file(self, file_content):
        # find all keys in the file
        keys = re.findall(self.HEX_KEY_REGEX, file_content)

        return keys

    def get_contacts(self, full_name):
        url = f"https://api.github.com/repos/{full_name}/stargazers"

        r = self._authorized_get_request(url)
        res = r.json()

        return res

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
        'truffle',
        'brownie',
        'web3',
        'ethers',
        'ganache',
    ]

    LANGUAGES = [
        'solidity',
    ]

    BLOCKED_PATHS = [
        "node_modules",
        "package-lock.json",
        "package.json",
        "yarn.lock",
        "yarn-error.log",
        "yarn.lock",
        "yarn-error.log",
        "venv",
        ".pyc"
    ]

    # Regex to find ethereum private keys
    HEX_KEY_REGEX = re.compile(
        r"[a-fA-F0-9]{64}"
    )

    def __init__(self):
        self.repo_calls = {}
        self.repos = {}

    def start_retrieval(self):
        print("RepoManager started retrieval")

        for tag in self.TAGS:
            for repo in self.get_repos_by_tag(tag):
                self._retrieve_or_create_repo(repo)

        for language in self.LANGUAGES:
            for repo in self.get_repos_by_language(language):
                self._retrieve_or_create_repo(repo)

    def start_sync(self):
        print("RepoManager started file sync")

        repos = Repo.objects.filter(files__count=0)

        self.sync_repos(repos)

    def _retrieve_or_create_repo(self, repo):
        repo, created = Repo.objects.get_or_create(
            full_name=repo["full_name"],
            default_branch=repo["default_branch"]
        )

        return repo

    def _sync_repo(self, repo, cap=None):
        repo, created = Repo.objects.get_or_create(
            full_name=repo["full_name"],
            default_branch=repo["default_branch"]
        )

        # Get every commit in the repo
        commits = [commit['sha']
                   for commit in self.get_commits(repo.full_name)]

        if cap:
            commits = commits[:cap]

        for commit in commits:
            files = self.get_files(repo.full_name, commit)
            if RepoFile.objects.filter(commit=commit).exists():
                repo.last_commit = files[0]["sha"]

                for file in files:
                    if file["type"] == "blob":
                        # make sure that this file is not a dependency file
                        if all([blocked_path not in file["path"] for blocked_path in settings.BLOCKED_PATHS]):
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

    def sync_repos(self, repos, cap=None):
        if cap:
            repos = repos[:cap]

        for repo in repos:
            self._sync_repo(repo, cap)

        return True

    def _authorized_get_request(self, url):
        r = requests.get(url, headers={
            "Authorization": f"token {GITHUB_AUTH_TOKEN}"
        })

        return r

    def _get_repo(self, full_name):
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

    def get_commits(self, full_name, branch=None, page=1):
        if not branch:
            branch = self.get_repo_by_name(full_name)["default_branch"]

        querying = True

        commits = []

        _page = 0

        while querying:
            url = f'https://api.github.com/repos/{full_name}/commits?page={page + _page}&per_page=100'

            if url in self.repo_calls:
                return self.repo_calls[url]

            r = self._authorized_get_request(url)
            res = r.json()

            commits.append(res)

            self.repo_calls[url] = res

            if 'next' in r.links:
                _page += 1
            else:
                querying = False

        # convert the above for loop to a one liner
        commits = [c for commit in commits for c in commit]

        return commits

    def get_first_commit(self, full_name):
        commits = self.get_commits(full_name)

        return commits[len(commits) - 1]["sha"]

    def get_all_commits_count(self, full_name, branch=None):
        if not branch:
            branch = self._get_repo(full_name)["default_branch"]

        first_commit = self.get_first_commit(full_name)

        url = f'https://api.github.com/repos/{full_name}/compare/{first_commit}...{branch}'

        if url in self.repo_calls:
            return self.repo_calls[url]

        r = self._authorized_get_request(url)
        res = r.json()

        commit_count = res['total_commits'] + 1

        self.repo_calls[url] = commit_count

        return commit_count

    # Get all the files in the repository
    # `sha` can be commit hash or branch name
    def get_files(self, full_name, sha=None):
        if not sha:
            sha = self._get_repo(full_name)["default_branch"]

        url = f"https://api.github.com/repos/{full_name}/git/trees/{sha}?recursive=1"

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
    # `sha` can be commit hash or name of branch
    def get_file(self, full_name, sha, filename):
        url = f"https://raw.githubusercontent.com/{full_name}/{sha}/{filename}"

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

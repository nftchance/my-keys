from django.test import TestCase

from .repos import RepoManager


class RepoManagerTestCase(TestCase):
    def setUp(self):
        self.repo_manager = RepoManager()

    def test_get_repos_by_tag(self):
        repos = self.repo_manager.get_repos_by_tag("hardhat", 1)
        self.assertTrue(len(repos) > 0)

    def test_get_repos_by_language(self):
        repos = self.repo_manager.get_repos_by_language("solidity", 1)
        self.assertTrue(len(repos) > 0)

    def test_get_repos_by_tag_multiple_pages(self):
        repos = self.repo_manager.get_repos_by_tag("hardhat", 2)
        self.assertTrue(len(repos) > 0)

    def test_get_repo_by_name(self):
        repo = self.repo_manager.get_repo_by_name("nftchance/nft-nondilutive")
        self.assertTrue(len(repo) > 0)

    def test_get_files(self):
        files = self.repo_manager.get_files(
            "nftchance/nft-nondilutive", "main")
        self.assertTrue(len(files) > 0)

    def test_get_files_without_branch(self):
        files = self.repo_manager.get_files("nftchance/nft-nondilutive")
        self.assertTrue(len(files) > 0)

    def test_get_filtered_files(self):
        files = self.repo_manager.get_files(
            "nftchance/nft-nondilutive", "main")
        self.assertTrue(len(files) > 0)

    def test_get_file(self):
        files = self.repo_manager.get_file(
            "nftchance/my-keys", "master", "test/keys.txt")
        self.assertTrue(len(files) > 0)

    def test_get_file_keys(self):
        file_content = self.repo_manager.get_file(
            "nftchance/my-keys", "master", "test/keys.txt")
        self.assertTrue(len(file_content) > 0)

        keys = self.repo_manager.get_keys_in_file(file_content)
        self.assertTrue(len(keys) != 0)

from django.test import TestCase

from .repos import RepoManager

# Create your tests here.
class RepoManagerTestCase(TestCase):
    def test_get_repos_by_tag(self):
        repo_manager = RepoManager()
        repos = repo_manager.get_repos_by_tag("hardhat")
        self.assertTrue(len(repos) > 0) 

    def test_get_repos_by_language(self):
        repo_manager = RepoManager()
        repos = repo_manager.get_repos_by_language("solidity")
        self.assertTrue(len(repos) > 0)

    def test_get_files(self):
        repo_manager = RepoManager()
        files = repo_manager.get_files("grumbach/ft_ping")
        self.assertTrue(len(files) > 0)

    def test_get_filtered_files(self):
        # Use personal repository for this
        pass

    def test_get_file(self):
        repo_manager = RepoManager()
        files = repo_manager.get_file("grumbach/ft_ping", "master", "srcs/gen_ip_header.c")
        self.assertTrue(len(files) > 0)
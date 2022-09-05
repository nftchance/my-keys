from django.db import models

from .repos import RepoManager

class RepoKey(models.Model):
    key = models.CharField(max_length=200)

class RepoFile(models.Model):
    commit = models.TextField()    
    file_name = models.TextField() 
    contents_hash = models.TextField()

    keys = models.ManyToManyField(RepoKey)

class Repo(models.Model):
    full_name = models.CharField(max_length=255)
    default_branch = models.CharField(max_length=255)

    files = models.ManyToManyField(RepoFile)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    def get_repo(self):
        return RepoManager().get_repo_by_name(self.full_name)

    def get_files(self):
        return RepoManager().get_files(self.full_name)

    def get_files_of_branch(self, branch): 
        return RepoManager().get_files(self.full_name, branch)

    def get_file(self, branch=default_branch, file_name=None):
        if not file_name:
            raise Exception("No file name provided")

        return RepoManager().get_file(self.full_name, branch, file_name)

    class Meta:
        ordering = ['-updated_at']
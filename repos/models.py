from django.db import models

class RepoKey(models.Model):
    key = models.CharField(max_length=200)

    def __str__(self):
        return self.key

class RepoFile(models.Model):
    commit = models.TextField()    
    file_name = models.TextField() 

    keys = models.ManyToManyField(RepoKey)

    def __str__(self):
        return self.file_name

class Repo(models.Model):
    full_name = models.CharField(max_length=255)
    default_branch = models.CharField(max_length=255)

    files = models.ManyToManyField(RepoFile)
    last_commit = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['-updated_at']
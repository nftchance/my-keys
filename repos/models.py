from django.db import models

class RepoKey(models.Model):
    key = models.CharField(max_length=200)

class RepoFile(models.Model):
    commit = models.TextField()    
    file_name = models.TextField() 
    contents_hash = models.TextField()

    keys = models.ManyToManyField(RepoKey)

class Repo(models.Model):
    full_name = models.CharField(max_length=255)

    files = models.ManyToManyField(RepoFile)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
from django.db import models

from keys.keys import KeyManager

KEY_MANAGER = KeyManager()

class RepoKey(models.Model):
    def save(self, *args, **kwargs):
        self.is_private_key = KEY_MANAGER.is_private_key(self.key)

        if self.is_private_key:
            self.address = KEY_MANAGER.get_address(self.key)
        elif KEY_MANAGER.is_address(self.key):
            self.address = self.key

        if self.address:
            self.balance = KEY_MANAGER.get_balance(self.address)

        super(RepoKey, self).save(*args, **kwargs)

    key = models.CharField(max_length=200)
    is_private_key = models.BooleanField(default=False)
    address = models.CharField(max_length=200, null=True, blank=True)
    balance = models.CharField(max_length=200, null=True, blank=True)

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
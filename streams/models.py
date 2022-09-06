
from django.db import models

class StreamVod(models.Model):
    vod_id = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vod_id

class Stream(models.Model):
    username = models.TextField()

    vods = models.ManyToManyField(StreamVod, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-created_at']
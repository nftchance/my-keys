
from django.db import models


class StreamVod(models.Model):
    vod_id = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vod_id


class Stream(models.Model):
    stream_id = models.CharField(max_length=255)

    title = models.CharField(max_length=255)
    description = models.TextField()

    view_count = models.IntegerField()

    started_at = models.DateTimeField()

    duraton = models.PositiveIntegerField()

    category_id = models.CharField(max_length=255)
    category_name = models.CharField(max_length=255)

    is_live = models.BooleanField(default=False)

    vods = models.ManyToManyField(StreamVod, related_name='streams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Streamer(models.Model):
    username = models.TextField()

    streams = models.ManyToManyField(Stream, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-created_at']

from django.contrib import admin

from .models import Streamer, Stream, StreamVod 


@admin.register(Streamer)
class StreamerAdmin(admin.ModelAdmin):
    list_display = ('username', 'created_at', 'updated_at')

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('stream_id', 'title', 'view_count', 'is_live', 'created_at', 'updated_at')

@admin.register(StreamVod)
class StreamVodAdmin(admin.ModelAdmin):
    list_display = ('vod_id', 'created_at', 'updated_at')
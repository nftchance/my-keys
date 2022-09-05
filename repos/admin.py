from django.contrib import admin

from .models import Repo, RepoFile, RepoKey

@admin.register(Repo)
class RepoAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created_at', 'updated_at')

@admin.register(RepoFile)
class RepoFileAdmin(admin.ModelAdmin):
    list_display = ('commit', 'file_name')

@admin.register(RepoKey)
class RepoKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_private_key', 'address', 'balance')
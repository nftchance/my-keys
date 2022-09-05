import os

from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            from .jobs import JobManager

            manager = JobManager()

            manager.ready()

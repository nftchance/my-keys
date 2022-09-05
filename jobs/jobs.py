# runapscheduler.py
from repos.repos import RepoManager
from keys.keys import KeyManager
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)


@util.close_old_connections
def sync_repos():
    repo_manager = RepoManager()
    repo_manager.start()


@util.close_old_connections
def sync_keys():
    key_manager = KeyManager()
    key_manager.start()

# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class JobManager:
    def ready(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            sync_repos,
            trigger=CronTrigger(second="*/30"),  # Every 6000 seconds
            id="sync_repos",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=False,
        )
        print("Added job 'sync_repos'.")

        scheduler.add_job(
            sync_keys,
            trigger=CronTrigger(second="*/30"),  # Every 60 seconds
            id="sync_keys",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=False,
        )
        print("Added job 'sync_keys'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        print(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            print("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            print("Stopping scheduler...")
            scheduler.shutdown()
            print("Scheduler shut down successfully!")

# runapscheduler.py
from repos.repos import RepoManager
from keys.keys import KeyManager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

repo_manager = RepoManager()
key_manager = KeyManager()

@util.close_old_connections
def retrieve_repos():
    repo_manager.start_retrieval()

@util.close_old_connections
def sync_repos():
    repo_manager.start_sync()

@util.close_old_connections
def sync_keys():
    key_manager.start()

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class JobManager:
    def ready(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Retrieve repos every 12 hours
        scheduler.add_job(
            retrieve_repos,
            trigger=CronTrigger(second="*/59"),
            id="retrieve_repos",
            max_instances=1,
            replace_existing=True,
        )
        print("Added job 'retrieve_repos'.")

        scheduler.add_job(
            sync_repos,
            trigger=CronTrigger(second="*/59"),
            id="sync_repos",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        print("Added job 'sync_repos'.")

        scheduler.add_job(
            sync_keys,
            trigger=CronTrigger(second="*/59"),
            id="sync_keys",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
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

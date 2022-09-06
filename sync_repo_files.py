import django
import os

# setup django with the right settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keys.settings")
django.setup()

from repos.repos import RepoManager

CONFIG = {
    'REPOS': True,
    'TWITCH': False,
}

def run():
    repo_manager = RepoManager()
    repo_manager.start_sync()

# Run the primary process
def main():
    run()

if __name__ == '__main__':
    main()

release: python manage.py migrate 
web: gunicorn keys.wsgi --log-level=info --log-file=-
sync_repos: python sync_repos.py
sync_keys: python sync_keys.py
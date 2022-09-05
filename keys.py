import os
import django

# setup django with the right settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keys.settings")
django.setup()

from keys.keys import KeyManager

def run():
    key_manager = KeyManager()
    key_manager.start()

# Run the primary process
run()


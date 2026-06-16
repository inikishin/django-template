import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")

# Take all celery settings from Django settings with the CELERY_ prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks in each app's `tasks` module/package.
app.autodiscover_tasks()

#!/bin/sh
# Start Celery beat (periodic task scheduler) backed by django-celery-beat.
set -e
cd "$(dirname "$0")/../src"
exec celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

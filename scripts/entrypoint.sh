#!/bin/sh
set -e

# Apply migrations and collect static files before starting the app.
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

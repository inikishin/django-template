#!/bin/sh
# Start Flower - web UI for monitoring Celery tasks (http://localhost:5555).
set -e
cd "$(dirname "$0")/../src"
exec celery -A app flower --port=5555

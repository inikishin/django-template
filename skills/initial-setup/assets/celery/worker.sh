#!/bin/sh
# Start the Celery worker. Run from anywhere; switches into src/ itself.
set -e
cd "$(dirname "$0")/../src"
exec celery -A app worker -l info

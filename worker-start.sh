#! /usr/bin/env bash
set -e


# Kill any existing Celery workers
pkill -f 'celery -A app.worker worker' || true

python /app/app/celeryworker_pre_start.py
# Standard command, no autoreload
#celery -A app.worker worker -l info -Q main-queue -c 1
celery -A app.worker worker -l info -Q main-queue --autoscale=4,2

# Dockerfile will run it with autoreload:
#watchmedo shell-command --patterns="*.py" --recursive --command='./worker-start.sh' .
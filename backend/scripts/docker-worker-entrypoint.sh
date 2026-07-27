#!/usr/bin/env sh
set -eu

# Default queue set matches task_routes in app/workers/celery_app.py.
QUEUES="${CELERY_QUEUES:-refresh,delivery,media,maintenance}"

exec celery -A app.workers worker \
  --loglevel="${CELERY_LOG_LEVEL:-info}" \
  --concurrency="${CELERY_CONCURRENCY:-2}" \
  -Q "${QUEUES}" \
  "$@"

#!/usr/bin/env sh
set -eu

MODE="${1:-api}"
shift || true

case "$MODE" in
  api)
    if [ "${RUN_MIGRATIONS_ON_START:-true}" = "true" ] && [ -n "${DATABASE_URL:-}" ]; then
      echo "Running database migrations (alembic upgrade head)..."
      alembic upgrade head
    else
      echo "Skipping migrations on API start."
    fi
    # Dokploy often injects PORT; fall back to API_PORT then 8000.
    PORT_VALUE="${PORT:-${API_PORT:-8000}}"
    exec uvicorn app.main:app \
      --host "${API_HOST:-0.0.0.0}" \
      --port "${PORT_VALUE}" \
      --workers "${UVICORN_WORKERS:-1}" \
      "$@"
    ;;
  worker)
    exec ./scripts/docker-worker-entrypoint.sh "$@"
    ;;
  beat)
    exec celery -A app.workers beat --loglevel="${CELERY_LOG_LEVEL:-info}" "$@"
    ;;
  *)
    echo "Unknown mode: $MODE (expected api, worker, or beat)" >&2
    exit 1
    ;;
esac

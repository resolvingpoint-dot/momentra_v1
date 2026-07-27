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
    # Fail closed with a clear message before uvicorn (shows in Dokploy logs).
    python - <<'PY'
from app.core.config import settings, validate_production_security
try:
    validate_production_security(settings)
except Exception as exc:
    print("=" * 72)
    print("FATAL: production security check failed — API will not start.")
    print(exc)
    print("Fix Dokploy Environment, then redeploy. See backend/DOKPLOY.md")
    print("=" * 72)
    raise SystemExit(1)
print(
    "Security preflight ok (debug=%s momentra_env=%s storage=%s)"
    % (
        settings.debug,
        settings.momentra_env or "(unset)",
        "set" if settings.effective_storage_public_base_url else "MISSING",
    )
)
PY
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

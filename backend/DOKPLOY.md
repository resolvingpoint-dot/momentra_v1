# Dokploy Deployment Guide (Backend)

This backend deploys with the included `Dockerfile` (API + optional Celery worker/beat).

## 1) Create service in Dokploy

- **Build type:** Dockerfile
- **Docker Context Path:** `backend`
- **Docker File:** `Dockerfile` (or `backend/Dockerfile` if context is repo root)
- **Container port:** `8000` (or Dokploy’s injected `PORT`)

For Celery as separate services (same image):

| Service | Command | Extra env |
|---|---|---|
| API | default (`api`) | `RUN_MIGRATIONS_ON_START=true` |
| Worker | `worker` | `RUN_MIGRATIONS_ON_START=false` |
| Beat | `beat` | `RUN_MIGRATIONS_ON_START=false` |

Or deploy [`docker-compose.yml`](docker-compose.yml) (api + worker + beat + redis).

## 2) Environment variables

Required for production (`DEBUG=false`):

- `DATABASE_URL` — Postgres / Supabase pooler
- `APP_SESSION_SECRET` — random secret (required when `DEBUG=false`)
- Firebase (one of):
  - `FIREBASE_SERVICE_ACCOUNT_JSON_B64`
  - `FIREBASE_CREDENTIALS_PATH`
  - `FIREBASE_PROJECT_ID` + `FIREBASE_CLIENT_EMAIL` + `FIREBASE_PRIVATE_KEY`
- `CORS_ORIGINS_STR` — e.g. `https://www.momentra.tech,https://momentra.tech`

Recommended:

- `REDIS_URL` — required for Celery; e.g. `redis://redis:6379/0` on compose, or your Dokploy Redis host
- `MOMENTRA_APP_INVITE_BASE_URL` — e.g. `https://www.momentra.tech/invite`
- `MOMENTRA_RESEND_API_KEY` / `MOMENTRA_RESEND_FROM`
- `UVICORN_WORKERS` (default `1`)

Do **not** set `ALLOW_TEST_AUTH=true` in production.

## 3) Health check

- Liveness: `GET /health` → `{"status":"ok",...}`
- Readiness: `GET /health/ready` (DB / Redis / Celery)

Dockerfile healthcheck uses `/health`.

## 4) Migrations

API container runs `alembic upgrade head` on start when `RUN_MIGRATIONS_ON_START=true` (default for API).

## 5) First deploy validation

- `/health` returns 200
- `/docs` loads
- Auth exchange + a personal/group pulse call succeed
- If using workers: Celery connects to Redis (not `localhost` inside the container)

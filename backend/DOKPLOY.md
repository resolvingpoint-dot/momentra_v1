# Dokploy Deployment Guide (Backend)

This backend deploys with the included `Dockerfile` (API + Celery worker/beat) or the full Compose stack in [`docker-compose.yml`](docker-compose.yml).

## Preferred: full stack (API + worker + beat + Redis)

HTTP alone works with an API-only Dockerfile app. **Worker + beat + Redis** are required for background projection refresh and scheduled Celery jobs. Without them, `/health/ready` reports `redis: down` / `celery: down` and some pulse/projection updates stay stale until a sync rebuild or `force_refresh`.

### 1) Create (or replace) a Compose application

In Dokploy:

1. Prefer **stopping** the old single-service Dockerfile app (`momentra-backend`) so Traefik host `api.mallaapp.org` is free.
2. Create a new service → **Docker Compose** (not Dockerfile Application).
3. **Source:** GitHub/Git (not raw-only) — `build: .` needs the repo so the `Dockerfile` exists. Same repo/branch as the previous Dockerfile app is fine.
4. **Compose path:** `./backend/docker-compose.yml` (repo root = monorepo). Build context for each service is `backend/` via `build: .` inside that compose file.

That compose file starts:

| Service | Role |
|---------|------|
| `redis` | Broker for Celery |
| `api` | uvicorn + migrations on start |
| `worker` | `command: ["worker"]` |
| `beat` | `command: ["beat"]` |

### 2) Environment

Dokploy writes the Environment editor to a `.env` file next to the compose file. This compose already uses `env_file: .env`, so paste the same secrets you used for the API app:

Required when `DEBUG=false`:

- `DATABASE_URL` — Postgres / Supabase pooler
- `APP_SESSION_SECRET` — random secret
- Firebase (one of):
  - `FIREBASE_SERVICE_ACCOUNT_JSON_B64`
  - `FIREBASE_CREDENTIALS_PATH`
  - `FIREBASE_PROJECT_ID` + `FIREBASE_CLIENT_EMAIL` + `FIREBASE_PRIVATE_KEY`
- `CORS_ORIGINS_STR` — e.g. `https://www.momentra.tech,https://momentra.tech`

Recommended:

- `MOMENTRA_APP_INVITE_BASE_URL` — e.g. `https://www.momentra.tech/invite`
- `MOMENTRA_RESEND_API_KEY` / `MOMENTRA_RESEND_FROM`
- `UVICORN_WORKERS` (default `1`)

**Redis / Celery:** do **not** set `REDIS_URL` to `localhost`. Compose already forces:

```text
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

on `api`, `worker`, and `beat`. You may omit `REDIS_URL` from the Dokploy Environment editor entirely.

Do **not** set `ALLOW_TEST_AUTH=true` in production.

### 3) Domains / ports

- **Domains** tab → add `api.mallaapp.org`
  - **Service:** `api`
  - **Container port:** `8000`
  - HTTPS as you prefer (Cloudflare tunnel can terminate TLS upstream)
- Do **not** expose `worker`, `beat`, or `redis` with public domains
- Cloudflare Tunnel stays on Dokploy Traefik `:80` with Host `api.mallaapp.org` (e.g. `http://127.0.0.1:80` on the Dokploy host)

### 4) Deploy and verify

Click **Deploy**. In Logs you should see **four** services: `api`, `worker`, `beat`, `redis` (not only `momentra-backend`).

On the Dokploy host:

```bash
curl -H "Host: api.mallaapp.org" http://127.0.0.1:80/health
curl -H "Host: api.mallaapp.org" http://127.0.0.1:80/health/ready
```

Expect ready JSON with `"database":"up","redis":"up","celery":"up"`.

Worker logs should show Celery consuming queues; beat should show the scheduler started.

From any machine on the LAN / internet:

```bash
curl https://api.mallaapp.org/health
curl https://api.mallaapp.org/health/ready
```

### 5) API helper (optional)

If you generate a Dokploy API key (**Settings → Profile → API/CLI**):

```powershell
$env:DOKPLOY_URL = "http://192.168.68.108:3000"   # or https://dokploy.mallaapp.org
$env:DOKPLOY_API_KEY = "<your-key>"
# Optional: reuse secrets from a local .env for compose.saveEnvironment
$env:DOKPLOY_ENV_FILE = ".\.env"
.\scripts\dokploy-compose-deploy.ps1
```

---

## Alternative: three Dockerfile apps (same image)

| Service | Command | Extra env |
|---|---|---|
| API | default (`api`) | `RUN_MIGRATIONS_ON_START=true` |
| Worker | `worker` | `RUN_MIGRATIONS_ON_START=false` |
| Beat | `beat` | `RUN_MIGRATIONS_ON_START=false` |
| Redis | Dokploy Redis (or compose redis) | set `REDIS_URL` on all three to that host (**not** `localhost`) |

Domain only on the API app → container port `8000`.

## Health check

- Liveness: `GET /health` → `{"status":"ok",...}`
- Readiness: `GET /health/ready` (DB / Redis / Celery)

Dockerfile healthcheck uses `/health`.

## Migrations

API container runs `alembic upgrade head` on start when `RUN_MIGRATIONS_ON_START=true` (default for API). Worker/beat set this to `false` in compose.

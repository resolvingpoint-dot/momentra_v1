# Momentra Backend API

Phase 1 backend foundation for Momentra.

## Tech Stack

- **FastAPI** — async Python web framework
- **Firebase Admin SDK** — auth token verification
- **PostgreSQL / Supabase** — primary database
- **SQLAlchemy 2.0 (async)** — ORM with asyncpg driver
- **Alembic** — database migrations
- **Redis** — optional caching (falls back to in-memory)
- **Pydantic v2** — request/response schemas

## Architecture

Clean Architecture with repository pattern and service layer:

```
app/
  api/v1/        # Routers — parse input, call services, return schemas
  core/          # Config, Firebase, Security, Cache, Base
  dependencies/  # Auth dependency injection
  domains/       # Business domains (users, preferences, module_states, moments)
  tests/         # Mock-based test suite
```

## Required Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) |
| `FIREBASE_PROJECT_ID` | Firebase project ID |
| `FIREBASE_CLIENT_EMAIL` | Firebase service account client email |
| `FIREBASE_PRIVATE_KEY` | Firebase service account private key |
| `APP_SESSION_SECRET` | Secret for issuing app session JWTs |
| `APP_SESSION_EXPIRES_MINUTES` | Session token expiry (default: 60) |

**Optional:**

| Variable | Description |
|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Firebase service account JSON (alternative to FIREBASE_CLIENT_EMAIL + FIREBASE_PRIVATE_KEY) |
| `REDIS_URL` | Redis connection string (e.g. `redis://localhost:6379/0`) |
| `CORS_ORIGINS_STR` | Comma-separated allowed origins |

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Run Migrations

```bash
alembic upgrade head
```

To create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

## Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker / Dokploy

Production packaging lives in this directory:

| File | Purpose |
|---|---|
| `Dockerfile` | API image (migrations + uvicorn entrypoint) |
| `docker-compose.yml` | `api` + `worker` + `beat` + `redis` |
| `scripts/docker-entrypoint.sh` | `alembic upgrade head` then start process |
| `scripts/docker-worker-entrypoint.sh` | Celery worker (all queues) |

### Required production env (set in Dokploy UI)

- `DEBUG=false`
- `DATABASE_URL` — Supabase pooler or managed Postgres
- `APP_SESSION_SECRET` — random 256-bit key
- `FIREBASE_SERVICE_ACCOUNT_JSON_B64` **or** `FIREBASE_CREDENTIALS_PATH` **or** project/email/key trio
- `CORS_ORIGINS_STR` — e.g. `https://www.momentra.tech,https://momentra.tech`
- `REDIS_URL` — e.g. `redis://redis:6379/0` when using bundled Redis

Optional but recommended: `MOMENTRA_RESEND_*`, `MOMENTRA_APP_INVITE_BASE_URL`, `STORAGE_PUBLIC_BASE_URL`.

### Local compose smoke test

```bash
cp .env.example .env   # fill DATABASE_URL + secrets
# In .env for compose: REDIS_URL=redis://redis:6379/0
docker compose up --build
curl http://localhost:8000/health
curl http://localhost:8000/health/ready
```

### Dokploy

1. Create a **Compose** app (or three **Application** services from the same image).
2. Set **build context** to `backend/` and use `docker-compose.yml`, **or** build `Dockerfile` only and run:
   - API: default CMD `api`
   - Worker: command `worker`, `RUN_MIGRATIONS_ON_START=false`
   - Beat: command `beat`, `RUN_MIGRATIONS_ON_START=false`
3. Health check path: `/health` (liveness). Use `/health/ready` if Redis/Celery must be up.
4. Do **not** commit `.env` — configure secrets in Dokploy.

Worker only runs migrations on the API container (`RUN_MIGRATIONS_ON_START=true` by default there).

## Run Tests

```bash
pytest app/tests/ -v
```

## API Endpoints

### Health
```bash
curl http://localhost:8000/health
```

### Auth Sync
```bash
curl -X POST http://localhost:8000/api/v1/auth/sync \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
```

### Auth Exchange
```bash
curl -X POST http://localhost:8000/api/v1/auth/exchange \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
```

### Get Current User
```bash
curl http://localhost:8000/api/v1/me \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN_OR_SESSION_TOKEN>"
```

### App Bootstrap
```bash
curl http://localhost:8000/api/v1/app/bootstrap \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
```

### Create Moment
```bash
curl -X POST http://localhost:8000/api/v1/moments \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"context_type": "MY_MONEY", "title": "My first moment"}'
```

### Context Home Endpoints
```bash
curl http://localhost:8000/api/v1/my-money/home \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
curl http://localhost:8000/api/v1/group/home \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
curl http://localhost:8000/api/v1/business/home \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
curl http://localhost:8000/api/v1/circle/home \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
curl http://localhost:8000/api/v1/life360/home \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
curl http://localhost:8000/api/v1/memory/home \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>"
```

## Database Tables

- `users` — Firebase-authenticated users
- `user_preferences` — Per-user preferences (selected context)
- `module_states` — State machine for each module (EMPTY → SETUP → ACTIVE)
- `moments` — Base moments with context and status
- `moment_media` — Media attachments for moments

## Keywords

**Module keys:** MY_MONEY, GROUP, BUSINESS, CIRCLE, LIFE360, MEMORY, PULSE

**States:** EMPTY, SETUP, ACTIVE

**Context types for moments:** MY_MONEY, GROUP, BUSINESS (CIRCLE not creatable directly in Phase 1)

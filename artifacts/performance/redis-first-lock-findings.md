# Redis-first production lock — Phase 1 / Dokploy audit / interpret notes

Generated during implementation of the frozen Redis-first lock.

## Production probe (from India client → api.mallaapp.org)

| Path | Status | Client RTT (approx) | Body |
|------|--------|---------------------|------|
| GET /health cold | 200 | ~1070 ms | `status=ok` |
| GET /health warm | 200 | ~721 ms | `status=ok` |
| GET /health/ready cold | 200 | ~3354 ms | `database=up redis=up celery=up` |
| GET /health/ready warm | 200 | ~3525 ms | same |

### Interpretation

1. **Redis is up in production** (`/health/ready` → `redis:up`, `celery:up`). Shared compose Redis is functioning; in-memory fallback is not the current failure mode.
2. **`/health` alone is hundreds of ms from this network path.** That is TLS/proxy/geography, not projection rebuild. Acceptance target `<100 ms` for `/health` p95 is server-side; client RTT from India will still dominate until measured on-VPS or same-region.
3. **`/health/ready` ~3.3–3.5 s** while redis+celery report up strongly suggests **Postgres RTT / pooler latency** on the readiness DB ping (and therefore on cold projection builds). This matches the plan's top production hypothesis: external DB locality.
4. Authenticated Pulse cold/warm + post-mutation sequence still needs `MOMENTRA_PROBE_TOKEN` (+ optional moment IDs). Run:

```bash
python backend/scripts/prod_read_probe.py --base-url https://api.mallaapp.org --token "$TOKEN"
```

## Compose / Dokploy config (code-level audit)

| Knob | Value | Source |
|------|-------|--------|
| REDIS_URL (api/worker/beat) | forced `redis://redis:6379/0` | `backend/docker-compose.yml` |
| UVICORN_WORKERS | default `1` | `docker-entrypoint.sh` |
| CELERY_CONCURRENCY | default `2` | `docker-worker-entrypoint.sh` |
| Postgres | **not** in compose; `DATABASE_URL` external | `docker-compose.yml`, `DOKPLOY.md` |
| DB pool | size 5, overflow 10 | `config.py` |

**Do not raise Uvicorn workers and Celery concurrency together on a 2-vCPU VPS** until post-mutation Pulse timings show CPU contention (API slow only during rebuild bursts).

Optional: set `ENABLE_METRICS=true` in Dokploy to scrape projection hit/miss.

## Code lock shipped

- REST logs/headers: `projection_state`, `projection_lock`, `refresh_enqueued`, `refresh_reason`, `db_*`, `redis_ms`, `projection_build_ms`, `total_ms`
- Personal/Group/Business GET: FRESH→STALE→FRESH; `force_refresh` cannot sync-rebuild when stale exists
- Personal write invalidation: `mark_stale_first=True` (no delete)
- Clients (web/iOS/Android): do not send `force_refresh=true` on routine refresh; PTR may bypass device cache only
- Probe: `backend/scripts/prod_read_probe.py`

## Next evidence-gated infra moves

1. On-VPS `curl` `/health` and `/health/ready` to separate network RTT from process time.
2. Confirm Supabase/Postgres region vs Hostinger VPS region.
3. Run authenticated `prod_read_probe.py` post-mutation sequence; immediate GET must be `projection_state=stale` with no `projection;dur=` rebuild.
4. Only then consider Celery concurrency / DB pool / region moves — no Dokploy migration.

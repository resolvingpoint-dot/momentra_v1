# Momentra Backend Architecture Governance

Platform shape is **structurally frozen**. Changes are allowed only for security, reliability, measured performance, legacy-path removal, additive domain capability, and operational hardening — not rewrites or aesthetic reorganizations.

Companion to [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) (descriptive map). This document owns **policy**.

---

## 1. Verdict

| Dimension | Assessment |
|-----------|------------|
| Architecture quality | **8.5 / 10** |
| Fit for current product | Strong — Personal / Group / Business; web + Android + iOS; REST commands + GraphQL composed reads; Redis projections; Celery + Beat; MomentEngine lifecycle; centralized AuthN/AuthZ; template expansion |
| Recommendation | **Preserve** this architecture. Next work is consolidation, enforcement, operational hardening, and legacy overlap removal — **not** a rewrite |

---

## 2. What is architecturally strong

1. **REST vs GraphQL roles** — REST for commands/mutations/lifecycle/resources; GraphQL for composed homes, Pulse, Life, Memory. GraphQL use cases live under `app/application/queries`, not in resolvers.
2. **Domains own behavior** — API → AuthN → AuthZ → domain/application service → repository/cache → event → worker.
3. **Template registries** — Personal (Life Operations, Future Building, Lifestyle, Relationships); Group (Shared Experience, Purchase, Living); Business (Team Operations, Runway, Operations). New variants extend templates, not infrastructure.
4. **MomentEngine** — Canonical create / activate / pause / complete / archive vocabulary across contexts.
5. **Postgres / Redis / Celery** — Durable truth, cache/broker, async work + Beat schedule. Keep this separation frozen.
6. **Security as a platform concern** — Firebase/session JWT, `authorization.require`, headers, HTTP + worker idempotency, correlation IDs, GraphQL hardening, metrics / optional OTel.

---

## 3. Frozen rules

### Transport

REST routers and GraphQL resolvers contain **no domain calculations**. They may: parse input, resolve principal, call authorization, invoke application/domain service, map typed errors, return output.

### Authorization

Every resource read or mutation must pass through centralized AuthZ (`app/authorization`). Domains must not rely on UI hiding or route naming alone.

Workers that act on behalf of users must either:

- receive an already-authorized immutable command, or
- re-evaluate authorization where membership changes could matter.

### Cache

Redis is **never** the business source of truth. Every cached projection needs: schema version, source version or generated time, stale/fresh behavior, invalidation owner, rebuild task, fallback behavior, observability.

### Event

Critical post-commit work must be durable or reconcilable. If an event can be lost safely, document why. Otherwise prefer outbox / reconciliation.

**Current:** DB commit → in-process EventBus → Celery.

**Target for critical events:** DB transaction → outbox row → publisher → Celery / integration → outbox marked delivered.

Do not replace EventBus entirely; use outbox only where loss matters (projection refresh, notifications, invite delivery, audit guarantees).

### Query

GraphQL calls application query use cases; it does **not** query ORM models directly. Protects parity with REST.

### Lifecycle

All context lifecycle transitions go through **MomentEngine**. Compatibility services may adapt inputs; they must not invent parallel state machines.

### Migration

Every schema change goes through **Alembic**. No startup `create_all`, ad hoc production SQL, or runtime schema mutation.

---

## 4. Ownership matrices

### 4.1 Projection and memory

| Area | Should own | Must not own |
|------|------------|--------------|
| Domain template mapper (`domains/*/templates/…`) | Domain-specific projection calculation (pulse/moments/life/memory mapping) | Cache key schemes, worker dispatch, cross-domain orchestration |
| Shared projections (`domains/projections/`) | Cache keys, orchestration, invalidation, worker dispatch | Domain business formulas |
| Shared memory (`domains/memory/`) | User-level memory persistence / query contracts | Domain-specific source mapping |
| Domain memory package (`personal/…/memory`, `business/memory/`, group template memory mappers) | Domain contribution / source mapping only | Global memory API contracts |
| GraphQL application query | Composition only | Domain calculations or raw ORM |

### 4.2 Group routers

All under `/api/v1` (prefix `/group` unless noted).

| Router | Owns | Must not own |
|--------|------|--------------|
| `group_app` | Session/bootstrap, inventory, create options, setup profiles/people/activate, catalog-style active pulse/moments/memory/life, moment lifecycle helpers used by app shell | Deep trip/shared-experience runtime; settlement ledger CRUD; legacy resource CRUD that duplicates `group` |
| `group_read` | Shared-purchase + shared-living live-hub / pulse / moments-view / quick-add hub + module quick-add | Shared-experience trip deep endpoints; workspace admin |
| `group_shared` | Shared-experience / purchase / living **setup** (profiles, create, draft, preview, activate) | Active pulse rebuild; trip expense/corpus/plans deep APIs |
| `group_trips` | Compatibility / deep trip (shared-experience) endpoints: pulse, stream, expenses, contributions, plans, approvals, quick-add, attachments | New shared-purchase/living contracts; generic group catalog |
| `group_settlements` | Moment settlement preview/CRUD/mark-settled (`/group/moments/{id}/settlements`) | Projection builds; invite mint |
| `group` | Legacy / resource CRUD: home, moments list, activate/complete/archive, expenses, purchases, events, polls, activities (older contracts) | Prefer not to add new shared-experience deep APIs here; migrate callers toward `group_app` / `group_read` / `group_trips` / `group_shared` |

### 4.3 Business routers

| Router | Owns | Must not own |
|--------|------|--------------|
| `business_app` | Session/bootstrap, workspaces CRUD/select, members, **company/workspace invites** (opaque + dual-write), create options, moment setup draft/preview/activate/cover, moment lifecycle leave/archive/delete | Active Pulse/Moments/Activity dashboards under `/business/active` |
| `business_active` | Active per-moment Pulse / Moments / Activity (+ `/business/life`, `/business/memory` contract routes) | Workspace administration; invite mint/revoke |
| `business` | Legacy / resource CRUD: home, moments list, configure/activate, jobs, workspace structure/governance, members, **moment invitations** (legacy), departments/projects, approvals, risks, transactions, quick-add drafts, notifications, activity, pulse snapshots, analytics, memory overview | Prefer not to expand; new active reads go to `business_active`; new workspace invites to `business_app` |

---

## 5. Invite migration matrix

**Rule:** Stop **issuing** a legacy invite type before removing its **accept** path. Removal dates stay `TBD` until product picks a cutover.

| Context | Old route / path | New route / path | Issue allowed? | Accept allowed? | Revocation path | Removal date |
|---------|------------------|------------------|----------------|-----------------|-----------------|--------------|
| Cross-moment email / signed JWT | `POST /api/v1/moments/{id}/email-invites`, share-invite, invite-draft (`invites.py` → `InviteService`) | Opaque mint via `PlatformInviteService` (often dual-write from `InviteService` / setup) | Legacy: yes (during migration); prefer opaque when enabled | `POST /api/v1/invites/{token}/accept` | Refresh/revoke via invite-draft refresh + service revoke | TBD |
| Cross-moment accept (token) | `POST /api/v1/invites/{token}/accept` (JWT/email token) | Opaque accept when code shape matches (`PlatformInviteService.accept`) | N/A | Both until cutover | Platform revoke by invite id; legacy cancel where applicable | TBD |
| Business workspace / company | Email-bound `BusinessWorkspaceService.invite_member` dual-write fallback | `POST /api/v1/business/workspaces/{id}/invites`, `/invites/opaque`; preview/accept/decline `/company-invites/{code}`; revoke `/company-invites/by-id/{id}/revoke` | Prefer opaque when `invite_opaque_codes_enabled` | Opaque codes + `POST /workspaces/invites/accept` (routes by code shape) | Opaque revoke by id | TBD |
| Business moment invitations (legacy CRUD) | `POST/GET …/business/moments/{id}/invitations`, accept/cancel on `business.py` | Setup invite draft + opaque moment mint (`business_app` setup + `PlatformInviteService.mint_opaque_moment_invite`) | Legacy still present | Legacy accept still present | Legacy cancel; opaque revoke | TBD |
| Group moment | Legacy share/email via `InviteService` | `PlatformInviteService.create_group_invite` / mint opaque (from invite/setup flows) | Prefer opaque | Opaque + legacy accept until cutover | Platform revoke; draft refresh | TBD |

Publish cutover dates in this table when decided; do not delete accept handlers while clients may still hold issued tokens.

---

## 6. Main architectural risks

1. **Domain overlap** — `personal/projection` vs `personal/templates` vs `domains/projections`; multiple memory packages. Enforce §4.1.
2. **`app/core` dumping ground** — config, DB, Firebase, cache, storage, observability, rate limit, metrics, OTel. Long-term: move toward `app/infrastructure/{database,cache,storage,messaging,observability,identity}` **only when files are already being materially changed**.
3. **In-process EventBus nondurability** — commit can succeed and process die before Celery enqueue. Critical paths need outbox/reconciliation (§3 Event).
4. **Legacy + platform invites** — duplicated acceptance, revocation, route ambiguity, client token formats (§5).
5. **Naive timestamps** — many personal tables are `TIMESTAMP WITHOUT TIME ZONE`; aware datetimes cause production failures. Prefer `TIMESTAMPTZ` + aware UTC for **new** columns; centralize naive conversion for old tables; ban ad hoc `datetime.now()` in domain code.
6. **Router proliferation** — overlapping Group/Business endpoints; use §4.2–4.3 ownership; avoid new duplicates.
7. **Worker operational policy gaps** — see §7.

---

## 7. Worker operational guarantees

### Current (known)

| Concern | Status |
|---------|--------|
| Queues | `refresh`, `delivery`, `media`, `maintenance` (`celery_app.py` task_routes) |
| Time limits | Soft 300s, hard 360s (global Celery conf) |
| Acks | `task_acks_late=True`, `task_reject_on_worker_lost=True` |
| Prefetch | `worker_prefetch_multiplier=1` |
| Retries | Shared `RETRY_OPTS` in `workers/base.py`: autoretry on `Exception`, backoff + jitter, `max_retries` = `settings.celery_max_retries` (default **5**), `retry_backoff_max` default **600**s; no autoretry for `TemplateNotRegisteredError` |
| Eager mode | When no broker / `CELERY_TASK_ALWAYS_EAGER` — inline (tests/local) |
| Beat | Orchestration scan every 60s; cleanup nightly 03:00 UTC |

### Gaps (must document or implement before treating workers as “ops-complete”)

| Concern | Gap |
|---------|-----|
| Dead-letter / poison handling | Not established as a first-class queue or runbook |
| Queue saturation alerts | Not defined in architecture |
| Worker concurrency per queue | Not frozen in this doc / compose defaults |
| Beat leader uniqueness | Not documented for multi-instance deploy |
| Task schema / version compatibility across API + worker deploys | Not defined |
| Explicit graceful degradation when Redis or Celery unavailable | Partial (cache fallback exists); worker path needs runbook |

Add a worker runbook entry for each gap as it is closed; do not invent silent behavior.

---

## 8. Prioritized backlog

### P0

- Durable outbox (or equivalent) for critical events
- Document worker retry / time-limit / DLQ behavior (close §7 gaps)
- Remove or quarantine duplicate lifecycle paths (MomentEngine only)
- Complete legacy invite migration plan (fill §5 removal dates; stop issuing legacy first)
- Route ownership + permission matrices kept current (§4)
- Versioned cache contract on every projection
- Enforce no direct ORM access from GraphQL resolvers

### P1

- Gradually migrate timestamps to timezone-aware storage
- Consolidate duplicated authorization queries
- Reduce router overlap (new endpoints only on owning router)
- Define Business / Group / Personal aggregate ownership boundaries
- Deployment compatibility checks for API + worker schema versions
- Explicit graceful degradation when Redis or Celery is unavailable

### P2

- Gradually separate `core` into `infrastructure` packages (opportunistic moves only)
- Generate client SDKs from OpenAPI / GraphQL operations
- Event schema registry / versioning
- DB read replicas only if production evidence justifies them
- Independent worker autoscaling per queue

---

## 9. What must not change

Do **not**:

- Replace FastAPI, SQLAlchemy, Redis, or Celery
- Move to microservices
- Merge all domains into generic tables
- Convert every REST endpoint to GraphQL
- Create separate projection microservices
- Make Supabase the data API (storage only)
- Introduce Kafka at this stage
- Reorganize the repository purely for aesthetics

---

## 10. Allowed change classes

| Class | Examples |
|-------|----------|
| Security | AuthZ gaps, invite revocation, secret rotation, GraphQL hardening |
| Reliability | Outbox, retries/DLQ, idempotency, readiness probes |
| Measured performance | Projection cache contracts, query batching, budgets with evidence |
| Legacy removal | Invite cutover, duplicate lifecycle quarantine, unused routers |
| Additive domain | New template handlers, new moment types via registries |
| Operational hardening | Alerts, Beat uniqueness, deploy compatibility, runbooks |

---

## 11. Suggested package evolution (opportunistic only)

Target shape when files are already being changed — **not** a big-bang move:

```
app/
├── api/
│   ├── rest/          # today’s api/v1
│   └── graphql/
├── application/
│   ├── commands/
│   ├── queries/
│   └── ports/
├── domains/
├── authorization/
├── infrastructure/
│   ├── database/
│   ├── cache/
│   ├── messaging/
│   ├── storage/
│   └── observability/
├── workers/
└── shared/
```

`app/core/` and `app/dependencies/` remain until natural refactors justify relocation.

---

## 12. Related docs

- [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) — stack, file tree, domain inventory
- [../README.md](../README.md) — local setup / env
- [../DOKPLOY.md](../DOKPLOY.md) — production deploy

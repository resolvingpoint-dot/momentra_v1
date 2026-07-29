# Momentra Backend Platform v2

Platform foundation for the existing FastAPI / Redis / Celery backend.
This is an evolution of the current stack, not a replacement.

## Phase map

| Phase | Status | Focus |
|-------|--------|--------|
| **1 — Foundation** | Shipped | API standards, AuthN Principal, central AuthZ, security, observability |
| **2 — GraphQL reads** | 2.0–2.2 shipped (`groupMoment`) | Composed reads only; same AuthN/AuthZ path |
| **2.5 — Hardening** | Shipped | APQ, GraphQL security limits, field AuthZ, observability, SDL/compat, freeze |
| **3 — Product GraphQL** | Next | Pulse, Activity, Homes, Dashboards, Life, Memory (additive queries only) |
| **Freeze** | [ADR 0005](../adr/0005-platform-feature-freeze.md) | No platform rearchitecture after 2.5 |

## Packages (additive)

```
backend/app/
  auth/              # Principal + get_current_principal + auth audit events
  authorization/     # require(principal, action, resource)
  application/       # ports + thin use-cases (e.g. list_auth_sessions, group_moment_detail)
  security/          # headers, Idempotency-Key helper
  api/v1/            # existing REST (commands)
  api/graphql/       # Strawberry read platform at /graphql
  domains/           # unchanged bounded contexts
  workers/           # Celery + Beat
```

## Documentation index

| Doc | Purpose |
|-----|---------|
| [ADR 0001 — Platform v2](../adr/0001-backend-platform-v2.md) | Stack stays FastAPI/Redis/Celery; GraphQL deferred then gated |
| [ADR 0002 — AuthN sessions](../adr/0002-authn-session-model.md) | Firebase exchange, refresh rotation, Principal |
| [ADR 0003 — Central AuthZ](../adr/0003-central-authz.md) | Shared `require` for REST / workers / GraphQL |
| [ADR 0004 — GraphQL reads](../adr/0004-graphql-read-platform.md) | Strawberry at `/graphql`; reads only |
| [ADR 0005 — Feature freeze](../adr/0005-platform-feature-freeze.md) | Platform freeze after 2.5; Phase 3 product queries |
| [BACKEND_API_STANDARDS](./BACKEND_API_STANDARDS.md) | Errors, pagination, idempotency, no-breaking-change |
| [GRAPHQL_CONVENTIONS](./GRAPHQL_CONVENTIONS.md) | Naming, cursor connections, APQ, limits, observability |
| [SECURITY_CONTROLS](./SECURITY_CONTROLS.md) | OWASP API Top 10 mapping |
| [graphql/CODEGEN.md](./graphql/CODEGEN.md) | Client codegen notes |
| [graphql/SCHEMA_CHANGELOG.md](./graphql/SCHEMA_CHANGELOG.md) | SDL version history |

## GraphQL (Phase 2 / 2.5 / 3)

- Endpoint: `POST /graphql` (Bearer access token; rate-limited)
- Reads: `groupMoment`, `pulse(...)`, `activity(...)`
- Resolvers → application queries → domain services
- Field AuthZ via `require_permission(...)` for moment-scoped fields
- No mutations; REST remains the command layer
- APQ: Redis `gql:apq:{version}:{sha256}` (query document only; TTL + schema version)
- Hardening: depth/complexity/aliases/tokens/ops/nodes/page/body/variables/timeout; optional persisted-only
- Contracts: committed `schema.graphql` + checksum + changelog; backward-compat detector
- After 2.5: platform freeze ([ADR 0005](../adr/0005-platform-feature-freeze.md)); Phase 3 is product queries only

## Worker AuthZ pattern

Celery tasks that mutate tenant data should call:

```python
from app.authorization import ResourceRef, require

await require(
    session,
    actor_user_id,  # UUID is accepted
    "group.moment.view",
    ResourceRef(kind="group_moment", id=moment_id),
)
```

Do not bypass membership checks inside workers.

## Observability switches

| Env | Effect |
|-----|--------|
| `ENABLE_METRICS` | Expose Prometheus `/metrics` (also on when `DEBUG=true`) |
| `ENABLE_OTEL` | Optional FastAPI OpenTelemetry instrumentation |
| `GRAPHQL_*` | See [GRAPHQL_CONVENTIONS](./GRAPHQL_CONVENTIONS.md) for full limit/APQ knobs |

Headers: `X-Request-ID`, `X-Correlation-ID` (echo or equal request id). GraphQL also may set `X-GraphQL-*` diagnostic headers.

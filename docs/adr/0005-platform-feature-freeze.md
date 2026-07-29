# ADR 0005 — Backend platform feature freeze

## Status

Accepted — 2026-07-29 (effective after Phase 2.5 hardening)

## Context

Momentra Backend Platform v2 delivered REST commands, Firebase→JWT AuthN, central AuthZ, Redis/Celery, API standards, security controls, observability, and a production GraphQL read platform (including `groupMoment` and Phase 2.5 hardening: APQ, limits, schema contracts, rich GQL telemetry).

Further unscoped platform churn would slow product delivery (Personal / Group / Business clients) without proportional benefit.

## Decision

**Feature-freeze the backend platform** after Phase 2.5.

### Freeze covers

- REST application architecture (FastAPI host, `/api/v1` command layer)
- GraphQL platform (`/graphql`, extensions, APQ, DataLoader registry, conventions)
- AuthN / AuthZ contracts (`Principal`, `authorization.require`, field permission extensions)
- Observability contracts (request/correlation IDs, GraphQL diagnostic headers/metrics)
- Cursor pagination conventions
- GraphQL SDL conventions and security policies (introspection, limits, body/variable caps)

### Allowed after freeze

- Security fixes
- Defect fixes
- Infrastructure compatibility (runtime, Redis, Postgres, Celery versions)
- **Additive** capabilities: new GraphQL queries/types, new REST endpoints that reuse existing platform primitives

### Not allowed without a new ADR

- Parallel AuthZ systems
- GraphQL mutations replacing REST commands
- GraphQL JSON response caches keyed only by query hash
- Breaking changes to frozen contracts without schema changelog + client migration plan

## Phase 3 product GraphQL (after freeze)

Implement only product-facing composed reads on the hardened platform (no architectural redesign):

1. Pulse  
2. Unified Activity  
3. Personal Home  
4. Group Home  
5. Business Dashboard  
6. Life Timeline  
7. Memory  

## Consequences

Engineering focus shifts to product capabilities. Platform PRs require freeze-exception rationale. SDL exports must update `schema.graphql`, `schema.meta.json`, and `SCHEMA_CHANGELOG.md` in the same change.

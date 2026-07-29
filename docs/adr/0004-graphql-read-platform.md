# ADR 0004 — GraphQL read platform

## Status

Accepted — 2026-07-29

## Context

Phase 1 delivered shared AuthN (`Principal`), central AuthZ (`authorization.require`), API standards, and observability. Clients still need composed reads (group moment inventory with members, balances, expenses, activity) that today require multiple REST calls. GraphQL was deferred until that platform existed so the read layer would not invent a second permission or domain model.

## Decision

- Mount **Strawberry GraphQL** at **`/graphql`** on the existing FastAPI app
- GraphQL is a **read-only** composition layer; **REST remains the command layer** (no GraphQL mutations in Phase 2)
- Every operation uses the same path:

  `Bearer AuthN → Principal → authorization.require → application query → domain services → repos/Redis`

- Resolvers stay thin; composition lives in `app/application/queries/`
- Cursor-based connections for list fields (`first` / `after`)
- DataLoaders for per-request batching (e.g. users by id)
- Depth / complexity limits via settings (`graphql_max_depth`, `graphql_max_complexity`)
- **No GraphQL-specific Redis cache keys**; domain projection caches remain authoritative
- Automatic Persisted Queries (APQ) deferred to a later hardening phase

First vertical: `groupMoment` (Phase 2.2). Dashboards (Pulse, Activity, Home, Business, Life, Memory) come after this vertical is stable.

## Consequences

- Clients may adopt `/graphql` for composed views without changing mutation clients
- Duplicate AuthZ / DTO / SQL in resolvers is explicitly forbidden
- GraphQL IDE follows the same production docs-disable policy as OpenAPI

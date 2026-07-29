# ADR 0001 — Backend Platform v2

## Status

Accepted — 2026-07-29

## Context

Momentra already runs FastAPI, PostgreSQL, Redis, Celery workers, and Celery Beat with domain services for Personal, Group, Business, and related contexts. Cross-cutting platform concerns (typed principal, central AuthZ, API standards, security headers, observability) were partial or domain-local. GraphQL was proposed as a read-composition layer, but building it before shared AuthN/AuthZ and API standards would duplicate transport-specific security.

## Decision

Evolve the existing stack into **Backend Platform v2** without replacing FastAPI, Redis, Celery, workers, or Beat.

| Phase | Scope |
|-------|--------|
| **1 (now)** | API standards, AuthN Principal, central AuthZ, security hardening, observability, thin `application/` ports |
| **2** | GraphQL read platform (`/graphql`) using the same AuthN/AuthZ/application path — no mutations initially |
| **3** | Developer platform (OpenAPI polish, SDKs, contract tests) |
| **4** | Platform services (webhooks, event schemas, gateway, search, multi-region) |

**REST remains the command layer.** GraphQL is deferred until Phase 1 gates are met.

GraphQL resolvers (when added) must call:

```
AuthN Principal → authorization.require → application query → domain service → repository/cache
```

They must not introduce custom SQL or parallel permission logic.

## Consequences

- Additive packages: `app/auth/`, `app/authorization/`, `app/application/`, `app/security/`
- Existing `domains/` stay in place; no big-bang rewrite
- No breaking changes to `/api/v1` response shapes for current clients
- Dual AuthZ implementations should not run indefinitely — migrate call sites to the central facade incrementally

# ADR 0002 — AuthN session model

## Status

Accepted — 2026-07-29

## Context

Clients authenticate with Firebase, then use Momentra access + refresh tokens. Refresh sessions are stored in PostgreSQL (`auth_refresh_sessions`) with hashed tokens, family rotation, and reuse detection. Access tokens are short-lived JWTs with no server-side denylist.

## Decision

Keep the Firebase → Momentra session exchange:

1. Client presents Firebase ID token to `POST /api/v1/auth/firebase/exchange`
2. FastAPI verifies Firebase identity and provisions the Momentra user
3. Server issues access JWT (`type=session`) + opaque refresh token (hashed server-side)
4. Clients authenticate REST (and future GraphQL) with the access bearer
5. `POST /api/v1/auth/refresh` rotates refresh tokens; reuse of a rotated token revokes the entire family
6. `POST /api/v1/auth/logout` / `logout-all` revoke refresh sessions
7. `GET/DELETE /api/v1/auth/sessions` list and revoke individual device sessions

Introduce a typed **`Principal`** (user_id, session_id when known, device metadata, auth_strength, scopes, claims) shared by REST dependencies and documented for Celery workers (workers pass explicit `actor_user_id`).

### Explicit non-goals (Phase 1)

- Service / m2m API keys (no consumer yet)
- Server-side access-token denylist (short TTL + refresh revocation is the model)

## Consequences

- Existing `get_current_user` / `get_current_user_id` remain; `get_current_principal` wraps them
- Auth security events (`auth.login`, `auth.refresh`, `auth.refresh_reuse`, `auth.logout`, `auth.logout_all`, `auth.session_revoke`) publish on the domain event bus for audit
- Rate limiting peeks the bearer `sub` when present so authenticated traffic can be keyed by identity

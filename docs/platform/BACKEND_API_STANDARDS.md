# Backend API standards

Momentra Platform v2 HTTP conventions for `/api/v1`. These document existing behaviour and guide **new** code. **No breaking changes** to current client contracts.

## Versioning

- All product REST APIs live under `/api/v1`
- Health probes: `/health`, `/health/ready` (no `/api/v1` prefix)
- Future GraphQL (Phase 2): `/graphql`
- Deprecations: keep old routes until clients migrate; advertise via docs, not silent removal

## Error envelope

Preferred machine-readable body (from `AppError` / registered handlers):

```json
{
  "error": {
    "code": "permission_denied",
    "message": "Human-readable explanation",
    "details": null
  }
}
```

Prefer raising `AppError` subclasses (`ValidationError`, `NotFoundError`, `PermissionDeniedError`, `ConflictError`, …) from application and new route code. Legacy routes may still raise `HTTPException`; do not mass-rewrite them in Phase 1.

### Status hints

| Code | Typical HTTP |
|------|----------------|
| `validation_error` | 422 |
| `not_found` | 404 |
| `permission_denied` | 403 |
| `conflict` / lifecycle codes | 409 |
| `app_error` | 400 |

IDOR policy for group/personal moment access: unauthorized callers may receive **404** (see [ADR 0003](../adr/0003-central-authz.md)).

## Pagination

Two styles coexist:

1. **Offset** — `PageParams` / `PaginatedResponse` in `app.core.pagination` (`page`, `per_page`)
2. **Cursor** — `cursor` + `limit` query params; helper `CursorPage` in `app.core.pagination`

**New list endpoints** should pick one style and document it. Do not force-migrate existing lists.

## Idempotency

- Domain flows may use `client_request_id` fields (already present on several models)
- Opt-in HTTP header: `Idempotency-Key` with Redis helper `app.security.idempotency` for mutating routes that opt in
- Celery jobs continue to use `app.workers.idempotency`

Contract when using the header helper:

- Key is scoped to `(user_id, route, key)`
- Successful responses may be replayed from cache for the TTL
- Concurrent first attempts: only one winner; others wait or receive `conflict`

## Commands vs reads

- **REST** — commands and straightforward resource CRUD / lifecycle
- **GraphQL** — deferred; rich composed reads only (no mutations in the initial GraphQL surface)

## Authentication

See [ADR 0002](../adr/0002-authn-session-model.md). Both REST and future GraphQL use the same `Principal`.

## Authorization

See [ADR 0003](../adr/0003-central-authz.md). Call `authorization.require` rather than inventing route-local checks for new work.

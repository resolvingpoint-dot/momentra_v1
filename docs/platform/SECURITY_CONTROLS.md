# Security controls — OWASP API Top 10 mapping (Momentra Platform v2)

Momentra maps the [OWASP API Security Top 10](https://owasp.org/API-Security/)
to controls in the FastAPI backend. Edge TLS/WAF (Cloudflare/Traefik) remains
outside the app.

| Risk | Momentra control |
|------|------------------|
| API1 Broken Object Level Authorization | Central `authorization.require` + domain gates; IDOR-safe 404 for group/personal moments ([ADR 0003](../adr/0003-central-authz.md)) |
| API2 Broken Authentication | Firebase verify + Momentra JWT; refresh rotation / reuse→family revoke; session list/revoke ([ADR 0002](../adr/0002-authn-session-model.md)) |
| API3 Broken Object Property Level Authorization | Domain DTOs omit sensitive fields; business finance gated by `business.finance.view` |
| API4 Unrestricted Resource Consumption | Redis/IP+identity rate limits (`app.core.rate_limit`, includes `/graphql`); GraphQL depth/complexity/alias/token/ops/nodes/page/body/variable/timeout limits; upload size/MIME allowlist (`app.core.storage`) |
| API5 Broken Function Level Authorization | Shared AuthZ actions; privileged business roles via `permissions.py` |
| API6 Unrestricted Access to Sensitive Business Flows | Lifecycle/state checks in moment engine; AuthZ on mutating routes |
| API7 Server Side Request Forgery | No user-supplied URL fetch in API hot paths; signed storage URLs server-minted |
| API8 Security Misconfiguration | `validate_production_security`; security headers middleware; CORS allowlist; docs disabled in production |
| API9 Improper Inventory Management | OpenAPI when debug; `/api/v1` versioning; ADRs + BACKEND_API_STANDARDS |
| API10 Unsafe Consumption of APIs | Firebase Admin verify; Resend/storage with server secrets only |

## Secrets / config audit (Phase 1)

Required in production (see `app.core.config.validate_production_security`):

- `APP_SESSION_SECRET` / `JWT_SECRET` (≥48, prefer ≥64)
- `DEBUG=false`, `ALLOW_TEST_AUTH` off
- HTTPS `STORAGE_PUBLIC_BASE_URL` (or derived) + `SUPABASE_SECRET_KEY`
- Explicit `CORS_ORIGINS_STR` (no `*`)

Phase 1 does **not** automate secret rotation — ops rotates via environment.

## Headers

`SecurityHeadersMiddleware` sets:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` (restrictive defaults)
- `Cache-Control: no-store`
- `Strict-Transport-Security` when production

## AuthZ permission cache

Redis keys `authz:{user}:{kind}:{id}:{action}` with TTL **≤60s** (implemented 45s).
Do not raise TTL — membership removals must take effect quickly.

## GraphQL security (Phase 2.5)

- Introspection disabled by default (`GRAPHQL_DISABLE_INTROSPECTION`)
- APQ stores hash→query only (`gql:apq:{version}:{sha}`); never full responses
- Optional `GRAPHQL_PERSISTED_ONLY` for future public APIs
- Declarative field AuthZ: `require_permission(...)` → central `authorization.require`
- See [GRAPHQL_CONVENTIONS](./GRAPHQL_CONVENTIONS.md) for the full limit table

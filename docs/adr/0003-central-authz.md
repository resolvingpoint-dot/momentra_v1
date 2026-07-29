# ADR 0003 — Central authorization

## Status

Accepted — 2026-07-29

## Context

Authorization checks are domain-local today (`require_group_moment_access`, business permission helpers, personal ownership via `get_by_user_and_id`). Without a shared façade, REST, future GraphQL, and Celery workers risk divergent rules.

## Decision

Introduce `app.authorization.require(session, principal, action, resource)` that **dispatches to existing domain gates**. It does not invent a second policy engine.

### Action vocabulary (starter)

| Action | Meaning |
|--------|---------|
| `group.moment.view` | Active group membership or owner |
| `group.expense.create` | Member of ACTIVE group moment (view access today; tighter rules can layer later) |
| `business.moment.view` | Business moment read (member or owner) |
| `business.workspace.view` | Active workspace membership |
| `business.finance.view` | Workspace/moment member with privileged finance role (privileged member check) |
| `personal.moment.own` | Caller owns the personal moment |

### Resource references

```python
ResourceRef(kind="group_moment" | "business_moment" | "business_workspace" | "personal_moment", id=UUID)
```

### Denial policy (IDOR)

- **Group moment missing or unauthorized** → `not_found` (404) — preserve existing anti-enumeration behaviour
- **Business permission failures** → `permission_denied` (403) with domain codes where the legacy helper used 403
- **Personal moment not owned / missing** → `not_found` (404)

### Caching

Optional Redis keys `authz:{user_id}:{resource_kind}:{resource_id}:{action}` with **TTL ≤ 60 seconds**. Do not cache longer — membership/role changes must take effect quickly. Invalidate on known membership mutations when cheap.

### Worker usage

Celery tasks must not skip AuthZ. Pass an explicit actor UUID into `require` (or a principal built for that actor) before mutating tenant data.

## Consequences

- Pilot REST routes call the façade; domain services may still double-check during migration
- GraphQL (Phase 2) must use the same `require`
- Full unification of every `_require_*` is incremental, not a Phase 1 rewrite

# Moment Lifecycle Contract

**Status:** Frozen (Cross-Context Lifecycle Stability Sprint)  
**Related:** [LIFECYCLE_ROUTING_AUDIT.md](./LIFECYCLE_ROUTING_AUDIT.md), [LIFECYCLE_ROUTING_MATRIX.md](./LIFECYCLE_ROUTING_MATRIX.md)

## Canonical statuses

`DRAFT` → `ACTIVE` → `PAUSED` ↔ `ACTIVE` → `COMPLETED` → `ARCHIVED`

Also:

- `DRAFT` / `SETUP` → `ACTIVE` (activate)
- `ACTIVE` → `ARCHIVED`
- `PAUSED` → `COMPLETED` | `ARCHIVED`
- `COMPLETED` → `ARCHIVED`

Illegal transitions → **409** `lifecycle_transition_invalid`.

## Typed response (optional fields for backward compatibility)

```json
{
  "moment_id": "...",
  "context_type": "PERSONAL|GROUP|BUSINESS",
  "moment_type_code": "...",
  "previous_status": "ACTIVE",
  "status": "ARCHIVED",
  "updated_at": "...",
  "module_state": "ACTIVE|SETUP|EMPTY",
  "replacement_moment_id": "... or null",
  "replacement_moment_type_code": "... or null"
}
```

Clients must prefer `replacement_moment_id` over local guessing when present.

## Engine path

Router → context service → **MomentEngine** → adapter → event → module-state + bootstrap invalidate once → mark projections stale → return (do **not** wait for Celery rebuild).

## Selection rules

1. Keep selected if still selectable  
2. Else backend `replacement_moment_id`  
3. Else first ACTIVE → PAUSED → COMPLETED → draft  
4. Never ARCHIVED / wrong-context / inaccessible IDs  

Selection is by **moment ID**.

## Client dispatch

| Context | Coordinator target |
|---------|-------------------|
| PERSONAL | PersonalRepository / personal APIs |
| GROUP | GroupRepository / group APIs |
| BUSINESS | BusinessRepository / business APIs |

Wrong-context repository calls are forbidden.

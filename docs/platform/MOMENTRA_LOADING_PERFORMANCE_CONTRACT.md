# Momentra Loading Performance Contract

**Status:** Shared cross-platform contract  
**Related:** [Audit](./MOMENTRA_LOADING_AUDIT.md) · [Flow matrix](./MOMENTRA_LOADING_FLOW_MATRIX.md) · [Parity telemetry](../parity/TELEMETRY_CONTRACT.md)

This contract defines one shared lifecycle, event names, and metadata for measuring loading and mutation consistency. Existing parity span names (`pulse.load`, `setup.open`, …) remain valid as **child spans / aliases** under a parent flow.

---

## Shared lifecycle

Not every flow emits every mark. Names and semantics must stay consistent when present.

```
user_action
→ client_start
→ cache_read
→ shell_painted
→ network_started
→ backend_received
→ authn_completed
→ authz_completed
→ db_completed
→ redis_completed
→ service_completed
→ response_sent
→ client_response_received
→ store_updated
→ content_rendered
→ screen_interactive
→ background_reconcile_completed
→ final_consistency_reached
```

| Mark | Meaning |
|------|---------|
| `user_action` | User gesture or system trigger that starts the flow |
| `client_start` | Client flow tracer begins |
| `cache_read` | Local/memory/disk cache lookup started or completed (pair with events) |
| `shell_painted` | Chrome/skeleton visible |
| `network_started` | First network call for this flow |
| `backend_received` | FastAPI middleware accepted request |
| `authn_completed` | Principal resolved |
| `authz_completed` | Authorization check finished |
| `db_completed` | SQL work for request finished (aggregate) |
| `redis_completed` | Redis work for request finished (aggregate) |
| `service_completed` | Domain/service layer finished |
| `response_sent` | Response headers/body leaving server |
| `client_response_received` | Client received response |
| `store_updated` | Client store/repository committed new state |
| `content_rendered` | Meaningful content painted |
| `screen_interactive` | Primary controls usable |
| `background_reconcile_completed` | Soft refresh / SWR reconcile finished |
| `final_consistency_reached` | Source surface + Pulse + Activity (per product rules) agree |

---

## Common event names

| Event | When |
|-------|------|
| `flow_started` | Flow tracer begins |
| `shell_painted` | Shell/skeleton visible |
| `cache_read_started` | Cache lookup begins |
| `cache_read_completed` | Cache lookup ends (`cache_hit` set) |
| `network_started` | Outbound request begins |
| `network_completed` | Outbound request ends |
| `backend_completed` | Server finished (from headers/trace) |
| `store_updated` | Client state committed |
| `content_rendered` | Content paint |
| `screen_interactive` | Interactive |
| `background_reconcile_started` | Background refresh starts |
| `background_reconcile_completed` | Background refresh ends |
| `mutation_started` | Create/edit/delete begins |
| `optimistic_update_applied` | Optimistic UI applied |
| `mutation_committed` | Server ack success |
| `mutation_failed` | Server/client failure |
| `rollback_applied` | Optimistic rollback |
| `pulse_refresh_started` | Pulse refresh begins |
| `pulse_refreshed` | Pulse refresh ends |
| `activity_refresh_started` | Activity refresh begins |
| `activity_refreshed` | Activity refresh ends |
| `projection_refresh_started` | Projection rebuild/invalidate starts |
| `projection_refreshed` | Projection ready |
| `final_consistency_reached` | Consistency assertion passed |

---

## Mapping to parity span names

| Flow event / phase | Parity span alias (child) |
|--------------------|---------------------------|
| Bootstrap | `app.bootstrap` |
| Login → first pulse | `login.to_pulse` |
| Context switch | `context.switch` |
| Setup open/load/save | `setup.open`, `setup.load`, `setup.save` |
| Quick Add | `quick_add.open`, `quick_add.save` |
| Pulse | `pulse.load`, `pulse.refresh` |
| Life / Memory / Activity | `life.load`, `memory.load`, `activity.load` |
| Moment activate/complete/archive | `moment.activate`, `moment.complete`, `moment.archive` |
| Template loads | `template.*.load` |

Do not rename parity spans in a breaking way. New flow API wraps them.

---

## Common metadata

| Field | Notes |
|-------|-------|
| `platform` | `web` \| `android` \| `ios` \| `backend` |
| `app_version` | Client version string |
| `build_type` | `debug` \| `release` \| `ci` |
| `environment` | `local` \| `staging` \| `production` |
| `context` | `PERSONAL` \| `GROUP` \| `BUSINESS` \| `CIRCLE` |
| `screen` | Stable screen id (not free text) |
| `flow` | Stable flow id (e.g. `setup.resume`, `quick_add.expense`) |
| `template` | Template / moment type code |
| `moment_id_hash` | Non-reversible hash; **not** raw UUID |
| `workspace_id_hash` | Non-reversible hash; **not** raw UUID |
| `request_id` | Per HTTP call |
| `correlation_id` | Per logical user action / flow |
| `operation_name` | GraphQL op or REST operation label |
| `route` | Route **template** (no raw IDs in path) |
| `cache_hit` | boolean |
| `cache_layer` | `memory` \| `disk` \| `redis` \| `none` |
| `cold_warm_state` | `cold` \| `warm` \| `cached` |
| `network_type` | When available (`wifi`, `cellular`, `offline`, `unknown`) |
| `duration_ms` | number |
| `success` | boolean |
| `error_code` | Stable code; never message text with PII |
| `retry_count` | number |
| `response_size_bytes` | number |
| `render_count` | Where applicable |

### Identity hashing

When correlation by identity is required, use a stable non-reversible hash (e.g. SHA-256 truncated to 16 hex chars of `salt + id`). Never log full user / moment / workspace UUIDs in new flow metadata. Legacy parity spans may still carry opaque server IDs until migrated; new flow events must use hashes.

---

## Privacy — never log

- Names, emails, phone numbers
- Descriptions, notes
- Raw financial values
- Invitation links
- JWTs, Firebase tokens, refresh tokens
- Full user IDs
- Full moment / workspace IDs (use hashes)

See also unsafe list in [TELEMETRY_CONTRACT.md](../parity/TELEMETRY_CONTRACT.md).

---

## Correlation headers

| Header | Role |
|--------|------|
| `X-Correlation-ID` | Logical flow / user action; preserved across retries of the same action |
| `X-Request-ID` | Unique per network call (child of correlation) |
| `X-Duration-Ms` | Server total duration (response) |
| `X-Cache-Hit` | When meaningful |
| `Server-Timing` | Phase timings when available |

### Validation (server)

Accept only:

- UUID string, or
- `[A-Za-z0-9_-]{8,128}`

Invalid or overlong values are replaced with a newly minted ID. Do not trust arbitrary external IDs without validation.

---

## Client flow API (normative)

```text
startFlow(flow, metadata) → flowId
mark(flowId, event, metadata?)
measure(flowId, fromEvent, toEvent) → durationMs
attachRequest(flowId, requestId, correlationId)
completeFlow(flowId, metadata?)
failFlow(flowId, errorCode, metadata?)
exportDebugTrace(flowId) → JSON  // debug builds
```

Platform implementations:

- Web: `web/lib/telemetry/performanceTelemetry.ts`
- Android: `TelemetryStore` flow API
- iOS: `TelemetryStore` flow API

---

## Verdict language (reporting)

Use p50 / p75 / p95 / p99. Do **not** use average as the primary verdict.

Flow verdicts: `PASS` | `INVESTIGATE` | `FAIL` | `NOT MEASURED` | `DEVICE VERIFICATION REQUIRED`.

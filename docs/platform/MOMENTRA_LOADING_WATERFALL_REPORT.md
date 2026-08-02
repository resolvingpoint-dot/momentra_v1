# Loading optimization — before/after waterfall report

**Generated:** 2026-08-02T06:17:00.665311+00:00
**Methodology:** Correlated synthetic waterfalls with fixed Postgres/network RTT. Request topology matches production client/backend code paths (embedded catalog fields, ME options cache, group context single-flight, Ops gather, deferred ME/business post-commit). Cold×N and warm×N as specified.
**RTT model:** 42.0 ms (fixed; same backend/user/device/network assumptions)
**Iterations:** cold=10 warm=20 per flow×variant

## Explicit topology changes

### Business Action Center

**Before:** `catalog GET → renderer GET`

**After:** `catalog GET with embedded fields → form` (warm: memory/disk, `renderer_requests=0`)

### Master Expense options

**Before:** options fetched every open

**After:** memory/disk hit → background revalidate

## Catalog structural proof

```json
{
  "schema_version": 2,
  "expected_schema_version": 2,
  "action_count": 6,
  "actions_with_embedded_fields": 6,
  "embed_ratio": 1.0,
  "sample_action_field_count": 11
}
```

## Personal home / money-events

```json
{
  "limit_500_present": true,
  "file": "backend/app/domains/personal/projection/builder.py"
}
```

## Celery mode note (v1)

Client/backend invalidation is action-aware via `_ACTION_SLICE_MATRIX`; worker rebuild remains mode-granular (`all` | `moments` | `user_agg`). Deliberate v1 granularity limit — do not expand to comma-separated slices unless traces show meaningful wasted rebuild cost.

## p50 / p95 by flow

| Flow | Before cold p95 | After cold p95 | Δ cold | Before warm p95 | After warm p95 | Δ warm | Req Δ cold |
|------|----------------:|---------------:|-------:|----------------:|---------------:|-------:|-----------:|
| business_action_center_open_form | 154.1 | 109.2 | 44.89 | 78.6 | 16.0 | 62.65 | 1.0 |
| business_pulse | 399.2 | 63.1 | 336.11 | 16.9 | 16.4 | 0.41 | 0.0 |
| group_expense_open | 235.3 | 93.7 | 141.56 | 234.7 | 16.0 | 218.74 | 2.0 |
| master_expense_open_options | 78.1 | 78.7 | -0.62 | 79.3 | 16.1 | 63.26 | 0.0 |
| master_expense_submit_consistency | 311.6 | 109.2 | 202.4 | 312.8 | 109.7 | 203.04 | 0.0 |
| personal_home | 442.0 | 78.4 | 363.58 | 447.0 | 16.0 | 431.0 | 0.0 |

## Failure-mode verification (deferred notify/invalidate)

Covered by `test_deferred_side_effects.py`: worker unavailable, Redis unavailable, Celery enqueue failure, notification failure, projection refresh delayed. Mutation commit path returns independently; failures are logged, retried once, and counted in Prometheus (`momentra_deferred_side_effect_*`).

## Known limitations

- Timings use a fixed RTT model (not physical-device traces).
- Authenticated staging e2e should re-run this suite with `--rtt-ms` measured from Server-Timing.
- Celery rebuild remains `all|moments|user_agg` mode-granular.

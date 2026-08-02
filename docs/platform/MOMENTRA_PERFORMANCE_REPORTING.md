# Momentra Performance Reporting

**Status:** Reporting + CI gate contract  
**Related:** [Flow matrix](./MOMENTRA_LOADING_FLOW_MATRIX.md) · [Device verification](./MOMENTRA_LOADING_DEVICE_VERIFICATION.md)

## Artifact layout

```
artifacts/performance/
  latest-summary.json
  latest-summary.md
  platform-parity.json
  platform-parity.md
  platform-parity.csv
  flow-details/
  platform-comparison.csv
  regressions.json
  baselines/
    approved.json
  device/
    android-*.md
    ios-*.md
```

Generator: `backend/scripts/performance_report.py`

## Platform Parity Dashboard

Generated on every report run (`platform-parity.md`).

| Flow | Backend | Web | Android | iOS | Verdict |
|------|---------|-----|---------|-----|---------|

Verdict examples:

- `Pass` — all measured layers within expected band
- `Android issue` / `Web issue` / `iOS issue` — single-platform outlier
- `Backend issue` — server duration dominates
- `Projection delay` — elevated backend + all clients high (shared pipeline)
- `NOT MEASURED` / `INVESTIGATE`

Use this dashboard to decide whether an [optimization backlog](./MOMENTRA_LOADING_OPTIMIZATION_BACKLOG.md) item is backend, platform-specific, or shared.

## Summary matrix columns

| Flow | Web p95 | Android p95 | iOS p95 | Backend p95 | Requests | Final consistency | Verdict |

## Verdicts

| Verdict | Meaning |
|---------|---------|
| PASS | Within budget; no contract failures |
| INVESTIGATE | Near budget or incomplete layer attribution |
| FAIL | Over budget or consistency assertion failed |
| NOT MEASURED | Harness missing for that platform/mode |
| DEVICE VERIFICATION REQUIRED | Emulator/simulator only; needs physical device |

## Diagnosis categories

`BACKEND` · `DATABASE` · `REDIS` · `CELERY_QUEUE` · `PROJECTION` · `NETWORK` · `WEB_RENDER` · `ANDROID_CLIENT` · `IOS_CLIENT` · `CACHE_INVALIDATION` · `DUPLICATE_REQUEST` · `SEQUENTIAL_REQUESTS` · `STATE_RECONCILIATION` · `UNKNOWN`

Failing flows include a waterfall:

```
tap → shell → request → backend → response → store → render → Pulse → Activity → consistency
```

## Aggregation

Report **p50 / p75 / p95 / p99**. Never use average as the primary verdict. Split cold vs warm.

## CI gates

**Blocking**

- Duplicate request regressions (above baseline threshold)
- Contract / schema / correlation ID tests
- Performance event schema failures
- API request count regression above fixed threshold
- Backend benchmark regression beyond allowed tolerance
- GraphQL complexity/limit regressions
- Mutation consistency failures
- SDL / API contract regressions where applicable

**Non-blocking (warnings)**

- Device p95 / p99 until approved baselines exist

## Baseline approval

- Checked-in baseline: `artifacts/performance/baselines/approved.json` (or `backend/artifacts/performance/baselines/approved.json`)
- Updating a baseline requires an explicit PR review — **no automatic replace on regression**
- Reporter writes `regressions.json`; CI fails if regressions present and `--strict` is set

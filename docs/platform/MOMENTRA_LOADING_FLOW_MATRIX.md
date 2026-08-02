# Momentra Loading Flow Matrix

**Status:** Measurement matrix + budgets  
**Related:** [Performance contract](./MOMENTRA_LOADING_PERFORMANCE_CONTRACT.md) · [Audit](./MOMENTRA_LOADING_AUDIT.md)

Primary verdict metrics: **p50 / p75 / p95 / p99**. Never use average as the primary verdict.

Budget provenance:

- **Frozen** — copied from existing domain / platform docs; do not silently override
- **Provisional** — initial targets from this initiative where no frozen budget exists

---

## A. Empty states

| Flow id | Context | Measure |
|---------|---------|---------|
| `empty.personal` | PERSONAL | context select → shell → content → interactive; request count; cache; bootstrap size |
| `empty.group` | GROUP | same |
| `empty.business` | BUSINESS | same |
| `empty.circle` | CIRCLE | same where applicable |
| `empty.life` | * | Life empty |
| `empty.memory` | * | Memory empty |

---

## B. Setup

For Personal, Group, Business where applicable:

| Flow id | Measure |
|---------|---------|
| `setup.create` | create tap → Step 1 paint |
| `setup.resume` | resume → cached paint; resume → reconciled |
| `setup.continue` | Continue → next step interactive; duplicate PUT/GET detection |
| `setup.back` | back step |
| `setup.autosave` | keystroke → Saving → Saved |
| `setup.review` | Review open → preview visible |
| `setup.activate` | Activate → active moment visible |
| `setup.reopen_after_restart` | reopen after app restart |
| `setup.retry_failed_save` | retry after failed save |
| `setup.offline_recovery` | offline save recovery |

---

## C. Updated / active moments

| Flow id | Measure |
|---------|---------|
| `moment.active.personal` | tap → shell → selected content → interactive |
| `moment.active.group` | same |
| `moment.active.business` | same |
| `moment.switch` | moment switch + remount/request/cache |
| `context.switch` | context switch |
| `tab.switch` | selected-tab-only; off-tab fetch detection |
| `app.background_resume` | background/resume |
| `app.cold_relaunch` | cold |
| `app.warm_relaunch` | warm |

---

## D. Quick Add

| Flow id | Examples |
|---------|----------|
| `quick_add.personal.expense` | personal expense |
| `quick_add.personal.income` | income |
| `quick_add.experience` | experience |
| `quick_add.group.expense` | group expense |
| `quick_add.business.expense` | business expense |
| `quick_add.bill` | bill |
| `quick_add.goal_contribution` | goal |
| `quick_add.mood_activity` | mood/activity |
| `quick_add.other` | other supported actions |

Measure: FAB → action center → form → save → source update → Pulse → Activity → final consistency.

---

## E. Mutations

| Operation | Entity examples | Assertions |
|-----------|-----------------|------------|
| CREATE | transaction, expense, moment, member, goal/bill, business record | appears; totals; Pulse; Activity; relaunch; no duplicate |
| UPDATE | same | updates; old totals removed; new totals; no stale/duplicate |
| DELETE | same | disappears; totals; Pulse; Activity rules; no reappear; cache invalidate |
| MOMENT_DELETE | moment | inventory; selection fallback; Pulse clear; Home clear; setup cache; no ghost tabs |

See [MOMENTRA_MUTATION_CONSISTENCY.md](./MOMENTRA_MUTATION_CONSISTENCY.md).

---

## F. Realtime / eventual consistency

```
mutation_committed
→ domain_event_emitted
→ worker_enqueued
→ worker_started
→ projection_updated
→ redis_invalidated_or_refreshed
→ client_refetched_or_pushed
→ pulse_updated
→ activity_updated
→ final_consistency_reached
```

---

## Performance budgets

### Client experience

| Metric | Budget (p95) | Provenance |
|--------|--------------|------------|
| Cached shell paint | < 100 ms | **Frozen** (Business loading) |
| Empty-state first meaningful paint | < 300 ms | Provisional |
| Cached moment open | < 300 ms | Provisional |
| Network-backed moment open | < 800 ms | Provisional |
| Setup create → Step 1 | < 300 ms | Provisional (Business setup aims tighter locally; see setup docs) |
| Cached setup resume paint | < 500 ms | Provisional |
| Setup resume reconciled | < 1,000 ms | Provisional |
| Continue → next step interactive | < 500 ms | Provisional |
| Soft moments+overview (parallel) | < 200 ms | **Frozen** (Business/Group setup performance) |
| Quick Add open | < 200 ms | Provisional |
| Mutation → local visible (optimistic) | < 300 ms | Provisional |
| Save → final consistent | < 1,000 ms | Provisional |
| Delete → local disappearance (optimistic) | < 300 ms | Provisional |
| Pulse refresh after mutation | < 1,000 ms | Provisional |
| Activity refresh after mutation | < 1,000 ms | Provisional |
| Tab switch cached (client) | < 200 ms | **Frozen** (Phase 6.9) |

### Backend

| Metric | Budget (p95) | Provenance |
|--------|--------------|------------|
| Cached session/bootstrap | < 150 ms | Provisional (Personal prod target bootstrap p95 600 ms in PERFORMANCE_BUDGETS — use domain doc for Personal CI mocks) |
| Warm Pulse | < 150 ms | **Frozen** (Business/Group) |
| Warm Moments | < 200 ms | **Frozen** (Business/Group) |
| Warm Life / Memory | < 200 ms | **Frozen** (Business gate / Group report) |
| Home/session composition | < 250 ms | Provisional |
| Setup GET | < 250 ms | Provisional |
| Setup draft PUT | < 200 ms | Provisional |
| Mutation POST/PATCH/DELETE | < 300 ms | Provisional |
| GraphQL composed read | < 300 ms | Provisional |
| Redis operation | < 10 ms | Provisional (Group report cites hit < 20 ms) |
| Ordinary SQL query | preferably < 50 ms | Provisional |

### Personal CI mock ceilings (frozen smoke)

From [PERFORMANCE_BUDGETS.md](../PERFORMANCE_BUDGETS.md):

| Endpoint | Budget |
|----------|--------|
| GET personal/pulse | 500 ms |
| GET personal/session/bootstrap | 800 ms |
| GET quick-add options | 600 ms |

### Cold vs warm (Group freeze examples)

| Surface | Cold | Warm |
|---------|------|------|
| Pulse | < 1.5 s | < 150 ms |
| Moments | < 2.0 s | < 200 ms |

---

## Tracked aggregates (all flows)

- p50, p75, p95, p99
- error rate, timeout rate
- cold/warm split
- cache hit ratio
- request count, response size
- DB query count (when available)
- worker queue delay
- final consistency duration

---

## Journey scenario ids (automation)

| Id | Scenario |
|----|----------|
| 01 | personal empty state |
| 02 | group empty state |
| 03 | business empty state |
| 04 | create personal moment |
| 05 | resume personal setup |
| 06 | activate personal moment |
| 07 | create group experience |
| 08 | resume group setup |
| 09 | add group expense |
| 10 | create business moment |
| 11 | resume business setup |
| 12 | activate business moment |
| 13 | quick add personal expense |
| 14 | quick add group expense |
| 15 | quick add business expense |
| 16 | edit existing item |
| 17 | delete existing item |
| 18 | delete moment |
| 19 | switch context |
| 20 | switch moment |
| 21 | background resume |
| 22 | verify pulse refresh |
| 23 | verify activity refresh |
| 24 | verify final consistency |
| 25 | offline save and retry |
| 26 | slow network resume |
| 27 | expired session recovery |

Test modes: `cold` | `warm` | `cache_hit` | `cache_miss` | `slow_network` | `offline` | `retry` | `background_resume`.

Web: desktop + mobile viewport. Android/iOS: emulator/simulator for CI; physical device runs documented separately — never claim device performance from simulator results.

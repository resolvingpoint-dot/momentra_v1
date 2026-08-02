# Momentra Loading Optimization Backlog

**Status:** Evidence-gated optimization program  
**Prerequisite:** [Loading Verification Foundation](./MOMENTRA_LOADING_AUDIT.md) is complete.  
**Rule:** No optimization enters development without corresponding trace evidence.

Related:

- [Diagnostic findings](./MOMENTRA_LOADING_DIAGNOSTIC_FINDINGS.md)
- [Device verification / release gates](./MOMENTRA_LOADING_DEVICE_VERIFICATION.md)
- [Performance reporting / parity dashboard](./MOMENTRA_PERFORMANCE_REPORTING.md)
- [Flow matrix + budgets](./MOMENTRA_LOADING_FLOW_MATRIX.md)

---

## Program posture

| Area | Maturity |
|------|----------|
| Instrumentation | Complete |
| Reporting | Complete |
| Automation | ~90% (physical-device automation remains) |
| Optimization | Intentionally deferred until evidence |
| Performance verification | Awaiting device baselines + authenticated e2e |

Do **not** start another instrumentation or architecture phase. Collect traces → promote backlog items → fix only confirmed bottlenecks.

---

## Entry criteria for any optimization PR

1. Linked correlation ID(s) and/or journey artifact path
2. Platform Parity Dashboard row for the flow (Backend / Web / Android / iOS p95)
3. Diagnosis category from the contract (`SEQUENTIAL_REQUESTS`, `DUPLICATE_REQUEST`, …)
4. Frozen budgets consulted; provisional budgets marked if used
5. Explicit “evidence summary” in the PR description
6. No frozen loading-architecture change without FAIL waterfall + review

---

## Ranked backlog

Items stay **BLOCKED** until evidence is attached. Status values: `BLOCKED` · `EVIDENCE_READY` · `IN_PROGRESS` · `DONE` · `WONT_FIX`.

### P0 — confirm or clear before other client work

| ID | Item | Evidence required | Likely diagnosis | Status |
|----|------|-------------------|------------------|--------|
| OPT-P0-01 | Android Business soft bootstrap sequential moments + overview | Waterfall proving sequential independent requests for one soft refresh | `SEQUENTIAL_REQUESTS` / `ANDROID_CLIENT` | BLOCKED |
| OPT-P0-02 | Setup Continue duplicate PUT | Trace / duplicate-request counter showing two PUTs for one Continue | `DUPLICATE_REQUEST` | BLOCKED |
| OPT-P0-03 | Activate redundant preview GET | Trace showing preview fetch after fresh preview already held | `DUPLICATE_REQUEST` / `NETWORK` | BLOCKED |

### P1 — UX-critical paint paths

| ID | Item | Evidence required | Likely diagnosis | Status |
|----|------|-------------------|------------------|--------|
| OPT-P1-01 | Resume-from-cache paint over target | Resume p95 over budget; shell before network vs waiting on GET | `STATE_RECONCILIATION` / client cache | BLOCKED |
| OPT-P1-02 | Empty-state oversized bootstrap | Empty-state trace: request count / payload / duration over budget | `BACKEND` or client bootstrap | BLOCKED |
| OPT-P1-03 | Off-tab fetches on active moment | Request trace showing Life/Memory/Activity while another tab selected | `SEQUENTIAL_REQUESTS` / client | BLOCKED |
| OPT-P1-04 | Context / moment switch remount thrash | Remount count + duplicate fetches on switch | `WEB_RENDER` / `ANDROID_CLIENT` / `IOS_CLIENT` | BLOCKED |

### P2 — consistency after mutations

| ID | Item | Evidence required | Likely diagnosis | Status |
|----|------|-------------------|------------------|--------|
| OPT-P2-01 | Pulse convergence after mutation | `pulse_refreshed` − `mutation_committed` p95; projection/Celery delay | `PROJECTION` / `CELERY_QUEUE` / `CACHE_INVALIDATION` | BLOCKED |
| OPT-P2-02 | Activity convergence after mutation | Same for Activity; soft-delete semantics respected | `PROJECTION` / `STATE_RECONCILIATION` | BLOCKED |
| OPT-P2-03 | Deleted-moment ghost cache | Mutation consistency report: inventory/Pulse/Home/setup disk after moment delete | `CACHE_INVALIDATION` | BLOCKED |
| OPT-P2-04 | Final consistency across open surfaces | `final_consistency_reached` p95 after Quick Add / edit / delete | `STATE_RECONCILIATION` | BLOCKED |

### P3 — attribution / platform-specific

| ID | Item | Evidence required | Likely diagnosis | Status |
|----|------|-------------------|------------------|--------|
| OPT-P3-01 | Client render dominates despite fast backend | Client flow duration ≫ `X-Duration-Ms` on parity dashboard | platform `*_CLIENT` / `WEB_RENDER` | BLOCKED |
| OPT-P3-02 | Backend composition / DB dominates | Server-Timing db/redis/app dominates; staging gap documented | `DATABASE` / `BACKEND` / `REDIS` | BLOCKED |
| OPT-P3-03 | Platform outlier (one client slow, peers pass) | Parity dashboard row with single-platform FAIL | that platform | BLOCKED |

---

## How evidence is collected

1. Run [release-gating journeys](./MOMENTRA_LOADING_DEVICE_VERIFICATION.md#release-gating-journey-suite) on physical devices (and authenticated Web).
2. Export flow JSONL (or device run sheets) into `artifacts/performance/`.
3. Generate reports:

```bash
python backend/scripts/performance_report.py \
  --input artifacts/performance/run.jsonl \
  --out artifacts/performance \
  --baseline artifacts/performance/baselines/approved.json
```

4. Open `platform-parity.md` / `platform-parity.json`.
5. Promote matching backlog IDs from `BLOCKED` → `EVIDENCE_READY` with artifact links.
6. Only then open an optimization PR.

---

## Explicit non-goals (still enforced)

- No GraphQL read migration, broad prefetch, all-tab load, Redis/Celery replacement
- No fake performance data
- No automatic baseline replacement on regression
- No simulator/emulator numbers as physical-device proof
- No frozen-budget overwrite without measured evidence

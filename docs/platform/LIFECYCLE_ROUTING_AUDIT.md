# Lifecycle Routing Audit (Cross-Context)

**Sprint:** Momentra Cross-Context Lifecycle Stability  
**Status:** Part 0 complete — route matrix frozen before code changes  
**Date:** 2026-07-17  

## Status legend

| Tag | Meaning |
|-----|---------|
| CORRECT | Right context, route, and service path |
| WRONG_CONTEXT | Calls another context’s repository/route |
| WRONG_ROUTE | Wrong path or legacy store for this action |
| STALE_ID | Selection/cache keeps inaccessible/archived id |
| MISSING_PERMISSION | Capability/membership not enforced or undiagnosable |
| GENERIC_ERROR | Real error hidden behind “removed” / silent catch |
| DUPLICATE_REFRESH | Bootstrap/session refreshed more than once |
| MISSING_OPTIMISTIC_UPDATE | UI waits on network before inventory/selection change |
| BROKEN | End-to-end failure for real app moments |
| MISSING | Action not wired on this platform |

---

## Executive findings

1. **Group complete/archive are BROKEN** — clients call `POST /api/v1/group/moments/{id}/complete|archive`, served by legacy `group.py` → `GroupService` on `group_moments`, not app `moments`. Real Shared Experience/Purchase/Living IDs → 404 / wrong store.
2. **Business pause/resume bypass MomentEngine** — `PATCH` writes status only; pause skips bootstrap/projection side effects.
3. **Group pause/resume bypass MomentEngine** — same pattern via `group_app.patch_moment`.
4. **No WRONG_CONTEXT Business→Group or Personal→Group** in manage sheets (cleared).
5. **Optimistic lifecycle updates missing** on all three contexts × all clients.
6. **Duplicate bootstrap refresh** common (repo invalidate + home `refreshAfterManage`).
7. **Personal complete missing** on Android/iOS manage sheets (API exists).
8. **iOS RELATIONSHIPS archive** uses PATCH instead of template POST (works via engine, inconsistent).
9. **Business archive reselection STALE_ID** on Android/iOS (re-pins archived id after refresh).
10. **Typed lifecycle response / replacement_moment_id** not returned by current APIs.
11. **403 diagnostics** not structured (`event=MomentAccessDenied` missing).
12. **Canonical dedicated pause/resume POSTs** do not exist — clients use PATCH (compatible; coordinators should normalize).

---

## Canonical target routes

| Context | Activate | Pause | Resume | Complete | Archive |
|---------|----------|-------|--------|----------|---------|
| Personal | `POST …/personal/moments/{id}/setup` (setup commit) | `PATCH …/personal/moments/{id}` `{PAUSED}` *or* dedicated POST when added | `PATCH … ACTIVE` | `POST …/personal/templates/{type}/moments/{id}/complete` | `POST …/personal/templates/{type}/moments/{id}/archive` |
| Group | `POST …/group/setup/moments/{id}/activate` (+ shared-template activate) | `PATCH …/group/moments/{id}` | same | **Must** hit app store: `POST …/group/moments/{id}/complete` via **group_app** | same archive via **group_app** |
| Business | `POST …/business/moments/{id}/setup/activate` | `PATCH …/business/moments/{id}` | same | `POST …/business/moments/{id}/complete` | `POST …/business/moments/{id}/archive` |

---

## Backend route ownership (current)

| Prefix | First-registered router | Lifecycle coverage |
|--------|-------------------------|--------------------|
| `/api/v1/group` | `group_app` then `group` (legacy) | App: create, patch, setup activate. Legacy: activate/complete/archive on **group_moments** |
| `/api/v1/business` | `business_app` then `business` (legacy) | App: setup activate, patch, complete, archive. Legacy activate/complete/archive shadowed for overlapping paths |
| `/api/v1/personal` | `personal` | Setup activate, patch, template complete/archive |

---

## Matrix: Personal

| Action | Web | Android | iOS | Backend |
|--------|-----|---------|-----|---------|
| activate | CORRECT (setup) | CORRECT | CORRECT | CORRECT (`engine.activate`) |
| pause | CORRECT + DUPLICATE_REFRESH + MISSING_OPTIMISTIC + GENERIC_ERROR | same | same | CORRECT via `patch_moment` → engine |
| resume | same | same | same | CORRECT |
| complete | CORRECT + DUPLICATE_REFRESH + MISSING_OPTIMISTIC | **MISSING** (UI) | **MISSING** (UI) | CORRECT template POST |
| archive | CORRECT + flags | CORRECT + flags | **WRONG_ROUTE** RELATIONSHIPS (PATCH) + silent errors | CORRECT |

**UI entry:** `PersonalMomentManageSheet` → home shell callbacks → `PersonalRepository` / session API.  
**No cross-context calls.**

---

## Matrix: Group

| Action | Web | Android | iOS | Backend |
|--------|-----|---------|-----|---------|
| activate | CORRECT (setup / shared) | CORRECT | CORRECT | CORRECT app setup activate |
| pause | CORRECT route + MISSING_OPTIMISTIC + DUPLICATE_REFRESH | same | same + GENERIC_ERROR | CORRECT route; **no MomentEngine**; weak permission |
| resume | same | same | same | same |
| complete | **BROKEN / WRONG_ROUTE** (legacy store) | **BROKEN / WRONG_ROUTE** | **BROKEN / WRONG_ROUTE** + GENERIC_ERROR | **MISSING** on `group_app` (legacy only) |
| archive | **BROKEN / WRONG_ROUTE** | **BROKEN / WRONG_ROUTE** | **BROKEN / WRONG_ROUTE** | **MISSING** on `group_app` |

**UI entry:** Group home manage → `GroupRepository` / `GroupMomentManageViewModel` / `APIClient` group methods.  
**No Personal/Business calls from Group UI.**

---

## Matrix: Business

| Action | Web | Android | iOS | Backend |
|--------|-----|---------|-----|---------|
| activate | CORRECT | CORRECT | CORRECT | CORRECT (`engine.activate`) |
| pause | CORRECT client route; E2E **BROKEN** | same | same + GENERIC_ERROR | **BROKEN** — PATCH no engine / pause side effects |
| resume | same | same | same | **BROKEN** |
| complete | CORRECT + MISSING_OPTIMISTIC | CORRECT | CORRECT + GENERIC_ERROR | CORRECT |
| archive | CORRECT | **STALE_ID** reselection race | **STALE_ID** + GENERIC_ERROR | CORRECT |

**UI entry:** `MomentManageSheet` / `BusinessMomentManageSheet` → `BusinessRepository` / manage VM / `APIClient` business.  
**WRONG_CONTEXT Group imports: none.**

---

## End-to-end trace samples

### Group archive (broken path today)

| Step | Current |
|------|---------|
| UI | Group manage sheet Archive |
| Callback | home `onArchive` |
| Repository | `GroupRepository.archiveMoment` |
| Client | `POST api/v1/group/moments/{id}/archive` |
| Router | `group.py` (legacy) — **not** `group_app` |
| Service | `GroupService.archive_moment` → `group_moments` |
| MomentEngine | unused |
| Result | **404 / wrong store** for app moments |
| Status | **BROKEN / WRONG_ROUTE / STALE_ID** |

### Business archive (mostly correct; selection bug)

| Step | Current |
|------|---------|
| UI | Business manage Archive |
| Repository | `BusinessRepository.archiveMoment` |
| Client | `POST api/v1/business/moments/{id}/archive` |
| Router | `business_app.archive_moment` |
| Service | `BusinessSetupService.archive` → MomentEngine |
| Bootstrap | invalidated |
| Reselection | Web OK; Android/iOS can re-pin archived id |
| Status | Backend CORRECT; mobile **STALE_ID** |

### Personal pause

| Step | Current |
|------|---------|
| UI | Personal manage Pause |
| Repository | `patchMoment({status: PAUSED})` |
| Client | `PATCH api/v1/personal/moments/{id}` |
| Service | `PersonalAppService.patch_moment` → engine |
| Refresh | invalidate + `refreshAfterManage` (**DUPLICATE_REFRESH**) |
| Optimistic | none |
| Status | CORRECT path + flags |

---

## Shared manage sheets

| Platform | Shared shell | Context binding |
|----------|--------------|-----------------|
| Web | `MomentManageSheet` (+ Personal-specific sheet) | Context from home shell props — **must not infer from imported repo** |
| Android | `MomentManageSheet` | Personal / Group / Business wrappers pass callbacks |
| iOS | `MomentManageSheet` | theme + callbacks from home |

Risk: wrappers that import wrong repository — **audit found none** for Business→Group; Group complete still hits wrong **backend** store.

---

## Runtime vs lifecycle invalidation (current)

| Mutation class | Bootstrap reload today | Target |
|----------------|------------------------|--------|
| Runtime activity create/edit/delete | Sometimes over-invalidates on soft paths | **No** bootstrap; projection stale only |
| Lifecycle pause/resume/complete/archive/activate | Often **2×** bootstrap | **Exactly once** |

---

## Gaps vs sprint contract

| Contract item | Gap |
|---------------|-----|
| Typed lifecycle response + `replacement_moment_id` | Missing |
| `409 lifecycle_transition_invalid` | Partial / inconsistent |
| `event=MomentAccessDenied` | Missing |
| Dedicated pause/resume POSTs | Optional; PATCH acceptable with adapters |
| Group complete/archive on app moments | **Must add to group_app** (keep legacy routes for old store) |
| Cross-client lifecycle coordinator | Missing |
| Optimistic inventory update | Missing |
| Cursor rule + platform docs | Missing (`docs/platform/` empty before this sprint) |

---

## Implementation priority (post-audit)

1. **P0** — Group `group_app` complete/archive (+ pause/resume via MomentEngine) returning typed response  
2. **P0** — Business pause/resume via MomentEngine + side effects  
3. **P0** — Replacement selection + typed errors + access-denied logs  
4. **P0** — Web/Android/iOS coordinators + manage sheet wiring  
5. **P1** — Personal complete on mobile; iOS RELATIONSHIPS template archive  
6. **P1** — Deduplicate bootstrap refresh; stop 403 retry storms  
7. **P1** — Docs, Cursor rule, matrix tests  

**Code changes begin after this document.**

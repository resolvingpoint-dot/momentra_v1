# Momentra Mutation Consistency

**Status:** Cross-platform acceptance assertions  
**Related:** [Optimistic mutation contract](../parity/OPTIMISTIC_MUTATION_CONTRACT.md) · [Flow matrix](./MOMENTRA_LOADING_FLOW_MATRIX.md)

Do not invent product behavior. Activity deletion semantics below are derived from existing domain soft-delete contracts.

---

## After CREATE

- Source list contains exactly one new item (idempotent client keys respected)
- Totals update
- Pulse reflects new state (optimistic hint and/or refresh)
- Activity reflects event if product contract requires it
- Refresh preserves item
- Relaunch preserves item
- No duplicate item

## After UPDATE

- Item reflects new state
- Old totals removed; new totals applied
- No duplicate item
- Stale cache must not overwrite the update (generation / version guards)

## After DELETE (item)

- Item disappears locally (optimistic)
- Backend confirms deletion
- Item remains absent after refresh
- Totals update
- Pulse no longer includes it
- Activity follows deletion semantics (below)
- Selected state falls back safely when needed
- Caches invalidate correctly

## After MOMENT DELETE

- Inventory removes moment
- Selected moment changes safely (domain selection fallback)
- Active Pulse becomes null or fallback
- Home cards remove reference
- Activity behavior matches domain contract
- No ghost moment after relaunch
- Group/Business workspace state remains valid
- Setup draft disk cache for that moment is cleared

---

## Activity deletion semantics (documented from existing contracts)

| Domain | Behavior | Source |
|--------|----------|--------|
| Business Team Ops / Runway | Soft-delete when `is_deletable`; excluded from active lists | `TEAM_OPERATIONS_*`, ActivityEngine |
| Group expenses | Soft-delete; excluded from list / settlement active expenses | `GROUP_EXPENSE_CONSISTENCY_REPORT` |
| Personal Lifestyle | Soft delete on Activity view | `LIFESTYLE_V1_FREEZE` |

**Assertion rule:** After delete, Activity list must not show the soft-deleted row as an active editable item. Tombstone / history entries are allowed only if the domain contract already defines them — do not invent history UI.

Invalidation: projection caches for pulse/moments/quick_add are marked stale and refreshed via Celery (see Business cache invalidation matrix). Consistency measurement ends at `final_consistency_reached` when Pulse + source list + Activity (per domain) agree.

---

## Automated helpers

Backend: `backend/app/tests/acceptance/performance/mutation_assertions.py`  
Web: Vitest helpers under `web/lib/telemetry/`  
Android: extend guided setup / mutation unit tests  
iOS: XCTest flow tracer + mutation helpers when harness exists

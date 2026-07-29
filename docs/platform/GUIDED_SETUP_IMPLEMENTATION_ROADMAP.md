# Guided Setup — Implementation Roadmap

**Status:** Phase 0 freeze  
**Guardrail:** Presentation layer over existing engines — no fourth setup engine.

Related: [GUIDED_SETUP_UX.md](./GUIDED_SETUP_UX.md), [GUIDED_SETUP_SHELL_CONTRACT.md](./GUIDED_SETUP_SHELL_CONTRACT.md), [GUIDED_SETUP_EXTENSION_POINTS.md](./GUIDED_SETUP_EXTENSION_POINTS.md)

---

## Phase order

| Phase | Scope |
|-------|--------|
| **0** | Spec, catalogs, schema, validation, Cursor rule, parity matrix (this freeze) |
| **1** | Web Business (Team Ops, Runway, Ops) |
| **1.5** | Shared GuidedSetupShell hardening (controls, theme, summary, registry, analytics) |
| **2** | Web Group (SE, SP, SL) — **CLOSED** |
| **2→G3–G7** | [Group Native Parity](../group/GROUP_NATIVE_PARITY_ROADMAP.md): Android completion → iOS adapters → iOS completion → certification → legacy removal |
| **3** | Web Personal (Life Ops, Future Building, Lifestyle, Relationships) |
| **4** | Android Business |
| **5** | Android Group (platform-wide; Group E2E = Native Parity Phase 3) |
| **6** | Android Personal |
| **7** | iOS Business |
| **8** | iOS Group (adapters/completion = Native Parity Phases 4–5) |
| **9** | iOS Personal |
| **10** | Cross-platform parity, a11y, visual QA, legacy cleanup (Group legacy = Native Parity Phase 7) |

---

## Phase 0 — Spec / catalogs

**Files**

- `docs/platform/GUIDED_SETUP_UX.md`
- `docs/platform/GUIDED_SETUP_SHELL_CONTRACT.md`
- `docs/platform/guided_setup_catalog.schema.json`
- `docs/platform/GUIDED_SETUP_COPY_PARITY_MATRIX.md`
- `docs/platform/GUIDED_SETUP_IMPLEMENTATION_ROADMAP.md`
- `docs/business/business_setup_copy.json`
- `docs/group/group_setup_copy.json`
- `docs/personal/personal_setup_copy.json`
- `scripts/validate_guided_setup_catalogs.py`
- `scripts/test_validate_guided_setup_catalogs.py`
- `.cursor/rules/guided-setup-ux.mdc`

**Acceptance**

- Validation script exits 0  
- Catalog tests pass  
- No production setup screens changed  

**Build gate:** `python scripts/validate_guided_setup_catalogs.py` + pytest on catalog tests  

**Deprecation:** none yet  

---

## Phase 1 — Web Business

**Files (planned):** `web/components/setup/GuidedSetupShell.tsx`, Business template screens, `useBusinessSetupFlow`, catalog loader  

**Acceptance:** All three Business templates pass exit gates (first paint, no preview before Review, Continue flush, local summary, Review preview)  

**Build gate:** unit tests + manual QA checklist  

**Deprecation:** do not remove legacy until gates pass  

---

## Phase 1.5 — Shared GuidedSetupShell hardening (Web)

**Goals:** Convert GuidedSetupShell into a reusable platform component before Group migration.

**Delivered**

| Item | Location |
|------|----------|
| Shared controls | `web/components/setup/shared/` (Business re-exports under `business/setup/shared/`) |
| Setup theme | `GuidedSetupTheme.tsx` — Personal / Group / Business variants |
| Summary model | `guidedSetupSummary.ts` — `GuidedSetupSummary` + `guidedSummaryToRows` |
| Field registry | `SetupFieldRenderer.tsx` — `controlType` → shared control |
| Analytics hooks | `guidedSetupAnalytics.ts` + shell `onAnalytics` |
| A11y | Summary sheet focus + Escape; `motion-reduce`; activation subtitle prop |

**Still manual before Phase 2**

- Visual regression baselines (desktop / tablet / mobile × Team Ops / Runway / Ops)
- Full keyboard / SR / 200% zoom / landscape pass on shell
- Perf check: single mount, no duplicate autosave / preview, Continue = one flush

**Exit criteria**

- Shell has no Business template logic (Team Ops / Runway / Ops labels live in catalogs + builders)
- Shared controls under `components/setup/shared`
- Theme is context-driven
- Summary renderer is generic
- Field rendering is registry-based (available; templates may adopt incrementally)
- Business behavior unchanged (adapter + re-exports)
- Do **not** delete deprecated Business wrappers until Group has migrated

**Build gate:** `GuidedSetupShell` unit tests + Business smoke (open → Continue → Review)

---

## Phase 2 — Web Group

**Status:** CLOSED — Web Group Guided Setup COMPLETE (Phases 2A–2D)  

| Area | Status |
|------|--------|
| Web Group Guided Setup | COMPLETE |
| Legacy Group Setup | QUARANTINED (`web/components/group/setup/legacy/`) |
| Android Group Guided Setup | STARTED (adapters done; E2E gates open) |
| iOS Group Guided Setup | NOT STARTED |

**Current phase:** Native Guided Setup Parity  

**Files**

- `web/components/group/setup/experience/SharedExperienceSetup.tsx`
- `web/components/group/setup/purchase/SharedPurchaseSetup.tsx`
- `web/components/group/setup/living/SharedLivingSetup.tsx`
- `web/components/group/setup/shared/GroupSetupInviteSection.tsx`
- `web/components/group/setup/legacy/` (quarantined)
- Android: `SharedExperienceSetupScreen` / `SharedPurchaseSetupScreen` / `SharedLivingSetupScreen`
- `docs/group/GROUP_GUIDED_SETUP_IMPLEMENTATION.md` (project baseline)

**Acceptance (Web):** all three templates on GuidedSetupShell; legacy quarantined; catalog validation + tests  

**Group Native Parity track (after Phase 2):** see [`docs/group/GROUP_NATIVE_PARITY_ROADMAP.md`](../group/GROUP_NATIVE_PARITY_ROADMAP.md)

| Group Phase | Objective | Status |
|-------------|-----------|--------|
| **3** | Android platform completion | ACTIVE |
| **4** | iOS adapter migration | NOT STARTED |
| **5** | iOS platform completion | NOT STARTED |
| **6** | Cross-platform parity certification | NOT STARTED |
| **7** | Legacy removal | NOT STARTED |

> Group Phases 3–7 are distinct from platform-wide Phase 3 (Web Personal) below.

---

## Phase 3 — Web Personal

**Files:** Personal guided shell; flexible/optional steps; personal catalog  

**Acceptance:** No forced “People” filler; template-specific step 3 names  

---

## Phases 4–6 — Android (platform-wide Business → Group → Personal)

**Files:** `apk_copy/.../ui/setup/GuidedSetupShell.kt`, assets catalogs, Business → Group → Personal  

**Acceptance:** Same behavioral contract; seed/skip-GET and preview-on-Review preserved  

**Group track:** Adapter cutover done. Remaining Group work is **Group Native Parity Phase 3** (platform completion) in [`GROUP_NATIVE_PARITY_ROADMAP.md`](../group/GROUP_NATIVE_PARITY_ROADMAP.md).

---

## Phases 7–9 — iOS (platform-wide)

**Files:** `ios_copy/.../Setup/GuidedSetupShell.swift`, bundled catalogs, Business → Group → Personal  

**Acceptance:** MainActor / create-seed rules preserved; same step order and copy  

**Group track:** Starts after Android Group COMPLETE — Group Native Parity Phases 4–5.

---

## Phase 10 — Parity & legacy cleanup

**Files:** parity matrix updates, a11y audits, removal of quarantined shells  

**Acceptance:** Matrix rows `PARITY_VERIFIED`; Group legacy delete is **Group Native Parity Phase 7** (only after Web + Android + iOS Group COMPLETE).

---

## Shared exit gates (Phases 1–9)

See [GUIDED_SETUP_UX.md](./GUIDED_SETUP_UX.md) exit gates. Backend field keys unchanged throughout.

# Guided Setup — Parity & Legacy Quarantine

**Status:** Phase 6 checklist  
**Related:** [GUIDED_SETUP_UX.md](./GUIDED_SETUP_UX.md), [GUIDED_SETUP_SHELL_CONTRACT.md](./GUIDED_SETUP_SHELL_CONTRACT.md)

## Active production path

| Context | Web | Android | iOS |
|---------|-----|---------|-----|
| Business Team / Runway / Ops | `GuidedSetupShell` via `BusinessSetupShell` adapter + template screens | `ui/setup/GuidedSetupShell` + template screens | `Setup/GuidedSetupShell` + template views |
| Group SE / SP / SL | `Shared*Setup` → `GuidedSetupShell` | `GroupMomentSetupScreen` | `GroupMomentSetupView` |
| Personal | `PersonalMomentSetup` → `GuidedSetupShell` (`layout="singleScroll"`) | `PersonalMomentSetupScreen` (`singleScroll=true`) | `PersonalMomentSetupView` (`singleScroll: true`) |

Home routers must open the paths above. Personal is single-scroll by design (screen specs under `docs/screens/personal/**/setup`). Group / Business must not fall back to quarantined multi-screen legacy shells.

## Quarantined (do not route in production)

| Path | Notes |
|------|-------|
| `web/components/group/setup/shared/GroupSetupShell.tsx` | Legacy chrome for create-wizard demos |
| `web/components/group/setup/experience/ExperienceSetup.tsx` | Alternate create flow — not home setup reopen |
| `web/components/group/setup/purchase/PurchaseSetup.tsx` | Same |
| `web/components/group/setup/living/LivingSetup.tsx` | Same |
| `web/components/business/setup/BusinessMomentSetup.tsx` | Generic placeholder; prefer typed templates |
| Android/iOS `BusinessSetupShell` placeholders | Prefer typed Team/Runway/Ops screens |

Add `@deprecated` / file header when touching these. Prefer deletion only after no imports from home routers.

## Exit gates (verify per template)

- [ ] First step paints without blocking preview
- [ ] No `POST …/preview` before Review
- [ ] Autosave shows dirty / saving / saved / error
- [ ] Continue flushes pending draft before advance
- [ ] Resume restores step
- [ ] No technical enum labels; no “minor units” wording
- [ ] Large lists: suggested chips + searchable picker
- [ ] Live summary local-only
- [ ] Review uses server preview; Activate field-aware
- [ ] Footer never covers content; keyboard / SR nav
- [ ] Same step order + catalog copy across platforms
- [ ] Backend field keys unchanged

## Catalog validation

```bash
python scripts/validate_setup_catalogs.py
```

Keep `docs/**/ *_setup_copy.json` synced to web/lib, Android assets, and iOS Setup/Catalogs.

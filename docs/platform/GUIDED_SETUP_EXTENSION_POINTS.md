# GuidedSetupShell — extension points (Phase 1.5)

## Import map

| Need | Import |
|------|--------|
| Shell | `@/components/setup/GuidedSetupShell` |
| Shared controls | `@/components/setup/shared` |
| Field registry | `@/components/setup/SetupFieldRenderer` |
| Theme | `@/components/setup/GuidedSetupTheme` |
| Summary model | `@/components/setup/guidedSetupSummary` |
| Analytics | `@/components/setup/guidedSetupAnalytics` |

Business templates may still import `@/components/business/setup/shared/*` (thin re-exports). Prefer `@/components/setup/shared` for new code. Do not delete Business re-exports until Group migration is done.

## Adding a context (Group / Personal)

1. Pass `contextType="group" | "personal"` into `GuidedSetupShell`.
2. Map draft → `GuidedSetupSummary` (see `buildBusinessLiveSummaryModel`).
3. Render fields via `SetupFieldRenderer` or direct shared controls.
4. Wire `onAnalytics` with `emitGuidedSetupAnalytics` → `MomentraAnalytics`.

## Field registry

```tsx
<SetupFieldRenderer
  control="choice_cards"
  label="…"
  value={…}
  options={…}
  onChange={…}
/>
```

Unsupported in registry (template-owned): `date`, `invite`, `multi_chips`.

## Theme tokens

`accentColor`, `surface`, `selectedCard`, `selectedChip`, `summaryAccent`, `illustrationTint` — resolved from context + `useThemeTokens()`.

## Analytics events (shell)

`setup_open`, `step_changed`, `autosave_*` (from `saveState`), `review_opened`, `activation_started` (on Activate). Emit `activation_completed` / `activation_failed` from the parent after the engine responds.

# GuidedSetupShell contract

**Status:** Canonical — Phase 0 freeze  
Behavioral contract for Web, Android, and iOS. Prop names may map per language; **semantics must match**.

Related: [GUIDED_SETUP_UX.md](./GUIDED_SETUP_UX.md)

---

## Required shell inputs

| Input | Role |
|-------|------|
| `contextType` | `personal` \| `group` \| `business` |
| `templateId` | Presentation template id (e.g. `team_ops`, `shared_experience`, `life_operations`) |
| `momentTypeCode` | Backend moment type code |
| `momentId` | Active moment id |
| `title` | Header title |
| `subtitle` | Header subtitle |
| `estimatedDuration` | Minutes (number) |
| `layout` / `singleScroll` | Optional. Web: `layout="singleScroll"`; native: `singleScroll=true`. Hides step nav and “Step N of M”. **Personal only.** |
| `steps` | Visible `GuidedSetupStep[]` after `hidden_when` (personal single-scroll may pass a single synthetic step) |
| `currentStep` | 1-based index into **visible** steps |
| `saveState` | `idle` \| `dirty` \| `saving` \| `saved` \| `error` |
| `liveSummary` | Local key/value rows for summary panel |
| `contextHelp` | Tip / help for current step |
| `canGoBack` | Footer Back enabled |
| `canContinue` | Footer Continue enabled (non-Review guided flows) |
| `canActivate` | Activate enabled when engine says ready (Review or personal single-scroll) |
| `onBack` | Go to previous step |
| `onContinue` | Flush → validate → advance (guided) or activate (personal single-scroll on Android/iOS primary) |
| `onClose` | Dismiss setup |
| `onRetrySave` | Retry failed autosave |
| `onOpenSummary` | Open summary sheet (phone / tablet); Android may wire Preview refresh here |
| `onActivate` | Activate (Web Review / personal single-scroll) |
| `content` | Main step body (platform view slot) |

Optional but recommended:

| Input | Role |
|-------|------|
| `canPreview` | True on Review (guided) or always on personal single-scroll |
| `onPreview` | Explicit refresh preview |
| `footerPrimaryLabel` | Continue / Activate CTA |
| `footerSecondaryAction` | Preview |

Personal single-scroll: debounced preview on answer change is allowed; Group/Business keep preview on Review only.

---

## Step model

Catalog / shell step (JSON uses snake_case; TS may use camelCase aliases):

```json
{
  "id": "basics",
  "title": "Team basics",
  "short_title": "Basics",
  "description": "Tell us what this team does.",
  "optional": false,
  "hidden_when": null
}
```

```ts
type GuidedSetupStep = {
  id: string
  title: string
  shortTitle: string // alias of short_title
  description: string
  optional?: boolean
  hiddenWhen?: string | null
}
```

- Maximum **four** visible stages.
- Evaluate `hidden_when` against local draft answers before rendering nav.

---

## Step visual states

`incomplete` · `current` · `complete` · `warning` · `blocked`

---

## Save states

`idle` · `dirty` · `saving` · `saved` · `error`

---

## Continue behavior (mandatory)

1. Cancel pending debounce  
2. Flush draft save  
3. Validate current step (existing engine / client — **not** catalog)  
4. Show field errors  
5. Advance only when current step is valid and save has settled (unless draft already persisted)

---

## Review behavior (mandatory)

1. Flush draft  
2. Call server preview  
3. Render `blocking_errors`  
4. Render `warnings`  
5. Activate only when `activation_ready === true`

**Steps before Review must never call preview.**

---

## Live summary

- Local draft only  
- Never calls preview  
- Never gates Continue or field interaction  

---

## Layout zones

Header · step nav · main · summary (desktop right / mobile sheet) · sticky footer.

Footer never covers content (padding + safe-area insets).

### Responsive

| Viewport | Behavior |
|----------|----------|
| ≥1024 | Left nav · main · right summary · sticky footer |
| Tablet | Horizontal chips · main · collapsible summary |
| Phone | Scrollable chips · one column · summary sheet via `onOpenSummary` · sticky footer |

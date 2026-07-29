# Guided Setup UX

**Status:** Canonical — Phase 0 freeze  
**Guardrail:** One guided **presentation** system over existing setup engines. Not a new setup engine.

```
Backend contract
→ existing setup flow (VMs / repos / APIs)
→ guided presentation layer (shell + catalogs)
```

Related:

- [GUIDED_SETUP_SHELL_CONTRACT.md](./GUIDED_SETUP_SHELL_CONTRACT.md)
- [GUIDED_SETUP_EXTENSION_POINTS.md](./GUIDED_SETUP_EXTENSION_POINTS.md)
- [guided_setup_catalog.schema.json](./guided_setup_catalog.schema.json)
- [GUIDED_SETUP_COPY_PARITY_MATRIX.md](./GUIDED_SETUP_COPY_PARITY_MATRIX.md)
- [GUIDED_SETUP_IMPLEMENTATION_ROADMAP.md](./GUIDED_SETUP_IMPLEMENTATION_ROADMAP.md)
- [BUSINESS_SETUP_GUIDED_UX.md](../business/BUSINESS_SETUP_GUIDED_UX.md)

---

## 1. Product goal

Replace long technical setup forms with guided onboarding across Personal, Group, and Business on Web, Android, and iOS—same step order, copy, controls, autosave, live summary, and Review preview behavior; native shells per platform.

## 2. Behavioral principles

1. **Backend is authoritative** for field keys, validation, required fields, activation readiness, permissions, and lifecycle.
2. **Catalogs are presentation only** — labels, helpers, placeholders, icons, control styles, option display text, explainers, tips, summary labels, display defaults, character-limit display.
3. **At most four** visible stages; rename or omit via catalog — never empty filler screens.
4. **Live summary is local** — never blocks, never calls preview.
5. **Continue flushes** pending autosave before validate/advance.
6. **Preview only on Review** — steps before Review never `POST …/preview`.
7. **No chip walls** for currency / country / locale / timezone — suggested chips + searchable picker.
8. **No raw enums, snake_case, or “minor units”** in user-facing copy.
9. **Native UI** per platform; shared contract and catalogs.

## 3. Shared four-stage setup pattern

Typical shape (titles vary by template):

1. Basics  
2. Configuration / preferences / money  
3. People / supporting details (optional or renamed)  
4. Review and activate  

## 4. Optional / renamed step behavior

```ts
type GuidedSetupStep = {
  id: string
  title: string
  short_title: string
  description: string
  optional?: boolean
  hidden_when?: string | null  // evaluated against local draft answers
}
```

- Visible steps = catalog steps after `hidden_when`.
- Personal may omit or rename step 3 (habits, priorities, lifestyle, relationship context) instead of forcing “People”.
- Step nav titles always come from the template step list.

## 5. Header

- Product/setup title  
- Optional subtitle  
- Step N of M  
- Estimated duration (e.g. “About 3 minutes”)  
- Close action  

## 6. Step navigation

- Uses `short_title` from each visible step  
- Visual states: `incomplete` · `current` · `complete` · `warning` · `blocked`  
- Desktop: vertical or left rail; tablet/phone: horizontal chips (scrollable on phone)

## 7. Main content

- One step’s fields at a time  
- Conversational labels, helpers, tips, explainers (`?`), examples, character counters  
- Control mapping per § Part 4 / Control strategy below  

## 8. Live summary

- Right panel (desktop) or sheet (phone)  
- **Fully local** draft values already entered  
- No preview, no server validation, no aggregates, no loading gate  
- Never blocks editing or Continue  

## 9. Context help

- Step description + optional tip / help from catalog `tips`  
- Jargon fields use explainer title + body  

## 10. Sticky footer

- Back · autosave status · Continue (or Activate on Review)  
- Optional Preview secondary on Review only  
- Footer never covers the last field (content padding + safe-area)  

## 11. Autosave

```
Edit → debounced autosave
saveState: idle → dirty → saving → saved | error
```

- Visible status in footer  
- Error offers Retry (`onRetrySave`)  

## 12. Continue behavior

```
1. Cancel pending debounce
2. Flush draft save immediately
3. Validate current step (engine / existing client rules — not catalog)
4. Show field errors
5. Advance only when current step is valid and save settled (or already persisted)
```

## 13. Review and preview

| Steps | Behavior |
|-------|----------|
| Before Review | Local live summary only; **no** preview |
| Review | Flush draft → `POST preview` → `blocking_errors` / `warnings` → Activate iff `activation_ready` |

Shell: `canPreview` / preview actions only on Review.

## 14. Invite behavior

- Member / participant step uses member picker + invite channel sheet  
- Channels (presentation): QR · WhatsApp · Message · Email · Copy link  
- Backend invite contracts unchanged  

## 15. Field explanations

- Helper under label for plain language  
- Explainer (`?`) for jargon (e.g. collection rate, vendor dependency)  
- Examples in placeholders where helpful  

## 16. Responsive layout

| Breakpoint | Layout |
|------------|--------|
| Desktop ≥1024 | Left step nav · main · right live summary · sticky footer |
| Tablet | Horizontal step chips · main · collapsible summary |
| Phone | Horizontal scrollable chips · one-column · summary bottom sheet / expandable · sticky footer + safe-area |

## 17. Accessibility

- Keyboard: focus order header → nav → fields → footer  
- Screen reader: step current announced; save status `aria-live`; errors associated with fields  
- Targets ≥44×44 where native HIG/Material require  
- Do not rely on color alone for step/save state  

## 18. Error states

- Field errors on Continue validation  
- Save error in footer with Retry  
- Review: blocking errors from preview; warnings non-blocking  
- Load failure: recoverable message + close/back  

## 19. Resume behavior

- Restore exact `current_step` from setup progress / draft  
- Restore answers; do not force preview until Review  

## 20. Legacy path deprecation

After a context’s guided path is production-routed and gated:

- Quarantine duplicate shells  
- Remove preview-on-keystroke for **Group / Business** guided flows  
- Retire hard-coded copy constants in favor of catalogs  

### Personal single-scroll (intentional)

Personal setups are **not** multi-step guided wizards. They use `GuidedSetupShell` in single-scroll layout (Web `layout="singleScroll"`, native `singleScroll=true`): all fields, live preview, and activate on one page. Specs: `docs/screens/personal/01_life operations/01_setup`, `02_future building/01_setup`, `03_lifesytle/00_setup`, `04_relastionships/00_setup`. Group and Business remain guided multi-step.

Do **not** delete Group/Business legacy until routing + tests prove the new shell is active (see roadmap).

## 21. Non-goals

- Redesign active dashboards  
- Change backend field keys  
- New setup engine or MomentEngine changes  
- New moment types  
- Chip walls for currency/locale/country/timezone  
- Catalog-defined validation or activation rules  

---

## Authority split (locked)

| Backend / engine | Catalogs |
|------------------|----------|
| Field keys | Labels |
| Validation | Helpers / placeholders |
| Required fields | Icons / control style |
| Activation readiness | Option **display** labels |
| Permissions / lifecycle | Explainers, tips, summary labels, display defaults |

Runtime form schema remains existing contracts / adapters.

---

## Control strategy (canonical)

| Field type | Control |
|------------|---------|
| 2–7 single-choice | chips or visual cards |
| 2–8 multi-choice | multi-select chips/cards |
| Large option list | searchable picker |
| Currency | suggested chips + searchable picker |
| Country / locale / timezone | searchable picker (optional suggested chips) |
| Money | localized **major-unit** input (never “minor units” in UI) |
| Percentage | suggested chips + numeric / slider |
| Boolean dependency | switch + conditional reveal |
| Member | member picker + invite sheet |
| Date | native date picker |
| Long text | textarea + character counter |
| Jargon | explainer + helper |

Never expose: raw enum labels, snake_case labels, “minor units”, backend-only terminology.

---

## Exit gates (every migrated flow — later phases)

First step paints immediately; no preview before Review; visible autosave; Continue flushes; resume restores step; no enum/minor-units wording; searchable large lists; local live summary; invite works; Review uses server preview; footer never covers content; a11y; same copy/step order cross-platform; field keys unchanged.

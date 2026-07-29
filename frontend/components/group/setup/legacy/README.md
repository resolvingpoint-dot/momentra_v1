# Group setup legacy quarantine (Phase 2D)

These modules are **not** used by production Group create/resume routing.

Production path:

- `GroupTripSetup` → `SharedExperienceSetup`
- `GroupPurchaseSetup` → `SharedPurchaseSetup`
- `GroupLivingSetup` → `SharedLivingSetup`
- shared invite: `../shared/GroupSetupInviteSection.tsx`

Contents here:

| Path | Role |
|------|------|
| `GroupMomentSetup.tsx` | Former generic GuidedSetupShell adapter |
| `experience/*` | Legacy Experience create wizard (`GroupSetupShell`) |
| `purchase/*` | Legacy Purchase create wizard |
| `living/*` | Legacy Living create wizard |
| `shared/GroupSetupShell.tsx` | Legacy wizard chrome |
| `shared/GroupSetupStepIndicator.tsx` | Legacy step dots |

Do not import these from `GroupHomePlaceholder` or new guided adapters.
Safe to delete in a later cleanup once Android/iOS parity no longer references the patterns for archaeology.

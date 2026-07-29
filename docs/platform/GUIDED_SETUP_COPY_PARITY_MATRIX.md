# Guided Setup — Copy Parity Matrix

**Status:** Phase 0 — SPEC_READY (Business / Personal) · Phase 2A–2D Web Group CLOSED · Native Group parity NOT STARTED  
**Purpose:** Track catalog-backed copy and step order across Web, Android, and iOS.

Update status during platform phases: `SPEC_READY` → `IN_PROGRESS` → `IMPLEMENTED` → `PARITY_VERIFIED`.

Catalog sources:

| Context | Catalog |
|---------|---------|
| Business | `docs/business/business_setup_copy.json` |
| Group | `docs/group/group_setup_copy.json` |
| Personal | `docs/personal/personal_setup_copy.json` |

Schema: `docs/platform/guided_setup_catalog.schema.json`

---

## Matrix

| Context | Template | Step | Web | Android | iOS | Catalog source | Status |
|---------|----------|------|-----|---------|-----|----------------|--------|
| Business | team_ops | Team basics | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | team_ops | How the team works | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | team_ops | People and roles | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | team_ops | Review and activate | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_runway | Runway basics | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_runway | Financial picture | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_runway | People and governance | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_runway | Review and activate | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_operations | Operations basics | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_operations | Budget and monitoring | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_operations | People and approvals | — | — | — | business_setup_copy.json | SPEC_READY |
| Business | business_operations | Review and activate | — | — | — | business_setup_copy.json | SPEC_READY |
| Group | shared_experience | Experience basics | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_experience | Dates, place, and money | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_experience | Participants and invitations | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_experience | Review and activate | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_purchase | Purchase basics | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_purchase | Goal, amount, and contribution rules | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_purchase | Members and ownership | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_purchase | Review and activate | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_living | Home basics | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_living | Budget, responsibilities, and preferences | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_living | Members and roles | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Group | shared_living | Review and activate | ✓ | ◐ | — | group_setup_copy.json | WEB_COMPLETE · ANDROID_STARTED |
| Personal | life_operations | Moment basics | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | life_operations | Preferences and goals | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | life_operations | Habits and recovery | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | life_operations | Review and activate | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | future_building | Building basics | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | future_building | Preferences and goals | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | future_building | Momentum and outlook | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | future_building | Review and activate | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | lifestyle | Lifestyle basics | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | lifestyle | Preferences and balance | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | lifestyle | Priorities and focus | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | lifestyle | Review and activate | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | relationships | Relationship basics | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | relationships | People and circles | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | relationships | Strengths and investment | — | — | — | personal_setup_copy.json | SPEC_READY |
| Personal | relationships | Review and activate | — | — | — | personal_setup_copy.json | SPEC_READY |

**Legend (Web / Android / iOS columns):** `—` = not implemented against this catalog yet; check mark when platform ships guided shell for that step.

**Initial status:** SPEC_READY / NOT_IMPLEMENTED for all platform cells.

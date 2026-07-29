# GraphQL Schema Changelog

## 2026-07-29 — `f5c460508117`

- checksum: `f5c4605081178ad7a11a3e24366022e4ce95503b382fdb027ff5826678d47f72`
- previous: `a080102cf8c2269654fa870efcabb2927a0382489bb6b64c8fcef1242fbc5076`
- notes: Business Home — `businessHome` (REST `/business/moments/home`)

## 2026-07-29 — `a080102cf8c2`

- checksum: `a080102cf8c2269654fa870efcabb2927a0382489bb6b64c8fcef1242fbc5076`
- previous: `4eb82b9db4dc7e3069936d053af35f9ebd26b370ca6ea200ce7d9db5eb31d4fa`
- notes: Group Home — `groupHome` → type cards + how-it-works (REST `/group/moments/home`)

## 2026-07-29 — `4eb82b9db4dc`

- checksum: `4eb82b9db4dc7e3069936d053af35f9ebd26b370ca6ea200ce7d9db5eb31d4fa`
- previous: `8c1868543a83894dcf6fc021083864df7913535a73702a11ffca80f9b7511d4e`
- notes: Personal Home — `personalHome` → cards + template detail JSON (REST `/personal/moments/home`)

## 2026-07-29 — `8c1868543a83`

- checksum: `8c1868543a83894dcf6fc021083864df7913535a73702a11ffca80f9b7511d4e`
- previous: `f60c363c3dbff024c63a0322e65ded4fdceb6a38886085c0296dbff266b51bd5`
- notes: Unified Activity — `activity(scope)` → `PersonalActivityFeed` | `GroupActivityFeed` | `BusinessActivityFeed`

## 2026-07-29 — `f60c363c3dbf`

- checksum: `f60c363c3dbff024c63a0322e65ded4fdceb6a38886085c0296dbff266b51bd5`
- previous: `af0d5c9163f47a056fb63879800f68d1b1e2d5f053306e359fec05f7f1937d70`
- notes: Active Pulse — `pulse(scope, momentId)` → `GroupActivePulse` | `BusinessActivePulse` (typed KPI shell + JSON payload)

## 2026-07-29 — `af0d5c9163f4`

- checksum: `af0d5c9163f47a056fb63879800f68d1b1e2d5f053306e359fec05f7f1937d70`
- previous: `19325f6ad6f2d6316014291fe2c96fdaea6b2d599b5808345fa520ad39900ead`
- notes: Phase 3 Pulse landings — `pulse(scope)` → `PersonalPulse` | `GroupPulse` | `BusinessPulse`

## 2026-07-29 — `19325f6ad6f2`

- checksum: `19325f6ad6f2d6316014291fe2c96fdaea6b2d599b5808345fa520ad39900ead`
- previous: `none`
- notes: Phase 2.5 baseline (`Query.health`, `Query.groupMoment`, cursor helpers)

Changelog entries are appended by `backend/scripts/export_graphql_schema.py` when the SDL changes.

# GraphQL client codegen (Momentra)

## Artifacts

| File | Purpose |
|------|---------|
| [`backend/app/api/graphql/schema.graphql`](../../../backend/app/api/graphql/schema.graphql) | Committed SDL snapshot |
| [`backend/app/api/graphql/schema.meta.json`](../../../backend/app/api/graphql/schema.meta.json) | `version`, `checksum_sha256` |
| [`SCHEMA_CHANGELOG.md`](./SCHEMA_CHANGELOG.md) | Human changelog on SDL drift |
| [`examples/`](./examples/) | Shared operations for Web / Android / iOS |

Export / refresh snapshot:

```bash
cd backend
python scripts/export_graphql_schema.py
```

Bump `GRAPHQL_APQ_SCHEMA_VERSION` (config `graphql_apq_schema_version`) on **breaking** SDL deploys so Redis APQ hashes invalidate under `gql:apq:{version}:{sha256}`.

## TypeScript (Web)

Suggested GraphQL Code Generator config (place under `web/` when wiring CI):

```yaml
schema: ../backend/app/api/graphql/schema.graphql
documents: ../docs/platform/graphql/examples/**/*.graphql
generates:
  src/graphql/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
```

## Kotlin (Android)

Use Apollo Kotlin against the same SDL + `examples/*.graphql`. Point `schemaFile` / downloaded schema at `schema.graphql` and share operations from this folder.

## Swift (iOS)

Use Apollo iOS (or equivalent) with `schema.graphql` and the shared operation documents.

## Platform freeze

After Phase 2.5, new product queries are additive SDL changes only — regenerate checksum/changelog via the export script in the same PR.

# GraphQL conventions (Momentra Platform v2)

See also [ADR 0004](../adr/0004-graphql-read-platform.md) and [ADR 0005](../adr/0005-platform-feature-freeze.md).

## Mount

| Endpoint | Role |
|----------|------|
| `POST /graphql` | GraphQL HTTP (Bearer access token); rate-limited |
| GraphQL IDE | Enabled when `DEBUG=true`; disabled in production |

## Naming

- Fields: **camelCase** (`groupMoment`, `displayName`, `netAmount`)
- Types: **PascalCase** (`GroupMoment`, `GroupMomentMember`)
- IDs: GraphQL `ID` (string UUID)

## AuthN / AuthZ

- Same Momentra access token as REST
- Unauthenticated → GraphQL error with `extensions.code = "unauthenticated"`
- Missing / unauthorized group resources → `not_found` (IDOR-safe), matching [ADR 0003](../adr/0003-central-authz.md)
- Prefer declarative field AuthZ:

```python
@strawberry.field(extensions=[require_permission("group.moment.view")])
async def group_moment(...): ...
```

## Pagination

List fields that page use **cursor connections**:

```graphql
expenses(first: Int = 20, after: String): GroupExpenseConnection!
```

Connection shape:

- `edges { cursor node }`
- `nodes` (shortcut)
- `pageInfo { hasNextPage endCursor }`

`first` is capped by `GRAPHQL_MAX_PAGE_SIZE` (default 50). Cursors are opaque (base64 index tokens). Do not invent a second Redis cache for GraphQL pages.

## Nullability

- Root resource queries are nullable (`groupMoment: GroupMoment`)
- Non-null lists on a loaded parent: `members: [GroupMomentMember!]!`

## Deprecation

Use `@deprecated(reason: "...")` when removing or renaming fields; keep REST as source of truth for commands.

## Security limits

| Setting | Default | Purpose |
|---------|---------|---------|
| `GRAPHQL_MAX_DEPTH` | 8 | Selection depth |
| `GRAPHQL_MAX_COMPLEXITY` | 200 | Field selection count |
| `GRAPHQL_MAX_ALIASES` | 15 | Alias storm |
| `GRAPHQL_MAX_TOKENS` | 1000 | Parser budget |
| `GRAPHQL_MAX_OPERATIONS` | 1 | Ops per HTTP request |
| `GRAPHQL_MAX_NODES` | 500 | Sum of `first` args |
| `GRAPHQL_MAX_PAGE_SIZE` | 50 | Cap on `first` |
| `GRAPHQL_MAX_VARIABLE_BYTES` | 65536 | Variables JSON size |
| `GRAPHQL_MAX_BODY_BYTES` | 262144 | HTTP body size |
| `GRAPHQL_QUERY_TIMEOUT_MS` | 5000 | Execution timeout |
| `GRAPHQL_DISABLE_INTROSPECTION` | true | Hide `__schema` |
| `GRAPHQL_PERSISTED_ONLY` | false | Optional APQ-only mode |

## APQ

Automatic Persisted Queries store **SHA-256 → query document only** in Redis:

`gql:apq:{GRAPHQL_APQ_SCHEMA_VERSION}:{sha256}`

TTL: `GRAPHQL_APQ_TTL_SECONDS` (default 86400). Bump `GRAPHQL_APQ_SCHEMA_VERSION` on schema-breaking deploys to invalidate. Never cache full GraphQL JSON responses by hash.

## Observability

Structured log event `graphql_operation` plus Prometheus series (`momentra_graphql_*`). Response headers when available:

- `X-GraphQL-Operation`, `X-GraphQL-Complexity`, `X-GraphQL-Depth`, `X-GraphQL-Duration-Ms`, `X-GraphQL-APQ`

## Schema contracts

Committed artifacts (regenerate via `PYTHONPATH=backend python backend/scripts/export_graphql_schema.py`):

- `backend/app/api/graphql/schema.graphql` — SDL snapshot
- `backend/app/api/graphql/schema.meta.json` — checksum, version, APQ schema version
- [SCHEMA_CHANGELOG.md](./graphql/SCHEMA_CHANGELOG.md) — append-on-change

Contract tests detect removed fields, type changes, nullability relaxations, and enum value removals (`schema_compat.compare_sdl`).

## Resolvers

Orchestrate only. Call application / domain services. No direct SQL, no parallel AuthZ, no mutations. Platform is frozen after Phase 2.5 ([ADR 0005](../adr/0005-platform-feature-freeze.md)); new product queries reuse this stack additively.

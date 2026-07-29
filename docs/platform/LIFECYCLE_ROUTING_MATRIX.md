# Lifecycle Routing Matrix

Canonical client routes (post-sprint):

| Context | Activate | Pause / Resume | Complete | Archive |
|---------|----------|----------------|----------|---------|
| Personal | `POST /api/v1/personal/moments/{id}/setup` | `PATCH /api/v1/personal/moments/{id}` | `POST /api/v1/personal/templates/{type}/moments/{id}/complete` | `POST /api/v1/personal/templates/{type}/moments/{id}/archive` |
| Group | `POST /api/v1/group/setup/moments/{id}/activate` | `PATCH /api/v1/group/moments/{id}` | `POST /api/v1/group/moments/{id}/complete` (**group_app**) | `POST /api/v1/group/moments/{id}/archive` (**group_app**) |
| Business | `POST /api/v1/business/moments/{id}/setup/activate` | `PATCH /api/v1/business/moments/{id}` | `POST /api/v1/business/moments/{id}/complete` | `POST /api/v1/business/moments/{id}/archive` |

## Router precedence

- `group_app` registered before legacy `group` — app complete/archive shadow legacy `group_moments` routes.
- `business_app` registered before legacy `business`.

## Coordinators

| Platform | Module |
|----------|--------|
| Web | `web/lib/lifecycle/MomentLifecycleCoordinator.ts` |
| Android | `…/ui/shared/lifecycle/MomentLifecycleCoordinator.kt` |
| iOS | `…/Shared/lifecycle/MomentLifecycleCoordinator.swift` |

See audit: [LIFECYCLE_ROUTING_AUDIT.md](./LIFECYCLE_ROUTING_AUDIT.md).

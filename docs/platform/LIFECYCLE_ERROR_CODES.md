# Lifecycle Error Codes

| HTTP | Code | Meaning | User message |
|------|------|---------|--------------|
| 401 | (auth) | Unauthenticated | Sign in again |
| 403 | `moment_not_owned` / `membership_missing` / `membership_inactive` / `context_mismatch` / `capability_missing` / `moment_archived` / `moment_not_visible` / `stale_session_selection` / `permission_denied` | Authenticated but forbidden | You don’t have permission to change this moment. |
| 404 | `not_found` | True missing resource | This moment no longer exists. |
| 409 | `lifecycle_transition_invalid` | Illegal or already-applied transition | This moment has already changed state. Refreshing… |
| 422 | `validation_error` | Bad payload | Some lifecycle details are invalid. |
| — | network | Offline / transport | We couldn’t update this moment. Your current view has been restored. |

## Backend access denial log

`event=MomentAccessDenied` with: contextType, momentId, momentType, userHash, action, ownerMatch, membershipFound, membershipStatus, role, requiredCapability, denialReason.

Never log email, phone, token, or full payloads.

Do **not** map 403 → “item may have been removed.”

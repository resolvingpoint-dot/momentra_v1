# Lifecycle vs Runtime Refresh Rules

## Runtime activity (create / edit / delete)

- **No** bootstrap / session inventory reload  
- Invalidate only active projections for selected moment + tab  
- Optimistic current-screen update  
- Redis stale mark + Celery refresh  
- Do not call lifecycle coordinators  

## Lifecycle (activate / pause / resume / complete / archive)

- Refresh bootstrap / session inventory **exactly once**  
- Invalidate lifecycle-sensitive projections  
- Update selected moment (replacement rules)  
- Bump session generation; cancel in-flight reads for old moment  
- Do not wait for heavy projection rebuild before returning  

## After 403 / inaccessible selected moment

Active Pulse/Moments/Activity reads that return **403** (`invalid_member`, membership revoked, etc.):

1. **Stop retrying** that `momentId` (hide Retry; do not force-reload the same id)  
2. Remove the moment from **local inventory** immediately  
3. Clear `selectedMomentId` if it matched  
4. Pick replacement via selection rules (ACTIVE → PAUSED/COMPLETED → draft → none)  
5. Refresh session/bootstrap **once**  
6. If none remain → **EMPTY** / setup empty screens for that context  

Never leave the UI mounted on a forbidden stale moment showing “User is not a member…”.

Same rule for Personal, Group, and Business.

See: `handleBusinessMomentInaccessible` (Web), `BusinessSessionViewModel.handleMomentInaccessible` (Android), `BusinessSessionStore.handleMomentInaccessible` (iOS).

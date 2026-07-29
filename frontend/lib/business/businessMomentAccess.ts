/**
 * Detect inaccessible Business moment errors and reseat session selection.
 *
 * On 403 / membership / not-a-member: stop retrying that momentId, refresh
 * inventory once, clear invalid selection, pick replacement or empty.
 */
import { ApiError } from "@/lib/api/client";

const ACCESS_DENIED_RE =
  /403|401|permission|forbidden|not allowed|access denied|unauthorized|not a member|invalid_member|membership_missing|membership_inactive|moment_not_visible|stale_session/i;

export function isBusinessMomentAccessDenied(err: unknown): boolean {
  if (err instanceof ApiError) {
    if (err.status === 401 || err.status === 403) return true;
    const code = (err.code || "").toLowerCase();
    if (
      code === "invalid_member" ||
      code === "permission_denied" ||
      code === "membership_missing" ||
      code === "membership_inactive" ||
      code === "moment_not_owned" ||
      code === "moment_not_visible" ||
      code === "context_mismatch" ||
      code === "stale_session_selection"
    ) {
      return true;
    }
  }
  if (err instanceof Error) {
    return ACCESS_DENIED_RE.test(err.message);
  }
  if (typeof err === "string") {
    return ACCESS_DENIED_RE.test(err);
  }
  return false;
}

export function isBusinessMomentAccessDeniedMessage(message: string | null | undefined): boolean {
  if (!message) return false;
  return ACCESS_DENIED_RE.test(message);
}

/** Moments that already triggered a reseat this session (avoid storm). */
const reseatedMomentIds = new Set<string>();

export function wasBusinessMomentReseated(momentId: string): boolean {
  return reseatedMomentIds.has(momentId);
}

export function markBusinessMomentReseated(momentId: string): void {
  reseatedMomentIds.add(momentId);
}

export function clearBusinessMomentReseatMarks(): void {
  reseatedMomentIds.clear();
}

export function getBusinessMomentReseatedIds(): ReadonlySet<string> {
  return reseatedMomentIds;
}

/** True when every moment in inventory already triggered a 403 reseat this session. */
export function areAllBusinessMomentsReseated(
  moments: ReadonlyArray<{ moment_id: string }>,
): boolean {
  if (moments.length === 0) return true;
  return moments.every((m) => reseatedMomentIds.has(m.moment_id));
}

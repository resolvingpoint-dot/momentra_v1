import type { SessionBootstrapResponse } from "@/lib/api/group";

export type GroupMomentType = "SHARED_EXPERIENCE" | "SHARED_PURCHASE" | "SHARED_LIVING";

export type ResolvedActiveGroupMoment = {
  id: string;
  type: GroupMomentType;
};

const GROUP_TYPES = new Set<string>([
  "SHARED_EXPERIENCE",
  "SHARED_PURCHASE",
  "SHARED_LIVING",
]);

function normalizeStatus(value: string | null | undefined): string {
  return (value ?? "").trim().toUpperCase();
}

function asGroupType(value: string | null | undefined): GroupMomentType {
  if (value && GROUP_TYPES.has(value)) {
    return value as GroupMomentType;
  }
  return "SHARED_EXPERIENCE";
}

function isActiveStatus(value: string | null | undefined): boolean {
  const normalized = normalizeStatus(value);
  return normalized === "ACTIVE" || normalized === "LIVE";
}

function fromIdAndType(
  id: string | null | undefined,
  type: string | null | undefined,
): ResolvedActiveGroupMoment | null {
  if (!id) return null;
  return { id, type: asGroupType(type) };
}

/**
 * Resolve the active group moment from session bootstrap using every field
 * the backend may populate (flat ids, live cards, moments list, pulse cards).
 */
export function resolveActiveGroupMoment(
  session: SessionBootstrapResponse,
): ResolvedActiveGroupMoment | null {
  const direct = fromIdAndType(session.active_moment_id, session.moment_type);
  if (direct) return direct;

  const focus = fromIdAndType(session.focus_moment_id, session.moment_type);
  if (focus) return focus;

  const liveCard = session.live_overview?.live_cards?.find((card) => card.id);
  if (liveCard?.id) {
    return fromIdAndType(liveCard.id, liveCard.moment_type);
  }

  const activeInMoments = session.moments?.find(
    (moment) => isActiveStatus(moment.lifecycle_status) && moment.id,
  );
  if (activeInMoments?.id) {
    return fromIdAndType(activeInMoments.id, activeInMoments.moment_type);
  }

  const activeCard = session.pulse?.type_cards?.find(
    (card) => card.linked_moment_id && isActiveStatus(card.linked_moment_status),
  );
  if (activeCard?.linked_moment_id) {
    return fromIdAndType(activeCard.linked_moment_id, activeCard.moment_type_code);
  }

  if (normalizeStatus(session.linked_moment_status) === "ACTIVE") {
    const linked = fromIdAndType(session.active_moment_id, session.moment_type);
    if (linked) return linked;
  }

  return null;
}

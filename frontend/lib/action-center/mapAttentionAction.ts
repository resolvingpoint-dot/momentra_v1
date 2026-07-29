/**
 * Map pulse attention `action` strings to Action Center action_ids.
 * Returns null for hub / unknown / activity-list actions.
 */
export type GroupMomentTypeCode = "SHARED_EXPERIENCE" | "SHARED_PURCHASE" | "SHARED_LIVING" | string;

export function mapAttentionActionToQuickAddId(
  action: string | undefined | null,
  momentTypeCode: GroupMomentTypeCode,
): string | null {
  const normalized = (action || "").trim().toLowerCase();
  if (!normalized || normalized === "hub" || normalized === "review") return null;

  // Bookings → View All activity (handled by caller), not Quick Add.
  if (normalized === "booking" || normalized === "bookings" || normalized === "activity" || normalized === "activities") {
    return null;
  }

  const isPurchase = momentTypeCode === "SHARED_PURCHASE";
  const isLiving = momentTypeCode === "SHARED_LIVING";

  switch (normalized) {
    case "contribution":
    case "contributions":
      return isPurchase ? "CONTRIBUTOR" : "CONTRIBUTION";
    case "vendor":
      return isPurchase || !isLiving ? "VENDOR" : null;
    case "ownership":
      return isPurchase ? "OWNERSHIP" : null;
    case "decision":
    case "poll":
    case "polls":
      return "POLL";
    case "participant":
    case "participants":
      if (isPurchase) return "PARTICIPANTS";
      if (isLiving) return "RESIDENT";
      return "PARTICIPANT";
    case "planning":
    case "planning_item":
      return !isPurchase && !isLiving ? "PLANNING_ITEM" : null;
    case "memory":
      return "MEMORY";
    case "expense":
      return "EXPENSE";
    default:
      return null;
  }
}

/** True when attention action should open the activity list instead of Quick Add. */
export function attentionActionOpensActivity(action: string | undefined | null): boolean {
  const normalized = (action || "").trim().toLowerCase();
  return (
    normalized === "booking" ||
    normalized === "bookings" ||
    normalized === "activity" ||
    normalized === "activities"
  );
}

/**
 * Frozen Team Ops action metadata — labels / display only.
 * Authorization flags come from the Activity DTO (is_editable / is_deletable / supported_actions).
 * Do not use this registry to gate edit/delete UI.
 */
export const TEAM_OPS_ACTION_TYPES = [
  "TEAM_UPDATE",
  "APPROVAL_REQUEST",
  "ISSUE",
  "RECOGNITION",
  "ESCALATION",
  "REVIEW",
  "PARTICIPATION",
  "MEETING",
  "MEMBER_UPDATE",
  "NOTE",
] as const;

export type TeamOpsActionType = (typeof TEAM_OPS_ACTION_TYPES)[number];

export const TEAM_OPS_ACTION_META: Record<
  TeamOpsActionType,
  { editable: boolean; deletable: boolean; label: string }
> = {
  TEAM_UPDATE: { editable: true, deletable: true, label: "Team Update" },
  APPROVAL_REQUEST: { editable: false, deletable: false, label: "Approval" },
  ISSUE: { editable: true, deletable: true, label: "Issue" },
  RECOGNITION: { editable: false, deletable: true, label: "Recognition" },
  ESCALATION: { editable: true, deletable: true, label: "Escalation" },
  REVIEW: { editable: false, deletable: false, label: "Review" },
  PARTICIPATION: { editable: false, deletable: true, label: "Participation" },
  MEETING: { editable: true, deletable: true, label: "Meeting" },
  MEMBER_UPDATE: { editable: true, deletable: true, label: "Member Update" },
  NOTE: { editable: true, deletable: true, label: "Note" },
};

export function resolveActivityPermissions(
  actionType: string,
  flags?: { is_editable?: boolean | null; is_deletable?: boolean | null },
): { is_editable: boolean; is_deletable: boolean } {
  if (typeof flags?.is_editable === "boolean" || typeof flags?.is_deletable === "boolean") {
    return {
      is_editable: Boolean(flags.is_editable),
      is_deletable: Boolean(flags.is_deletable),
    };
  }
  const meta = TEAM_OPS_ACTION_META[actionType as TeamOpsActionType];
  return {
    is_editable: meta?.editable ?? false,
    is_deletable: meta?.deletable ?? false,
  };
}

/**
 * Frozen Business Operations action metadata — labels / display only.
 * Authorization flags come from the Activity DTO.
 */
export const OPS_ACTION_TYPES = [
  "SPEND_ENTRY",
  "VENDOR_UPDATE",
  "OPS_APPROVAL_REQUEST",
  "ISSUE_RISK",
  "OPERATIONAL_IMPROVEMENT",
] as const;

export type OpsActionType = (typeof OPS_ACTION_TYPES)[number];

export const OPS_ACTION_META: Record<OpsActionType, { label: string }> = {
  SPEND_ENTRY: { label: "Spend" },
  VENDOR_UPDATE: { label: "Vendor" },
  OPS_APPROVAL_REQUEST: { label: "Approval" },
  ISSUE_RISK: { label: "Issue / Risk" },
  OPERATIONAL_IMPROVEMENT: { label: "Improvement" },
};

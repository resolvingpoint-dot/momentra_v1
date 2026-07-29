import type { GuidedSetupSummaryRow } from "@/components/setup/guidedSetupTypes";

export type GuidedSetupSummaryItem = {
  label: string;
  value: string;
};

/**
 * Structured live summary model — contexts map into this; shell renders generically.
 */
export type GuidedSetupSummary = {
  primaryType: string;
  title: string;
  members?: number;
  currency?: string;
  budget?: string;
  /** 0–100 completion percent */
  progress: number;
  estimatedMinutes?: number;
  /** e.g. "2 of 4" */
  currentStepLabel?: string;
  extras: GuidedSetupSummaryItem[];
};

export function isGuidedSetupSummary(
  value: GuidedSetupSummary | GuidedSetupSummaryRow[] | undefined,
): value is GuidedSetupSummary {
  return Boolean(value && !Array.isArray(value) && "primaryType" in value);
}

/** Flatten structured summary into label/value rows for the generic renderer. */
export function guidedSummaryToRows(
  summary: GuidedSetupSummary,
): GuidedSetupSummaryRow[] {
  const rows: GuidedSetupSummaryRow[] = [
    { label: "Type", value: summary.primaryType },
    ...summary.extras,
  ];
  if (summary.title.trim()) {
    rows.push({ label: "Title", value: summary.title });
  }
  if (summary.members != null) {
    rows.push({ label: "Members", value: String(summary.members) });
  }
  if (summary.currency) {
    rows.push({ label: "Currency", value: summary.currency });
  }
  if (summary.budget) {
    rows.push({ label: "Budget", value: summary.budget });
  }
  rows.push({
    label: "Completion",
    value: `${Math.round(Math.min(100, Math.max(0, summary.progress)))}%`,
  });
  if (summary.currentStepLabel) {
    rows.push({ label: "Current step", value: summary.currentStepLabel });
  }
  if (summary.estimatedMinutes != null) {
    rows.push({
      label: "Estimated completion",
      value: `About ${summary.estimatedMinutes} min`,
    });
  }
  return rows.filter((r) => r.value);
}

export function normalizeLiveSummary(
  liveSummary: GuidedSetupSummary | GuidedSetupSummaryRow[] | undefined,
): GuidedSetupSummaryRow[] {
  if (!liveSummary) return [];
  if (isGuidedSetupSummary(liveSummary)) {
    return guidedSummaryToRows(liveSummary);
  }
  return liveSummary;
}

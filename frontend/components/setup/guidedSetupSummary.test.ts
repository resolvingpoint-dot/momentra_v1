import { describe, expect, it } from "vitest";
import {
  guidedSummaryToRows,
  normalizeLiveSummary,
  type GuidedSetupSummary,
} from "@/components/setup/guidedSetupSummary";

describe("guidedSetupSummary", () => {
  it("flattens structured summary to rows", () => {
    const summary: GuidedSetupSummary = {
      primaryType: "Team Operations",
      title: "",
      members: 3,
      currency: "INR",
      budget: "INR 10,000",
      progress: 25,
      estimatedMinutes: 3,
      currentStepLabel: "1 of 4",
      extras: [{ label: "Team size", value: "6–15" }],
    };
    const rows = guidedSummaryToRows(summary);
    expect(rows.map((r) => r.label)).toEqual([
      "Type",
      "Team size",
      "Members",
      "Currency",
      "Budget",
      "Completion",
      "Current step",
      "Estimated completion",
    ]);
    expect(rows.find((r) => r.label === "Completion")?.value).toBe("25%");
  });

  it("normalizes legacy row arrays unchanged", () => {
    const rows = [{ label: "Type", value: "X" }];
    expect(normalizeLiveSummary(rows)).toEqual(rows);
  });
});

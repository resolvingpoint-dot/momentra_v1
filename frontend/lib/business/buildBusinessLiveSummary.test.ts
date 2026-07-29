import { describe, expect, it } from "vitest";
import { buildBusinessLiveSummary } from "@/lib/business/buildBusinessLiveSummary";

describe("buildBusinessLiveSummary", () => {
  it("builds local-only rows without requiring preview", () => {
    const rows = buildBusinessLiveSummary({
      templateId: "team_ops",
      answers: {
        team_size: "SMALL",
        operating_currency_code: "INR",
        monthly_team_budget_minor: 5000000,
      },
      currentStep: 2,
      totalSteps: 4,
      estimatedMinutes: 3,
      memberCount: 3,
    });

    const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]));
    expect(byLabel.Type).toBe("Team Operations");
    expect(byLabel.Members).toBe("3");
    expect(byLabel.Currency).toBe("INR");
    expect(byLabel["Team size"]).toBe("2–5");
    expect(byLabel.Completion).toBe("25%");
    expect(byLabel["Current step"]).toBe("2 of 4");
    expect(byLabel["Estimated completion"]).toContain("3");
  });

  it("includes stage for runway and scope for operations", () => {
    const runway = buildBusinessLiveSummary({
      templateId: "business_runway",
      answers: { business_stage: "GROWTH", operating_currency_code: "USD" },
      currentStep: 1,
      totalSteps: 4,
      estimatedMinutes: 3,
      memberCount: 1,
    });
    expect(runway.some((r) => r.label === "Stage" && r.value === "Growth")).toBe(true);

    const ops = buildBusinessLiveSummary({
      templateId: "business_operations",
      answers: {
        operations_scope: "VENDOR_OPERATIONS",
        operating_currency_code: "EUR",
      },
      currentStep: 1,
      totalSteps: 4,
      estimatedMinutes: 3,
      memberCount: 2,
    });
    expect(ops.some((r) => r.label === "Scope" && r.value === "Vendor operations")).toBe(true);
  });
});

import { describe, expect, it } from "vitest";
import {
  estimateRunwayMonths,
  formatRunwayEstimatePrimary,
} from "@/lib/business/runwayEstimate";
import { BUSINESS_SETUP_COPY, choiceLabel, setupChoices } from "@/lib/business/setupCatalog";

describe("business setup catalog", () => {
  it("exposes friendly labels for canonical enums", () => {
    expect(choiceLabel("business_stage", "PRE_REVENUE")).toBe("Pre-revenue");
    expect(choiceLabel("operations_scope", "GENERAL_OPERATIONS")).toBe("General operations");
    expect(choiceLabel("funding_sources", "FRIENDS_FAMILY")).toBe("Friends and family");
    expect(setupChoices("team_size").some((c) => c.value === "SOLO")).toBe(true);
  });

  it("has four steps per template", () => {
    expect(BUSINESS_SETUP_COPY.templates.team_ops.steps).toHaveLength(4);
    expect(BUSINESS_SETUP_COPY.templates.business_runway.steps).toHaveLength(4);
    expect(BUSINESS_SETUP_COPY.templates.business_operations.steps).toHaveLength(4);
  });
});

describe("runway estimate", () => {
  it("computes months from cash and burn", () => {
    const r = estimateRunwayMonths({
      currentCashMinor: 8_400_000,
      monthlyBurnMinor: 1_000_000,
      revenueStatus: "NO_REVENUE",
    });
    expect(r.kind).toBe("months");
    if (r.kind === "months") expect(r.months).toBe(8.4);
    expect(formatRunwayEstimatePrimary(r)).toContain("8.4");
  });

  it("handles positive cash flow", () => {
    const r = estimateRunwayMonths({
      currentCashMinor: 1_000_000,
      monthlyBurnMinor: 500_000,
      estimatedMonthlyRevenueMinor: 800_000,
      collectionRatePercent: 100,
      revenueStatus: "RECURRING_REVENUE",
    });
    expect(r.kind).toBe("positive_cashflow");
  });

  it("asks for burn when missing", () => {
    const r = estimateRunwayMonths({
      currentCashMinor: 1_000_000,
      monthlyBurnMinor: 0,
    });
    expect(r.kind).toBe("need_burn");
  });
});

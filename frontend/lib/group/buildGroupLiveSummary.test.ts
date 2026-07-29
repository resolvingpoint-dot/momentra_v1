import { describe, expect, it } from "vitest";
import { buildGroupLiveSummaryModel } from "@/lib/group/buildGroupLiveSummary";
import { groupSummaryBuilder } from "@/lib/group/buildGroupLiveSummary";
import {
  toGuidedSetupAnalyticsPayload,
} from "@/components/setup/guidedSetupAnalytics";

describe("GroupSummaryBuilder", () => {
  it("builds Shared Experience summary from local answers", () => {
    const summary = buildGroupLiveSummaryModel({
      templateId: "shared_experience",
      answers: {
        experience_type: "TRIP_VACATION",
        experience_name: "Goa Trip",
        budget_currency: "INR",
        estimated_budget: "50000",
        destination: "Goa",
        split_style: "SHARED_POOL",
      },
      currentStep: 2,
      totalSteps: 4,
      estimatedMinutes: 4,
      memberCount: 6,
    });

    expect(summary.primaryType).toBe("Shared Experience");
    expect(summary.title).toBe("Goa Trip");
    expect(summary.currency).toBe("INR");
    expect(summary.members).toBe(6);
    expect(summary.progress).toBe(25);
    expect(summary.extras.some((e) => e.label === "Experience")).toBe(true);
    expect(summary.extras.some((e) => e.label === "Destination" && e.value === "Goa")).toBe(
      true,
    );
  });

  it("satisfies GuidedSetupSummaryBuilder interface", () => {
    const summary = groupSummaryBuilder.build({
      answers: { templateId: "shared_purchase", purchase_name: "Gift", currency_code: "USD" },
      currentStep: 1,
      totalSteps: 4,
      estimatedMinutes: 4,
    });
    expect(summary.primaryType).toBe("Shared Purchase");
    expect(summary.title).toBe("Gift");
  });
});

describe("guided setup analytics payload", () => {
  it("normalizes events to comparable envelope", () => {
    const payload = toGuidedSetupAnalyticsPayload({
      type: "step_changed",
      stepId: "dates_money",
      stepIndex: 2,
      templateId: "shared_experience",
      contextType: "group",
      saveState: "saved",
      elapsedMs: 1200,
    });
    expect(payload).toEqual({
      action: "step_changed",
      context: "group",
      template: "shared_experience",
      step: "dates_money",
      stepIndex: 2,
      saveState: "saved",
      elapsedMs: 1200,
    });
  });
});

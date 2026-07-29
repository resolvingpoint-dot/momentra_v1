import { describe, expect, it } from "vitest";
import {
  buildGroupLiveSummaryModel,
  groupSummaryBuilder,
} from "@/lib/group/buildGroupLiveSummary";
import { toGuidedSetupAnalyticsPayload } from "@/components/setup/guidedSetupAnalytics";

describe("Shared Purchase summary", () => {
  it("maps purchase fields into local summary rows", () => {
    const summary = buildGroupLiveSummaryModel({
      templateId: "shared_purchase",
      answers: {
        purchase_profile: "GIFT_POOL",
        purchase_name: "Birthday gift for Rahul",
        expected_amount: "5000",
        currency_code: "INR",
        payment_plan: "EQUAL",
        ownership_style: "SHARED",
        decision_deadline: "2026-12-01",
        contributors: "4",
      },
      currentStep: 3,
      totalSteps: 4,
      estimatedMinutes: 4,
      memberCount: 4,
    });

    expect(summary.primaryType).toBe("Shared Purchase");
    expect(summary.title).toBe("Birthday gift for Rahul");
    expect(summary.currency).toBe("INR");
    expect(summary.budget).toContain("5,000");
    expect(summary.members).toBe(4);
    expect(summary.progress).toBe(50);
    expect(summary.extras.find((e) => e.label === "Purchase")?.value).toBe("Gift Pool");
    expect(summary.extras.find((e) => e.label === "Contribution")?.value).toBe(
      "Equal contribution",
    );
    expect(summary.extras.find((e) => e.label === "Ownership")?.value).toBe(
      "Shared equally",
    );
    expect(summary.extras.find((e) => e.label === "Target date")?.value).toBe(
      "2026-12-01",
    );
  });

  it("uses major units for expected_amount (not dividing by 100)", () => {
    const summary = groupSummaryBuilder.build({
      answers: {
        templateId: "shared_purchase",
        expected_amount: "1000",
        currency_code: "USD",
      },
      currentStep: 2,
      totalSteps: 4,
      estimatedMinutes: 4,
    });
    expect(summary.budget).toBe("USD 1,000");
  });
});

describe("Shared Purchase analytics envelope", () => {
  it("emits comparable payload without PII fields", () => {
    const payload = toGuidedSetupAnalyticsPayload({
      type: "setup_open",
      contextType: "group",
      templateId: "shared_purchase",
      momentTypeCode: "SHARED_PURCHASE",
      momentId: "m-purchase-1",
      elapsedMs: 0,
    });
    expect(payload.context).toBe("group");
    expect(payload.template).toBe("shared_purchase");
    expect(payload.action).toBe("setup_open");
    expect(JSON.stringify(payload)).not.toMatch(/Rahul|gift|email|phone|5000/i);
  });
});

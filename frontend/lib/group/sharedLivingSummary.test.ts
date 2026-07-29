import { describe, expect, it } from "vitest";
import {
  buildGroupLiveSummaryModel,
  groupSummaryBuilder,
} from "@/lib/group/buildGroupLiveSummary";
import { toGuidedSetupAnalyticsPayload } from "@/components/setup/guidedSetupAnalytics";
import { groupGuidedSteps, groupSetupTemplate } from "@/lib/group/setupCatalog";

describe("Shared Living summary", () => {
  it("maps living fields into local summary rows", () => {
    const summary = buildGroupLiveSummaryModel({
      templateId: "shared_living",
      answers: {
        living_type: "FLATMATES",
        home_name: "Jubilee Hills Flatmates",
        monthly_budget: "45000",
        currency_code: "INR",
        rent_split_style: "SHARED",
        chores_style: "ROTATION",
        members: "3",
      },
      currentStep: 3,
      totalSteps: 4,
      estimatedMinutes: 4,
      memberCount: 3,
    });

    expect(summary.primaryType).toBe("Shared Living");
    expect(summary.title).toBe("Jubilee Hills Flatmates");
    expect(summary.currency).toBe("INR");
    expect(summary.budget).toContain("45,000");
    expect(summary.members).toBe(3);
    expect(summary.progress).toBe(50);
    expect(summary.extras.find((e) => e.label === "Living type")?.value).toBe("Flatmates");
    expect(summary.extras.find((e) => e.label === "Cost split")?.value).toBe(
      "Shared equally",
    );
    expect(summary.extras.find((e) => e.label === "Chores")?.value).toBe("Rotation");
  });

  it("uses major units for monthly_budget (not dividing by 100)", () => {
    const summary = groupSummaryBuilder.build({
      answers: {
        templateId: "shared_living",
        monthly_budget_major: "1200",
        currency_code: "USD",
      },
      currentStep: 2,
      totalSteps: 4,
      estimatedMinutes: 4,
    });
    expect(summary.budget).toBe("USD 1,200");
  });

  it("catalog has four guided steps for shared_living", () => {
    const steps = groupGuidedSteps("shared_living");
    expect(steps).toHaveLength(4);
    expect(steps.map((s) => s.id)).toEqual([
      "basics",
      "budget_prefs",
      "members",
      "review",
    ]);
    expect(groupSetupTemplate("shared_living").activate_cta).toBe(
      "Activate Shared Living",
    );
  });
});

describe("Shared Living analytics envelope", () => {
  it("emits comparable payload without PII fields", () => {
    const payload = toGuidedSetupAnalyticsPayload({
      type: "setup_open",
      contextType: "group",
      templateId: "shared_living",
      momentTypeCode: "SHARED_LIVING",
      momentId: "m-living-1",
      elapsedMs: 0,
    });
    expect(payload.context).toBe("group");
    expect(payload.template).toBe("shared_living");
    expect(payload.action).toBe("setup_open");
    expect(JSON.stringify(payload)).not.toMatch(/Malla|Flatmates|email|phone|45000/i);
  });
});

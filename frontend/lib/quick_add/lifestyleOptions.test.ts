import { describe, expect, it } from "vitest";
import {
  lsErrorMessage,
  lsSuccessMessage,
  normalizeLifestyleEventType,
} from "@/lib/quick_add/lifestyleCopy";
import {
  buildLifestylePayload,
  canSubmitLifestyle,
} from "@/lib/quick_add/lifestyleOptions";
import { tabSuccessMessage } from "@/lib/quick_add/lifeOpsCopy";

describe("lifestyleCopy", () => {
  it("normalizes create/adjust aliases", () => {
    expect(normalizeLifestyleEventType("CREATIVE")).toBe("EXPRESSION");
    expect(normalizeLifestyleEventType("LIFESTYLE_ADJUST")).toBe("ADJUST");
  });

  it("covers success messages", () => {
    expect(lsSuccessMessage("LIFESTYLE_EXPENSE")).toBe("Lifestyle expense saved");
    expect(lsSuccessMessage("CREATIVE")).toBe("Creation saved");
    expect(lsSuccessMessage("LIFESTYLE_ADJUST")).toBe("Lifestyle updated");
    expect(tabSuccessMessage("WELLBEING")).toBe(lsSuccessMessage("WELLBEING"));
    expect(lsErrorMessage("DISCOVERY")).toContain("Try again");
  });
});

describe("lifestyleOptions", () => {
  it("requires event_title", () => {
    expect(
      canSubmitLifestyle("LIFESTYLE_EXPENSE", { amount: "10" }, {}, ""),
    ).toBe(false);
    expect(
      canSubmitLifestyle("LIFESTYLE_EXPENSE", { amount: "10" }, {}, "Dinner out"),
    ).toBe(true);
  });

  it("builds complete payload fields", () => {
    const payload = buildLifestylePayload(
      {
        amount: "120",
        spend_category: "Travel",
        experience_type: "Food",
        value_received: "Worth It",
        curiosity_level: "High",
        time_invested: "30_60",
      },
      {
        wellbeing_areas: new Set(["Health", "Rest"]),
        contributors: new Set(["Sleep"]),
      },
    );
    expect(payload.amount).toBe("120");
    expect(payload.spend_category).toBe("Travel");
    expect(payload.value_received).toBe("Worth It");
    expect(payload.curiosity_level).toBe("High");
    expect(payload.time_invested).toBe("30_60");
    expect(payload.wellbeing_areas).toEqual(["Health", "Rest"]);
    expect(payload.contributors).toEqual(["Sleep"]);
  });
});

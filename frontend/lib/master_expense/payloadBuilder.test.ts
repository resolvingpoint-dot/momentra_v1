import { describe, expect, it } from "vitest";
import { buildMasterExpensePayload } from "@/lib/master_expense/payloadBuilder";

describe("buildMasterExpensePayload", () => {
  it("sends amount_minor and currency_code", () => {
    const payload = buildMasterExpensePayload(
      {
        title: "Dinner",
        amountMinor: 450000,
        currencyCode: "INR",
        accountId: "acc-1",
        categoryCode: "DINING_OUT",
        subcategoryCode: "",
        occurredAt: "2026-07-08T12:00",
        feeling: "GREAT",
        meaningfulness: "HIGH",
        memorability: "HIGH",
        sharedEnabled: true,
        sharedWith: ["SPOUSE"],
        relationshipImpact: ["STRENGTHENED_CONNECTION"],
        contextReason: "CELEBRATION",
        notes: "",
      },
      "req-1",
    );

    expect(payload.amount_minor).toBe(450000);
    expect(payload.currency_code).toBe("INR");
    expect(payload.client_request_id).toBe("req-1");
  });

  it("shared=false excludes relationships fan-out flag", () => {
    const payload = buildMasterExpensePayload(
      {
        title: "Coffee",
        amountMinor: 50000,
        currencyCode: "USD",
        accountId: "acc-2",
        categoryCode: "FOOD",
        subcategoryCode: "",
        occurredAt: "",
        feeling: "",
        meaningfulness: "",
        memorability: "",
        sharedEnabled: false,
        sharedWith: [],
        relationshipImpact: [],
        contextReason: "",
        notes: "",
      },
      "req-2",
    );

    expect(payload.shared.is_shared).toBe(false);
    expect(payload.shared.shared_with).toEqual([]);
  });
});

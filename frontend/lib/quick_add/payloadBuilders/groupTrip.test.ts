import { describe, expect, it } from "vitest";
import { buildTripQuickAddPayload, parseAmountMinor } from "@/lib/quick_add/payloadBuilders/groupTrip";

describe("parseAmountMinor", () => {
  it("treats numbers as already-minor (no second *100)", () => {
    expect(parseAmountMinor(35_000_000)).toBe(35_000_000);
    expect(parseAmountMinor(100_000)).toBe(100_000);
  });

  it("converts major string rupees to minor once", () => {
    expect(parseAmountMinor("350000")).toBe(35_000_000);
    expect(parseAmountMinor("1000")).toBe(100_000);
  });
});

describe("buildTripQuickAddPayload BOOKING / CONTRIBUTION", () => {
  it("keeps pre-converted numeric amount_minor for bookings", () => {
    const payload = buildTripQuickAddPayload("BOOKING", {
      booking_type: "flight",
      provider: "Air India",
      booking_status: "confirmed",
      amount_minor: 35_000_000,
    });
    expect(payload.amount_minor).toBe(35_000_000);
  });

  it("converts major string once when callers pass rupees as string", () => {
    const payload = buildTripQuickAddPayload("BOOKING", {
      booking_type: "hotel",
      amount_minor: "350000",
    });
    expect(payload.amount_minor).toBe(35_000_000);
  });

  it("does not 100x inflate contribution when amount_minor is numeric", () => {
    const payload = buildTripQuickAddPayload("CONTRIBUTION", {
      amount_minor: 5_000_000,
      contributor_id: "u1",
    });
    expect(payload.amount_minor).toBe(5_000_000);
  });
});

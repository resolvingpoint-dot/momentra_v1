import { describe, expect, it } from "vitest";
import {
  attentionActionOpensActivity,
  mapAttentionActionToQuickAddId,
} from "@/lib/action-center/mapAttentionAction";

describe("mapAttentionActionToQuickAddId", () => {
  it("maps purchase funding and vendor signals", () => {
    expect(mapAttentionActionToQuickAddId("contribution", "SHARED_PURCHASE")).toBe("CONTRIBUTOR");
    expect(mapAttentionActionToQuickAddId("vendor", "SHARED_PURCHASE")).toBe("VENDOR");
  });

  it("maps experience contribution and bookings", () => {
    expect(mapAttentionActionToQuickAddId("contributions", "SHARED_EXPERIENCE")).toBe("CONTRIBUTION");
    expect(mapAttentionActionToQuickAddId("bookings", "SHARED_EXPERIENCE")).toBeNull();
    expect(attentionActionOpensActivity("bookings")).toBe(true);
  });
});

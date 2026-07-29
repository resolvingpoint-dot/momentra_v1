import { describe, expect, it } from "vitest";
import {
  buildEmotionalSecurityPayload,
  canSubmitRelationships,
  normalizeRelationshipsEventType,
  requiredKeysForTab,
  rsSuccessMessage,
} from "@/lib/personal/relationships/relationshipsQuickAddHelpers";

describe("relationshipsQuickAddHelpers", () => {
  it("normalizes RELATIONSHIP_ADJUST to ADJUST", () => {
    expect(normalizeRelationshipsEventType("RELATIONSHIP_ADJUST")).toBe("ADJUST");
    expect(requiredKeysForTab("RELATIONSHIP_ADJUST").has("adjustment_area")).toBe(true);
  });

  it("requires event title and type-specific keys", () => {
    expect(canSubmitRelationships("CONNECTION", { connection_type: "Call" }, "")).toBe(false);
    expect(canSubmitRelationships("CONNECTION", { connection_type: "Call" }, "Mom")).toBe(true);
    expect(canSubmitRelationships("SUPPORT", { support_type: "Care" }, "Helped")).toBe(false);
    expect(
      canSubmitRelationships(
        "SUPPORT",
        { support_type: "Care", support_direction: "Given" },
        "Helped",
      ),
    ).toBe(true);
  });

  it("builds payload with only filled fields", () => {
    const payload = buildEmotionalSecurityPayload({
      connection_type: "Call",
      notes: "  hi  ",
      amount: "",
    });
    expect(payload).toEqual({ connection_type: "Call", notes: "hi" });
  });

  it("returns type-specific success copy", () => {
    expect(rsSuccessMessage("SHARED_EXPERIENCE")).toBe("Shared experience saved");
    expect(rsSuccessMessage("ADJUST")).toBe("Relationship priority updated");
    expect(rsSuccessMessage("RELATIONSHIP_ADJUST")).toBe("Relationship priority updated");
  });
});

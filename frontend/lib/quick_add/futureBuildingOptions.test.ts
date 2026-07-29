import { describe, expect, it } from "vitest";
import {
  FB_EVENT_TYPES,
  fbErrorMessage,
  fbSuccessMessage,
} from "@/lib/quick_add/futureBuildingCopy";
import {
  buildFutureBuildingPayload,
  canSubmitFb,
  FIELD_TO_PAYLOAD_KEY,
  missingFbRequiredHint,
  requiredKeysForFbTab,
} from "@/lib/quick_add/futureBuildingOptions";
import { tabSuccessMessage } from "@/lib/quick_add/lifeOpsCopy";

describe("futureBuildingOptions payload", () => {
  it("includes outcome_value, learning_topic, and relevance", () => {
    expect(FIELD_TO_PAYLOAD_KEY.outcome_value).toBe("outcome_value");
    expect(FIELD_TO_PAYLOAD_KEY.learning_topic).toBe("learning_topic");
    expect(FIELD_TO_PAYLOAD_KEY.relevance).toBe("relevance");

    const payload = buildFutureBuildingPayload({
      outcome_value: "Income Increase",
      learning_topic: "Marketing",
      relevance: "Useful",
      amount: "100",
    });
    expect(payload).toEqual({
      outcome_value: "Income Increase",
      learning_topic: "Marketing",
      relevance: "Useful",
      amount: "100",
    });
  });

  it("requires event_title for submit", () => {
    expect(
      canSubmitFb(
        "CONTRIBUTION",
        [{ group_key: "amount", label: "Amount", field_type: "amount" }],
        { amount: "50" },
        "",
      ),
    ).toBe(false);
    expect(
      canSubmitFb(
        "CONTRIBUTION",
        [{ group_key: "amount", label: "Amount", field_type: "amount" }],
        { amount: "50" },
        "Invested in product",
      ),
    ).toBe(true);
  });

  it("keeps pivot notes required", () => {
    expect(requiredKeysForFbTab("PIVOT").has("notes")).toBe(true);
    expect(
      missingFbRequiredHint(
        "PIVOT",
        [
          { group_key: "pivot_change", label: "What changed?", field_type: "chip_grid" },
          { group_key: "notes", label: "Notes", field_type: "textarea" },
        ],
        { pivot_change: "Scope" },
        "Changed direction",
      ),
    ).toBe("Required: Notes");
  });
});

describe("futureBuilding copy", () => {
  it("covers all FB event types", () => {
    for (const type of FB_EVENT_TYPES) {
      expect(fbSuccessMessage(type)).not.toBe("Entry saved");
      expect(fbErrorMessage(type)).toContain("Try again");
      expect(tabSuccessMessage(type)).toBe(fbSuccessMessage(type));
    }
  });
});

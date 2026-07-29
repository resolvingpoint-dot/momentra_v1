import { describe, expect, it } from "vitest";

import {
  resolveMomentSwitcherOptions,
  reconcileSelectedMomentType,
  templateMomentsEnabled,
  memoryHasTypePayload,
  momentsHasTypePayload,
  pulseHasTypePayload,
} from "./personalMomentRouting";
import { hasTypeSessionCacheHint } from "@/lib/personal/sessionCacheHint";
import { parsePersonalPulseResponse } from "@/lib/personal/personalApiMappers";
import type {
  PersonalCreateOptionCard,
  PersonalMomentHomeCard,
  PersonalMomentsHomeResponse,
  PersonalMemoryResponse,
} from "@/lib/api/personal";

function homeCard(
  code: string,
  overrides: Partial<PersonalMomentHomeCard> = {},
): PersonalMomentHomeCard {
  return {
    moment_type_id: "1",
    moment_type_code: code,
    moment_type_name: code,
    display_order: code === "LIFE_OPERATIONS" ? 1 : 2,
    linked_moment_id: `${code}-id`,
    linked_moment_status: "ACTIVE",
    is_active: true,
    ...overrides,
  };
}

function createCard(
  code: string,
  overrides: Partial<PersonalCreateOptionCard> = {},
): PersonalCreateOptionCard {
  return {
    moment_type_id: "1",
    moment_type_code: code,
    moment_type_name: code,
    create_tagline: "",
    create_badge_label: null,
    is_create_featured: false,
    theme_color: "#000",
    icon_name: "icon",
    display_order: code === "LIFE_OPERATIONS" ? 1 : 2,
    linked_moment_id: `${code}-create-id`,
    linked_moment_status: "ACTIVE",
    has_draft: false,
    action_label: "Open",
    background_image_url: null,
    ...overrides,
  };
}

describe("templateMomentsEnabled", () => {
  it("enables template moments path for all personal templates", () => {
    expect(templateMomentsEnabled("LIFE_OPERATIONS")).toBe(true);
    expect(templateMomentsEnabled("FUTURE_BUILDING")).toBe(true);
    expect(templateMomentsEnabled("LIFESTYLE")).toBe(true);
    expect(templateMomentsEnabled("RELATIONSHIPS")).toBe(true);
  });
});

describe("resolveMomentSwitcherOptions", () => {
  it("merges LO on home with FB active on create only", () => {
    const momentsHome: PersonalMomentsHomeResponse = {
      subtitle: "",
      active_moment_count: 1,
      is_empty: false,
      cards: [homeCard("LIFE_OPERATIONS")],
    };
    const createOptions = [
      createCard("LIFE_OPERATIONS"),
      createCard("FUTURE_BUILDING"),
    ];
    const options = resolveMomentSwitcherOptions(momentsHome, createOptions);
    expect(options.map((o) => o.typeCode)).toEqual([
      "LIFE_OPERATIONS",
      "FUTURE_BUILDING",
    ]);
    expect(options.find((o) => o.typeCode === "LIFE_OPERATIONS")?.momentId).toBe(
      "LIFE_OPERATIONS-id",
    );
    expect(options.find((o) => o.typeCode === "FUTURE_BUILDING")?.momentId).toBe(
      "FUTURE_BUILDING-create-id",
    );
  });

  it("includes both types when both are active on home without duplicates", () => {
    const momentsHome: PersonalMomentsHomeResponse = {
      subtitle: "",
      active_moment_count: 2,
      is_empty: false,
      cards: [homeCard("LIFE_OPERATIONS"), homeCard("FUTURE_BUILDING")],
    };
    const createOptions = [
      createCard("LIFE_OPERATIONS"),
      createCard("FUTURE_BUILDING"),
    ];
    const options = resolveMomentSwitcherOptions(momentsHome, createOptions);
    expect(options.map((o) => o.typeCode)).toEqual([
      "LIFE_OPERATIONS",
      "FUTURE_BUILDING",
    ]);
  });

  it("falls back to create cards when home has no active cards", () => {
    const momentsHome: PersonalMomentsHomeResponse = {
      subtitle: "",
      active_moment_count: 0,
      is_empty: true,
      cards: [homeCard("FUTURE_BUILDING", { is_active: false })],
    };
    const createOptions = [createCard("FUTURE_BUILDING")];
    const options = resolveMomentSwitcherOptions(momentsHome, createOptions);
    expect(options.map((o) => o.typeCode)).toEqual(["FUTURE_BUILDING"]);
  });

  it("holds selected type while switcher options are stale after activation", () => {
    const momentsHome: PersonalMomentsHomeResponse = {
      subtitle: "",
      active_moment_count: 1,
      is_empty: false,
      cards: [homeCard("LIFE_OPERATIONS")],
    };
    const createOptions = [createCard("LIFE_OPERATIONS")];
    const staleOptions = resolveMomentSwitcherOptions(momentsHome, createOptions);
    expect(
      reconcileSelectedMomentType(staleOptions, "FUTURE_BUILDING", "FUTURE_BUILDING"),
    ).toBe("FUTURE_BUILDING");
  });
});

describe("pulseHasTypePayload", () => {
  it("detects payload per template type", () => {
    expect(
      pulseHasTypePayload(
        parsePersonalPulseResponse({ life_operations: { metrics: {} } }),
        "LIFE_OPERATIONS",
      ),
    ).toBe(true);
    expect(
      pulseHasTypePayload(
        parsePersonalPulseResponse({ future_building: { metrics: {} } }),
        "FUTURE_BUILDING",
      ),
    ).toBe(true);
    expect(
      pulseHasTypePayload(
        parsePersonalPulseResponse({ lifestyle: { metrics: {} } }),
        "LIFESTYLE",
      ),
    ).toBe(true);
    expect(
      pulseHasTypePayload(
        parsePersonalPulseResponse({ emotional_security: { metrics: {} } }),
        "RELATIONSHIPS",
      ),
    ).toBe(true);
  });

  it("does not treat another template payload as a match", () => {
    const pulse = parsePersonalPulseResponse({ life_operations: { metrics: {} } });
    expect(pulseHasTypePayload(pulse, "LIFESTYLE")).toBe(false);
    expect(pulseHasTypePayload(pulse, "FUTURE_BUILDING")).toBe(false);
  });
});

describe("momentsHasTypePayload", () => {
  it("requires lifestyle metrics for lifestyle moments", () => {
    expect(
      momentsHasTypePayload(
        {
          active_moment_count: 1,
          is_empty: false,
          cards: [],
          lifestyle_detail: { metrics: { journey_hero: {} } },
        } as unknown as PersonalMomentsHomeResponse,
        "LIFESTYLE",
      ),
    ).toBe(true);
    expect(
      momentsHasTypePayload(
        {
          active_moment_count: 1,
          is_empty: false,
          cards: [],
          lifestyle_detail: { metrics: null },
        } as unknown as PersonalMomentsHomeResponse,
        "LIFESTYLE",
      ),
    ).toBe(false);
  });
});

describe("memoryHasTypePayload", () => {
  it("detects relationships memory payload", () => {
    expect(
      memoryHasTypePayload(
        {
          is_empty: false,
          emotional_security: { metrics: {} },
        } as unknown as PersonalMemoryResponse,
        "RELATIONSHIPS",
      ),
    ).toBe(true);
  });
});

describe("hasTypeSessionCacheHint", () => {
  it("uses in-memory sources before disk", () => {
    expect(
      hasTypeSessionCacheHint("LIFESTYLE", {
        pulse: parsePersonalPulseResponse({ lifestyle: { metrics: {} } }),
      }),
    ).toBe(true);
    expect(
      hasTypeSessionCacheHint("LIFESTYLE", {
        pulse: parsePersonalPulseResponse({ life_operations: { metrics: {} } }),
      }),
    ).toBe(false);
  });
});

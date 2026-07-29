import { describe, expect, it } from "vitest";
import {
  parsePersonalMemoryResponse,
  parsePersonalMomentsHomeResponse,
  parsePersonalPulseResponse,
  parseTemplateMemoryResponse,
  parseTemplateMomentsResponse,
} from "./personalApiMappers";

describe("personalApiMappers", () => {
  it("returns safe defaults for invalid pulse payloads", () => {
    expect(parsePersonalPulseResponse(null)).toEqual({
      overall_rhythm_state: "EMPTY",
      active_moment_count: 0,
      is_empty: true,
      hero_title: null,
      hero_subtitle: null,
      journey_title: null,
      journey_subtitle: null,
      cta_label: null,
      life_operations: undefined,
      future_building: undefined,
      lifestyle: undefined,
      emotional_security: undefined,
    });
  });

  it("preserves known pulse branches", () => {
    const parsed = parsePersonalPulseResponse({
      is_empty: false,
      lifestyle: { metrics: { score: 1 } },
    });
    expect(parsed.is_empty).toBe(false);
    expect(parsed.lifestyle).toEqual({ metrics: { score: 1 } });
  });

  it("returns safe defaults for invalid moments payloads", () => {
    expect(parsePersonalMomentsHomeResponse(undefined)).toEqual({
      active_moment_count: 0,
      is_empty: true,
      subtitle: "",
      cards: [],
      life_operations_detail: undefined,
      future_building_detail: undefined,
      lifestyle_detail: undefined,
      emotional_security_detail: undefined,
    });
  });

  it("returns safe defaults for invalid memory payloads", () => {
    expect(parsePersonalMemoryResponse("bad")).toEqual({
      is_empty: true,
      life_operations: undefined,
      future_building: undefined,
      lifestyle: undefined,
      emotional_security: undefined,
    });
  });

  it("parses template projection envelopes", () => {
    expect(
      parseTemplateMomentsResponse({
        moment_type_code: "LIFESTYLE",
        status: "ACTIVE",
        moment_projection: { journey_hero: {} },
      }).status,
    ).toBe("ACTIVE");
    expect(
      parseTemplateMemoryResponse({
        moment_type_code: "RELATIONSHIPS",
        status: "ACTIVE",
        memory_projection: { highlights: [] },
      }).memory_projection,
    ).toEqual({ highlights: [] });
  });
});

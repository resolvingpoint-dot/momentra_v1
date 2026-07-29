import { describe, expect, it } from "vitest";

import { lifestyleTemplate } from "./myMoney";

const BACKEND_LIFESTYLE_FIELD_KEYS = [
  "moment_name",
  "lifestyle_vision",
  "current_lifestyle",
  "health_energy",
  "daily_habits",
  "work_life_balance",
  "relationships_social",
  "home_environment",
  "personal_priorities",
  "neglected",
  "future_lifestyle_goals",
];

describe("lifestyleTemplate", () => {
  it("matches backend setup_schema field keys", () => {
    const keys = lifestyleTemplate.sections.map((section) => section.field_key);
    expect(keys).toEqual(BACKEND_LIFESTYLE_FIELD_KEYS);
  });

  it("requires priorities, neglected, and future goals", () => {
    const required = lifestyleTemplate.sections
      .filter((section) => section.required)
      .map((section) => section.field_key);
    expect(required).toContain("personal_priorities");
    expect(required).toContain("neglected");
    expect(required).toContain("future_lifestyle_goals");
  });
});

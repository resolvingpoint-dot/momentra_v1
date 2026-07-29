import { describe, expect, it } from "vitest";
import {
  TEAM_OPS_LIFE_SLICE_KEYS,
  TEAM_OPS_MOMENTS_SECTION_KEYS,
  TEAM_OPS_PULSE_SECTION_KEYS,
} from "@/lib/api/businessActive";
import { MEMORY_BUCKET_ORDER } from "@/lib/business/teamOpsApiMappers";
import { healthBandColor } from "@/components/business/active/team_ops/teamOpsTheme";

describe("Team Ops Run 8.2 contracts", () => {
  it("Pulse deterministic section tree", () => {
    expect([...TEAM_OPS_PULSE_SECTION_KEYS]).toEqual([
      "hero",
      "kpis",
      "approvals",
      "participation",
      "issues",
      "recognition",
      "recent_activity",
      "attention",
      "signals",
      "next_action",
    ]);
  });

  it("Moments keeps timeline distinct from Pulse", () => {
    expect(TEAM_OPS_MOMENTS_SECTION_KEYS).toContain("timeline");
    expect(TEAM_OPS_MOMENTS_SECTION_KEYS).toContain("journey_hero");
    expect(TEAM_OPS_PULSE_SECTION_KEYS).not.toContain("timeline");
  });

  it("Life is seven Team Ops slices only", () => {
    expect(TEAM_OPS_LIFE_SLICE_KEYS).toHaveLength(7);
  });

  it("Memory bucket order is allowlist presentation only", () => {
    expect(MEMORY_BUCKET_ORDER).toContain("resolved_issues");
    expect(MEMORY_BUCKET_ORDER).toContain("team_updates");
    expect(MEMORY_BUCKET_ORDER).not.toContain("ai_summary");
  });

  it("health bands map without inventing scores", () => {
    expect(healthBandColor("healthy")).toMatch(/^#/);
  });
});

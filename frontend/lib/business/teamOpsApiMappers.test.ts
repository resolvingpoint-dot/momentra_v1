import { describe, expect, it, vi, beforeEach } from "vitest";
import {
  filterEventsByMoment,
  mergeOptimisticEvents,
  parseBusinessLifeResponse,
  parseTeamOpsMomentsResponse,
  parseTeamOpsPulseResponse,
} from "@/lib/business/teamOpsApiMappers";
import { TEAM_OPS_PULSE_SECTION_KEYS } from "@/lib/api/businessActive";

vi.mock("@/lib/api/client", () => ({
  requestWithRetry: vi.fn(async (url: string) => {
    if (String(url).endsWith("/pulse")) {
      return {
        moment_id: "m1",
        moment_type: "TEAM_OPERATIONS",
        status: "active",
        is_active: true,
        hero: { state: "empty", title: "Team" },
        health_drivers: { state: "empty", items: [] },
        kpis: {
          state: "empty",
          members: 0,
          open_issues: 0,
          pending_approvals: 0,
          recognitions: 0,
          meetings: 0,
          escalations: 0,
          participation: 0,
        },
        approvals: { state: "empty", items: [] },
        participation: { state: "empty", items: [] },
        issues: { state: "empty", items: [] },
        recognition: { state: "empty", items: [] },
        recent_activity: { state: "empty", items: [] },
        attention: { state: "empty", items: [] },
        signals: { state: "empty", items: [] },
        next_action: { state: "empty", item: null },
      };
    }
    if (String(url).endsWith("/life")) {
      return {
        active_moment_count: 0,
        moments: [],
        slices: {},
      };
    }
    return { url };
  }),
}));

vi.mock("@/repositories/BusinessRepository", () => ({
  BusinessRepository: {
    archiveMoment: vi.fn(),
    completeMoment: vi.fn(),
  },
}));

import { requestWithRetry } from "@/lib/api/client";
import { getLife, getPulse } from "@/repositories/BusinessActiveRepository";

describe("teamOpsApiMappers", () => {
  it("parses pulse with all section keys and enriched projector fields", () => {
    const pulse = parseTeamOpsPulseResponse({
      moment_id: "x",
      moment_type: "TEAM_OPERATIONS",
      status: "active",
      is_active: true,
      hero: {
        state: "complete",
        title: "Acme",
        overall_team_health: { label: "On track", band: "healthy", score: 82, max_score: 100 },
      },
      health_drivers: {
        state: "complete",
        items: [
          {
            driver_code: "participation",
            driver_name: "Participation",
            score: 88,
            status: "excellent",
            delta: 12,
            trend: "up",
          },
        ],
      },
      kpis: { state: "complete", members: 3, open_issues: 0, pending_approvals: 0, recognitions: 0, meetings: 0, escalations: 0, participation: 1 },
      approvals: { state: "empty", items: [] },
      participation: { state: "empty", items: [] },
      issues: { state: "empty", items: [] },
      recognition: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
      attention: {
        state: "partial",
        items: [{ kind: "pending_approvals", label: "2 pending approvals", count: 2, severity: "high" }],
      },
      signals: {
        state: "partial",
        items: [{ signal_type: "approval_request", label: "Approvals up", change_percent: 12 }],
      },
      next_action: {
        state: "complete",
        item: {
          action_id: "approval",
          label: "Review pending approvals",
          reason: "pending_approvals",
          cta_label: "Take Action",
        },
      },
    });
    for (const key of TEAM_OPS_PULSE_SECTION_KEYS) {
      expect(pulse).toHaveProperty(key);
    }
    expect(pulse.hero.overall_team_health?.score).toBe(82);
    expect(pulse.health_drivers.items[0]?.driver_code).toBe("participation");
    expect(pulse.signals.items[0]?.change_percent).toBe(12);
  });

  it("parses moments progress snapshot and highlights", () => {
    const moments = parseTeamOpsMomentsResponse({
      moment_id: "m1",
      journey_hero: { title: "Ops", member_count: 3, activity_count: 5, is_active: true },
      progress_snapshot: {
        state: "complete",
        items: [{ metric_code: "participation", metric_name: "Participation", score: 88, delta: 12 }],
      },
      highlights: { state: "empty", items: [] },
      milestones: { state: "empty", items: [] },
      meetings: { state: "empty", items: [] },
      approvals: { state: "empty", items: [] },
      recognition: { state: "empty", items: [] },
      issues: { state: "empty", items: [] },
      team_changes: { state: "empty", items: [] },
      timeline: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
    });
    expect(moments.progress_snapshot.items[0]?.metric_code).toBe("participation");
  });

  it("parses pulse sparse without invented scores", () => {
    const pulse = parseTeamOpsPulseResponse({
      moment_id: "x",
      moment_type: "TEAM_OPERATIONS",
      status: "active",
      is_active: true,
      hero: { state: "complete", title: "Acme", overall_team_health: { label: "On track", band: "healthy" } },
      health_drivers: { state: "empty", items: [] },
      kpis: { state: "complete", members: 3, open_issues: 0, pending_approvals: 0, recognitions: 0, meetings: 0, escalations: 0, participation: 1 },
      approvals: { state: "empty", items: [] },
      participation: { state: "empty", items: [] },
      issues: { state: "empty", items: [] },
      recognition: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
      attention: { state: "empty", items: [] },
      signals: { state: "empty", items: [] },
      next_action: { state: "empty", item: null },
    });
    for (const key of TEAM_OPS_PULSE_SECTION_KEYS) {
      expect(pulse).toHaveProperty(key);
    }
    expect(pulse.hero.overall_team_health?.band).toBe("healthy");
    expect((pulse.hero.overall_team_health as { score?: number }).score).toBeUndefined();
  });

  it("always emits seven life slices even when backend omits keys", () => {
    const life = parseBusinessLifeResponse({ active_moment_count: 1, moments: [], slices: {} });
    expect(Object.keys(life.slices)).toHaveLength(7);
    expect(life.slices.team_health.state).toBe("empty");
  });

  it("keeps optimistic merge + moment filter out of components", () => {
    const merged = mergeOptimisticEvents(
      [{ event_id: "1", action_type: "NOTE", title: "A" }],
      [{ event_id: "opt", action_type: "TEAM_UPDATE", title: "Just recorded" }],
    );
    expect(merged[0].event_id).toBe("opt");
    expect(
      filterEventsByMoment(
        [
          { event_id: "1", action_type: "NOTE", title: "A", source_moment_id: "m1" },
          { event_id: "2", action_type: "NOTE", title: "B", source_moment_id: "m2" },
        ],
        "m1",
      ),
    ).toHaveLength(1);
  });
});

describe("BusinessActiveRepository parsers", () => {
  beforeEach(() => {
    vi.mocked(requestWithRetry).mockClear();
  });

  it("returns parsed pulse from repository", async () => {
    const pulse = await getPulse("m1");
    expect(pulse.moment_id).toBe("m1");
    expect(pulse.kpis.members).toBe(0);
  });

  it("returns parsed life with all slice keys", async () => {
    const life = await getLife();
    expect(Object.keys(life.slices)).toHaveLength(7);
  });
});

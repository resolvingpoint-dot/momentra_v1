import { describe, expect, it } from "vitest";
import {
  toActivityViewModel,
  toLifeViewModel,
  toPulseViewModel,
} from "@/lib/business/teamOpsViewModels";
import type { BusinessLifeResponse, TeamOpsPulseResponse } from "@/lib/api/businessActive";

describe("teamOpsViewModels", () => {
  it("merges optimistic activity into pulse recent without inventing sections", () => {
    const pulse = {
      moment_id: "m1",
      moment_type: "TEAM_OPERATIONS",
      status: "active",
      is_active: true,
      hero: { state: "empty", title: "T" },
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
      approvals: { state: "empty", pending_count: 0, items: [] },
      participation: { state: "empty", count: 0, items: [] },
      issues: { state: "empty", open_count: 0, escalation_count: 0, items: [] },
      recognition: { state: "empty", count: 0, items: [] },
      recent_activity: {
        state: "complete",
        items: [{ event_id: "1", action_type: "NOTE", title: "Server" }],
      },
      attention: { state: "empty", items: [] },
      signals: { state: "empty", items: [] },
      next_action: { state: "empty", item: null },
    } as TeamOpsPulseResponse;

    const vm = toPulseViewModel(pulse, [
      { event_id: "opt", action_type: "TEAM_UPDATE", title: "Just recorded" },
    ]);
    expect(vm.recent_activity.items[0]?.event_id).toBe("opt");
    expect(vm.kpis.members).toBe(0);
  });

  it("filters life items by source moment in the ViewModel", () => {
    const life = {
      active_moment_count: 1,
      moments: [],
      slices: {
        team_health: {
          key: "team_health",
          label: "Team health",
          state: "complete",
          count: 2,
          items: [
            { event_id: "a", action_type: "NOTE", title: "A", source_moment_id: "m1" },
            { event_id: "b", action_type: "NOTE", title: "B", source_moment_id: "m2" },
          ],
        },
      },
    } as unknown as BusinessLifeResponse;
    const vm = toLifeViewModel(life, "m1");
    expect(vm.slices.team_health?.items).toHaveLength(1);
  });

  it("orders activity with optimistic first", () => {
    const items = toActivityViewModel(
      [{ event_id: "1", action_type: "NOTE", title: "A", is_editable: true, is_deletable: true, supported_actions: ["edit", "delete"] }],
      [{ event_id: "opt", action_type: "TEAM_UPDATE", title: "Just recorded" }],
    );
    expect(items[0]?.event_id).toBe("opt");
  });
});

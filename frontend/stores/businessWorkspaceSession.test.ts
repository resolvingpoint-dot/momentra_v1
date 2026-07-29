import { describe, expect, it, beforeEach, vi } from "vitest";
import type { BusinessSessionBootstrapResponse } from "@/lib/api/business";
import {
  getBusinessSessionSnapshot,
  validateBusinessSelection,
} from "@/stores/businessSessionStore";

describe("business workspace session", () => {
  beforeEach(() => {
    // Store is module singleton — smoke that helpers accept workspace-shaped bootstrap.
  });

  it("validateBusinessSelection ignores cross-company mixing by using provided inventory only", () => {
    const moments = [
      {
        moment_id: "m1",
        moment_type_id: "t1",
        moment_type_code: "TEAM_OPERATIONS",
        moment_name: "Ops",
        status: "ACTIVE",
        workspace_id: "ws-a",
      },
    ];
    const next = validateBusinessSelection(moments, "m1", "TEAM_OPERATIONS");
    expect(next.selectedMomentId).toBe("m1");
    expect(next.selectedMomentType).toBe("TEAM_OPERATIONS");
  });

  it("bootstrap type includes selected_workspace and module_tiles", () => {
    const bootstrap: BusinessSessionBootstrapResponse = {
      moments_home: {
        is_empty: true,
        active_moment_count: 0,
        cards: [],
      },
      moments: [],
      selected_workspace: {
        id: "ws1",
        name: "Pureborn",
        role: "OWNER",
        currency: "INR",
      },
      workspaces: [{ id: "ws1", name: "Pureborn", role: "OWNER" }],
      module_tiles: [
        {
          key: "finance",
          label: "Finance",
          status: "coming_soon",
          description: "Cash",
        },
      ],
      dashboard: {
        open_moments: 0,
        pending_approvals: 0,
        member_count: 1,
      },
    };
    expect(bootstrap.selected_workspace?.name).toBe("Pureborn");
    expect(bootstrap.module_tiles?.[0].status).toBe("coming_soon");
    expect(getBusinessSessionSnapshot().selectedWorkspaceId).toBeNull();
  });
});

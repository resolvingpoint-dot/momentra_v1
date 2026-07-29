import { describe, expect, it, vi, beforeEach } from "vitest";

vi.mock("@/lib/api/client", () => ({
  requestWithRetry: vi.fn(async (url: string) => {
    if (String(url).includes("/activity/e1")) {
      return {
        event_id: "e1",
        action_type: "TEAM_UPDATE",
        title: "Update",
        is_editable: true,
        is_deletable: true,
        supported_actions: ["edit", "delete"],
      };
    }
    if (String(url).includes("/activity")) {
      return {
        items: [
          {
            event_id: "e1",
            action_type: "TEAM_UPDATE",
            title: "Alpha update",
            occurred_at: "2026-07-15T12:00:00Z",
            is_editable: true,
            is_deletable: true,
            supported_actions: ["edit", "delete"],
          },
          {
            event_id: "e2",
            action_type: "ISSUE",
            title: "Broken pipe",
            occurred_at: "2026-07-14T12:00:00Z",
            is_editable: true,
            is_deletable: true,
            supported_actions: ["edit", "delete"],
          },
          {
            event_id: "e3",
            action_type: "APPROVAL_REQUEST",
            title: "Needs signoff",
            occurred_at: "2026-07-13T12:00:00Z",
            is_editable: false,
            is_deletable: false,
            supported_actions: [],
          },
        ],
        total: 3,
        page: 1,
        page_size: 20,
      };
    }
    if (String(url).endsWith("/pulse") || String(url).includes("/pulse?")) {
      return {
        moment_id: "m1",
        moment_type: "TEAM_OPERATIONS",
        status: "active",
        is_active: true,
        hero: { state: "empty", title: "Team" },
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
    return { url };
  }),
}));

vi.mock("@/repositories/BusinessRepository", () => ({
  BusinessRepository: {
    archiveMoment: vi.fn(async (id: string) => ({ id, archived: true })),
    completeMoment: vi.fn(async (id: string) => ({ id, completed: true })),
  },
}));

import { requestWithRetry } from "@/lib/api/client";
import {
  archiveMoment,
  completeMoment,
  getActivity,
  getPulse,
  listActivity,
  normalizeActivity,
} from "@/repositories/BusinessActiveRepository";
import { BusinessRepository } from "@/repositories/BusinessRepository";

describe("BusinessActiveRepository", () => {
  beforeEach(() => {
    vi.mocked(requestWithRetry).mockClear();
  });

  it("hits pulse with optional force refresh cache buster", async () => {
    await getPulse("m1");
    await getPulse("m1", true);
    const urls = vi.mocked(requestWithRetry).mock.calls.map((c) => String(c[0]));
    expect(urls[0]).toBe("/api/v1/business/active/m1/pulse");
    expect(urls[1]).toMatch(/\/pulse\?_refresh=/);
  });

  it("forwards filter/page query params to the server", async () => {
    const page = await listActivity(
      "m1",
      { actionTypes: ["ISSUE"], sort: "newest", status: "active" },
      { page: 1, pageSize: 10 },
    );
    const url = String(vi.mocked(requestWithRetry).mock.calls[0]?.[0]);
    expect(url).toContain("/api/v1/business/active/m1/activity?");
    expect(url).toContain("action=ISSUE");
    expect(url).toContain("status=active");
    expect(url).toContain("page=1");
    expect(url).toContain("page_size=10");
    expect(url).toContain("sort=newest");
    // Mock returns all three — server would filter; client must not re-filter.
    expect(page.items.length).toBe(3);
    expect(page.total).toBe(3);
  });

  it("uses server is_editable / is_deletable / supported_actions", async () => {
    const detail = await getActivity("m1", "e1");
    expect(detail.is_editable).toBe(true);
    expect(detail.is_deletable).toBe(true);
    expect(detail.supported_actions).toEqual(["edit", "delete"]);
  });

  it("does not invent permissions when API omits flags", () => {
    const item = normalizeActivity({
      event_id: "x",
      action_type: "APPROVAL_REQUEST",
      title: "Need sign",
      is_editable: false,
      is_deletable: false,
      supported_actions: [],
    });
    expect(item.is_editable).toBe(false);
    expect(item.is_deletable).toBe(false);
  });

  it("archive/complete delegate to BusinessRepository", async () => {
    await archiveMoment("m1");
    await completeMoment("m1");
    expect(BusinessRepository.archiveMoment).toHaveBeenCalledWith("m1");
    expect(BusinessRepository.completeMoment).toHaveBeenCalledWith("m1");
  });
});

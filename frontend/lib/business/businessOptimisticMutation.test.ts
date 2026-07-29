import { describe, expect, it } from "vitest";
import {
  applyBusinessMutationSuccess,
  normalizeMutationResponse,
  rollbackBusinessMutation,
} from "@/lib/business/businessOptimisticMutation";
import {
  peekBusinessPulseCache,
  seedBusinessPulseCache,
} from "@/hooks/useBusinessActiveTabs";

describe("businessOptimisticMutation", () => {
  it("normalizes wrapped mutation response", () => {
    const n = normalizeMutationResponse({
      activity: { event_id: "e1", action_type: "UPDATE", title: "Hi" },
      projection_hint: { op: "create", counters: { activity_delta: 1 } },
    });
    expect(n?.activity.event_id).toBe("e1");
    expect(n?.projection_hint?.op).toBe("create");
  });

  it("patches pulse recent_activity without clearing cache", () => {
    const momentId = "m-opt";
    seedBusinessPulseCache(momentId, {
      moment_id: momentId,
      moment_type: "TEAM_OPERATIONS",
      status: "ACTIVE",
      is_active: true,
      hero_title: "Team",
      recent_activity: {
        state: "ready",
        data: { items: [] },
      },
    } as never);

    const item = applyBusinessMutationSuccess({
      momentId,
      momentTypeCode: "TEAM_OPERATIONS",
      response: {
        activity: {
          event_id: "e-new",
          action_type: "TEAM_UPDATE",
          title: "Done",
          occurred_at: "2026-01-01T00:00:00Z",
          business_moment_id: momentId,
          client_request_id: "cr-1",
        },
        projection_hint: { op: "create", counters: { activity_delta: 1 } },
      },
    });
    expect(item?.event_id).toBe("e-new");
    const pulse = peekBusinessPulseCache(momentId, "TEAM_OPERATIONS");
    const items = (pulse as { recent_activity?: { data?: { items?: { event_id: string }[] } } })
      ?.recent_activity?.data?.items;
    expect(items?.[0]?.event_id).toBe("e-new");

    rollbackBusinessMutation("cr-1");
    const rolled = peekBusinessPulseCache(momentId, "TEAM_OPERATIONS");
    const rolledItems = (
      rolled as { recent_activity?: { data?: { items?: unknown[] } } }
    )?.recent_activity?.data?.items;
    expect(rolledItems?.length ?? 0).toBe(0);
  });
});

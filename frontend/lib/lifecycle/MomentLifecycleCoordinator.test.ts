import { describe, expect, it, vi, beforeEach } from "vitest";
import {
  LIFECYCLE_DISPATCH,
  pickReplacementLocally,
  runMomentLifecycle,
} from "@/lib/lifecycle/MomentLifecycleCoordinator";

vi.mock("@/repositories/PersonalRepository", () => ({
  PersonalRepository: {
    patchMoment: vi.fn(async () => ({ moment_id: "p1", status: "PAUSED" })),
    archiveTemplateMoment: vi.fn(async () => ({ moment_id: "p1", status: "ARCHIVED" })),
    completeTemplateMoment: vi.fn(async () => ({ moment_id: "p1", status: "COMPLETED" })),
  },
}));

vi.mock("@/repositories/GroupRepository", () => ({
  GroupRepository: {
    patchMoment: vi.fn(async () => ({ moment_id: "g1", status: "PAUSED" })),
    archiveMoment: vi.fn(async () => ({
      moment_id: "g1",
      status: "ARCHIVED",
      replacement_moment_id: "g2",
      replacement_moment_type_code: "SHARED_PURCHASE",
    })),
    completeMoment: vi.fn(async () => ({ moment_id: "g1", status: "COMPLETED" })),
  },
}));

vi.mock("@/repositories/BusinessRepository", () => ({
  BusinessRepository: {
    patchMoment: vi.fn(async () => ({ moment_id: "b1", status: "PAUSED" })),
    archiveMoment: vi.fn(async () => ({ moment_id: "b1", status: "ARCHIVED" })),
    completeMoment: vi.fn(async () => ({ moment_id: "b1", status: "COMPLETED" })),
  },
}));

vi.mock("@/stores/bootstrapStore", () => ({
  invalidateBootstrapAfterMutation: vi.fn(),
  notifyMomentMutation: vi.fn(),
}));

describe("MomentLifecycleCoordinator", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("dispatch table never cross-wires contexts", () => {
    expect(LIFECYCLE_DISPATCH.PERSONAL).toBe("PersonalRepository");
    expect(LIFECYCLE_DISPATCH.GROUP).toBe("GroupRepository");
    expect(LIFECYCLE_DISPATCH.BUSINESS).toBe("BusinessRepository");
  });

  it("pickReplacementLocally skips archived and prefers ACTIVE", () => {
    const r = pickReplacementLocally(
      [
        { momentId: "a", momentTypeCode: "X", status: "ARCHIVED" },
        { momentId: "b", momentTypeCode: "Y", status: "PAUSED" },
        { momentId: "c", momentTypeCode: "Z", status: "ACTIVE" },
      ],
      { excludeId: "a" },
    );
    expect(r.momentId).toBe("c");
  });

  it("Business archive uses BusinessRepository not Group", async () => {
    const { BusinessRepository } = await import("@/repositories/BusinessRepository");
    const { GroupRepository } = await import("@/repositories/GroupRepository");
    await runMomentLifecycle({
      contextType: "BUSINESS",
      momentId: "b1",
      momentTypeCode: "TEAM_OPERATIONS",
      action: "archive",
      previousStatus: "ACTIVE",
      inventory: [
        { momentId: "b1", momentTypeCode: "TEAM_OPERATIONS", status: "ACTIVE" },
        { momentId: "b2", momentTypeCode: "BUSINESS_RUNWAY", status: "ACTIVE" },
      ],
      selectedMomentId: "b1",
    });
    expect(BusinessRepository.archiveMoment).toHaveBeenCalledWith("b1");
    expect(GroupRepository.archiveMoment).not.toHaveBeenCalled();
  });

  it("Group archive uses GroupRepository and respects backend replacement", async () => {
    const { GroupRepository } = await import("@/repositories/GroupRepository");
    const result = await runMomentLifecycle({
      contextType: "GROUP",
      momentId: "g1",
      momentTypeCode: "SHARED_EXPERIENCE",
      action: "archive",
      previousStatus: "ACTIVE",
      inventory: [
        { momentId: "g1", momentTypeCode: "SHARED_EXPERIENCE", status: "ACTIVE" },
        { momentId: "g2", momentTypeCode: "SHARED_PURCHASE", status: "ACTIVE" },
      ],
      selectedMomentId: "g1",
    });
    expect(GroupRepository.archiveMoment).toHaveBeenCalledWith("g1");
    expect(result.replacementMomentId).toBe("g2");
  });
});

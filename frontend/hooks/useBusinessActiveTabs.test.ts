import { describe, expect, it } from "vitest";
import {
  BUSINESS_ACTIVE_REFRESH_SURFACES,
  __seedBusinessActiveCachesForTest,
  businessActiveCacheSnapshot,
  businessCacheKey,
  businessDedupeMetrics,
  invalidateBusinessActiveCaches,
} from "@/hooks/useBusinessActiveTabs";

describe("useBusinessActiveTabs cache keys", () => {
  it("builds user-scoped TEAM_OPERATIONS keys", () => {
    expect(businessCacheKey("u1", ["m1", "TEAM_OPERATIONS", "pulse"])).toBe(
      "business:u1:m1:TEAM_OPERATIONS:pulse",
    );
    expect(businessCacheKey("u1", ["m1", "BUSINESS_OPERATIONS", "pulse"])).toBe(
      "business:u1:m1:BUSINESS_OPERATIONS:pulse",
    );
    expect(businessCacheKey(null, ["life"])).toBe("business:anon:life");
  });

  it("exposes dedupe metrics including activityDetail", () => {
    expect(Object.keys(businessDedupeMetrics).sort()).toEqual([
      "activity",
      "activityDetail",
      "life",
      "memory",
      "moments",
      "pulse",
    ]);
  });

  it("invalidates without throwing", () => {
    expect(() => invalidateBusinessActiveCaches("m1", "u1")).not.toThrow();
  });

  it("submit refresh clears Activity, Pulse, Moments, Life, and Memory", () => {
    expect([...BUSINESS_ACTIVE_REFRESH_SURFACES]).toEqual([
      "activity",
      "pulse",
      "moments",
      "life",
      "memory",
    ]);

    __seedBusinessActiveCachesForTest("m1", "u1");
    expect(businessActiveCacheSnapshot("m1", "u1")).toEqual({
      activity: true,
      pulse: true,
      moments: true,
      life: true,
      memory: true,
    });

    invalidateBusinessActiveCaches("m1", "u1");

    expect(businessActiveCacheSnapshot("m1", "u1")).toEqual({
      activity: false,
      pulse: false,
      moments: false,
      life: false,
      memory: false,
    });
  });
});

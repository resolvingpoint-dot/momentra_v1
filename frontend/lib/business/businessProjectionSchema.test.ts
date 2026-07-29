import { describe, expect, it } from "vitest";
import { businessProjectionSchemaSegment } from "@/lib/business/businessProjectionSchema";
import { businessCacheKey } from "@/hooks/useBusinessActiveTabs";
import {
  getBusinessLoadMetricsSnapshot,
  logBusinessLoad,
  resetBusinessLoadMetrics,
} from "@/lib/telemetry/businessLoadTelemetry";

describe("Business projection schema cache keys", () => {
  it("embeds schema version in businessCacheKey", () => {
    const key = businessCacheKey("u1", ["mid", "TEAM_OPERATIONS", "pulse"]);
    expect(key.startsWith(`business:${businessProjectionSchemaSegment()}:`)).toBe(
      true,
    );
    expect(key).toContain("u1");
    expect(key).toContain("pulse");
  });
});

describe("BusinessLoad metrics aggregator", () => {
  it("counts ACTIVE bootstrap without create-options and tab network hits", () => {
    resetBusinessLoadMetrics();
    logBusinessLoad({
      tab: "session",
      requestKey: "session_bootstrap",
      cacheSource: "network",
      durationMs: 40,
      success: true,
    });
    logBusinessLoad({
      tab: "moments",
      requestKey: "fetch:…:moments",
      cacheSource: "network",
      durationMs: 120,
      success: true,
    });
    logBusinessLoad({
      tab: "moments",
      requestKey: "fetch:…:moments",
      cacheSource: "memory",
      reason: "fresh_ttl",
      durationMs: 0,
      success: true,
    });
    const snap = getBusinessLoadMetricsSnapshot();
    expect(snap.bootstrapNetwork).toBe(1);
    expect(snap.createOptionsNetwork).toBe(0);
    expect(snap.momentsNetwork).toBe(1);
    expect(snap.momentsMemoryHit).toBe(1);
  });
});

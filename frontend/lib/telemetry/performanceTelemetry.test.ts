import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  clearPerformanceTelemetry,
  endSpan,
  getRecentSpans,
  recordResponseHeaders,
  startLoginToPulseSpan,
  endLoginToPulseSpan,
  startSpan,
} from "@/lib/telemetry/performanceTelemetry";

describe("performanceTelemetry", () => {
  beforeEach(() => {
    clearPerformanceTelemetry();
    vi.stubGlobal("performance", { now: vi.fn(() => 1000) });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("records span duration on end", () => {
    const perf = performance as unknown as { now: ReturnType<typeof vi.fn> };
    perf.now.mockReturnValueOnce(1000).mockReturnValueOnce(1250);

    const spanId = startSpan("bootstrap.load", { force: true });
    const completed = endSpan(spanId);

    expect(completed?.name).toBe("bootstrap.load");
    expect(completed?.durationMs).toBe(250);
    expect(getRecentSpans()[0]?.metadata).toEqual({ force: true });
  });

  it("attaches response headers to an active span", () => {
    const spanId = startSpan("quick_add.save");
    const response = new Response(null, {
      headers: {
        "X-Request-ID": "req-123",
        "X-Duration-Ms": "42.5",
        "X-Cache-Hit": "true",
        "X-Projection-Version": "7",
      },
    });
    recordResponseHeaders(response, spanId);
    const completed = endSpan(spanId);

    expect(completed?.requestId).toBe("req-123");
    expect(completed?.serverDurationMs).toBe(42.5);
    expect(completed?.serverCacheHit).toBe(true);
    expect(completed?.projectionVersion).toBe(7);
  });

  it("tracks login.to_pulse as a single session span", () => {
    const perf = performance as unknown as { now: ReturnType<typeof vi.fn> };
    perf.now.mockReturnValueOnce(1000).mockReturnValueOnce(1700);

    startLoginToPulseSpan();
    startLoginToPulseSpan();

    const completed = endLoginToPulseSpan();
    expect(completed?.name).toBe("login.to_pulse");
    expect(completed?.durationMs).toBe(700);
    expect(endLoginToPulseSpan()).toBeNull();
  });
});

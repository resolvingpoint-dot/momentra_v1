import { describe, expect, it, beforeEach, vi } from "vitest";

const endSpan = vi.fn();
const startSpan = vi.fn((..._args: unknown[]) => `span-${Math.random()}`);

vi.mock("@/lib/telemetry/performanceTelemetry", () => ({
  startSpan: (name: string, metadata?: Record<string, unknown>) => startSpan(name, metadata),
  endSpan: (id: string, extra?: Record<string, unknown>) => endSpan(id, extra),
}));

describe("businessSetupTelemetry", () => {
  beforeEach(() => {
    vi.resetModules();
    startSpan.mockClear();
    endSpan.mockClear();
    startSpan.mockImplementation(() => `span-${Math.random()}`);
  });

  it("records create → first paint → get → bootstrap spans in order", async () => {
    const {
      beginBusinessSetupOpen,
      markBusinessSetupCreateDone,
      markBusinessSetupFirstPaint,
      markBusinessSetupGetDone,
      markBusinessSetupBootstrapDone,
    } = await import("@/lib/telemetry/businessSetupTelemetry");

    beginBusinessSetupOpen({ moment_type_code: "TEAM_OPERATIONS" });
    expect(startSpan).toHaveBeenCalledWith(
      "business_setup_total_open",
      expect.objectContaining({ metric: "business_setup_total_open_ms" }),
    );
    expect(startSpan).toHaveBeenCalledWith(
      "business_setup_create",
      expect.objectContaining({ metric: "business_setup_create_ms" }),
    );

    markBusinessSetupCreateDone("m1");
    expect(endSpan).toHaveBeenCalled();
    expect(startSpan).toHaveBeenCalledWith(
      "business_setup_first_paint",
      expect.objectContaining({ metric: "business_setup_first_paint_ms" }),
    );
    expect(startSpan).toHaveBeenCalledWith(
      "business_setup_get",
      expect.objectContaining({ metric: "business_setup_get_ms" }),
    );

    markBusinessSetupFirstPaint();
    expect(startSpan).toHaveBeenCalledWith(
      "business_setup_bootstrap_refresh",
      expect.objectContaining({ metric: "business_setup_bootstrap_refresh_ms" }),
    );

    markBusinessSetupGetDone({ cache: "create_seed" });
    markBusinessSetupBootstrapDone();
    expect(endSpan.mock.calls.length).toBeGreaterThanOrEqual(4);
    expect(endSpan).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        metadata: expect.objectContaining({ cache: "create_seed", metric: "business_setup_get_ms" }),
      }),
    );
  });
});

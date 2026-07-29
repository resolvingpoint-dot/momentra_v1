/** @vitest-environment jsdom */
import { act, useEffect } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { BusinessSetupPreview, BusinessSetupState } from "@/lib/api/business";

const getSetupState = vi.fn();
const saveDraft = vi.fn();
const preview = vi.fn();
const activate = vi.fn();

vi.mock("@/repositories/BusinessSetupRepository", () => ({
  BusinessSetupRepository: {
    getSetupState: (...args: unknown[]) => getSetupState(...args),
    saveDraft: (...args: unknown[]) => saveDraft(...args),
    preview: (...args: unknown[]) => preview(...args),
    activate: (...args: unknown[]) => activate(...args),
  },
}));

vi.mock("@/lib/telemetry/businessSetupTelemetry", () => ({
  markBusinessSetupGetDone: vi.fn(),
}));

import { useBusinessSetupFlow } from "@/hooks/useBusinessSetupFlow";

const seed: BusinessSetupState = {
  moment_id: "m-seed",
  moment_type_code: "TEAM_OPERATIONS",
  status: "DRAFT",
  template_id: "team_ops",
  template_version: "1",
  setup_version: "1",
  answers: {
    moment_name: "Seeded",
    members: [{ local_id: "o1", role: "OWNER", name: "Owner" }],
  },
  progress: { current_step: 1, completed_steps: [] },
};

function HookProbe({
  momentId,
  initialSetup,
  onSnap,
}: {
  momentId: string | null;
  initialSetup?: BusinessSetupState | null;
  onSnap: (snap: ReturnType<typeof useBusinessSetupFlow>) => void;
}) {
  const flow = useBusinessSetupFlow(momentId, { initialSetup });
  useEffect(() => {
    onSnap(flow);
  });
  return null;
}

describe("useBusinessSetupFlow", () => {
  let container: HTMLDivElement;
  let root: Root;
  let latest: ReturnType<typeof useBusinessSetupFlow> | null = null;

  beforeEach(() => {
    (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    vi.useFakeTimers();
    getSetupState.mockReset();
    saveDraft.mockReset();
    preview.mockReset();
    activate.mockReset();
    getSetupState.mockResolvedValue(seed);
    saveDraft.mockImplementation(async (_id: string, answers: Record<string, unknown>) => ({
      ...seed,
      answers,
    }));
    preview.mockResolvedValue({
      summary_blocks: [],
      warnings: [],
      activation_ready: true,
    } satisfies BusinessSetupPreview);
    activate.mockResolvedValue({
      moment_id: "m-seed",
      moment_type_code: "TEAM_OPERATIONS",
      status: "ACTIVE",
    });
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    latest = null;
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
    vi.useRealTimers();
  });

  function mount(momentId: string | null, initialSetup?: BusinessSetupState | null) {
    act(() => {
      root.render(
        <HookProbe
          momentId={momentId}
          initialSetup={initialSetup}
          onSnap={(s) => {
            latest = s;
          }}
        />,
      );
    });
  }

  it("skips GET when create seed matches momentId", async () => {
    mount("m-seed", seed);
    await act(async () => {
      await Promise.resolve();
    });
    expect(getSetupState).not.toHaveBeenCalled();
    expect(latest?.setup?.moment_id).toBe("m-seed");
    expect(latest?.answers.moment_name).toBe("Seeded");
    expect(latest?.loading).toBe(false);
  });

  it("loads GET when resume has no seed", async () => {
    mount("m-seed", null);
    await act(async () => {
      await Promise.resolve();
    });
    expect(getSetupState).toHaveBeenCalledWith("m-seed");
  });

  it("updateAnswer autosaves draft but does not preview", async () => {
    mount("m-seed", seed);
    await act(async () => {
      await Promise.resolve();
    });
    act(() => {
      latest!.updateAnswer("team_purpose", "Ship");
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(450);
    });
    expect(saveDraft).toHaveBeenCalled();
    expect(preview).not.toHaveBeenCalled();
  });

  it("requestPreview calls preview API on demand", async () => {
    mount("m-seed", seed);
    await act(async () => {
      await Promise.resolve();
    });
    await act(async () => {
      await latest!.requestPreview();
    });
    expect(preview).toHaveBeenCalledTimes(1);
    expect(latest?.preview?.activation_ready).toBe(true);
  });

  it("flushPendingSave cancels debounce and saves immediately", async () => {
    mount("m-seed", seed);
    await act(async () => {
      await Promise.resolve();
    });
    act(() => {
      latest!.updateAnswer("team_purpose", "Flush me");
    });
    expect(latest?.saveStatus).toBe("dirty");
    await act(async () => {
      await latest!.flushPendingSave();
    });
    expect(saveDraft).toHaveBeenCalled();
    expect(latest?.saveStatus).toBe("saved");
  });

  it("activate succeeds when draft save says moment already active", async () => {
    mount("m-seed", { ...seed, status: "ACTIVE" });
    await act(async () => {
      await Promise.resolve();
    });
    let ok = false;
    await act(async () => {
      ok = await latest!.activate();
    });
    expect(saveDraft).not.toHaveBeenCalled();
    expect(activate).toHaveBeenCalledWith("m-seed");
    expect(ok).toBe(true);
    expect(latest?.error).toBeNull();
  });

  it("activate tolerates activated-draft 400 then continues", async () => {
    const { ApiError } = await import("@/lib/api/client");
    saveDraft.mockRejectedValueOnce(
      new ApiError("Cannot save draft for an activated moment", 400),
    );
    mount("m-seed", seed);
    await act(async () => {
      await Promise.resolve();
    });
    let ok = false;
    await act(async () => {
      ok = await latest!.activate();
    });
    expect(activate).toHaveBeenCalledWith("m-seed");
    expect(ok).toBe(true);
    expect(latest?.error).toBeNull();
  });
});

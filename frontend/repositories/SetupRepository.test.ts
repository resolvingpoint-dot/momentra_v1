import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api/client", () => ({
  createPersonalMoment: vi.fn(),
  getPersonalMomentSetup: vi.fn(),
  previewPersonalSetup: vi.fn(),
  savePersonalSetupDraft: vi.fn(),
  submitPersonalSetup: vi.fn(),
}));

vi.mock("@/stores/bootstrapStore", () => ({
  invalidateBootstrapAfterMutation: vi.fn(),
  notifyMomentMutation: vi.fn(),
}));

import {
  createPersonalMoment,
  previewPersonalSetup,
  savePersonalSetupDraft,
  submitPersonalSetup,
} from "@/lib/api/client";
import {
  invalidateBootstrapAfterMutation,
  notifyMomentMutation,
} from "@/stores/bootstrapStore";

import { SetupRepository } from "./SetupRepository";

describe("SetupRepository", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("saveDraft and preview do not invalidate bootstrap", async () => {
    vi.mocked(savePersonalSetupDraft).mockResolvedValue({} as never);
    vi.mocked(previewPersonalSetup).mockResolvedValue({} as never);

    await SetupRepository.saveDraft("moment-1", {});
    await SetupRepository.preview("moment-1", {});

    expect(invalidateBootstrapAfterMutation).not.toHaveBeenCalled();
    expect(notifyMomentMutation).not.toHaveBeenCalled();
  });

  it("createDraft and activate soft-refresh sessions instead of full bootstrap", async () => {
    vi.mocked(createPersonalMoment).mockResolvedValue({} as never);
    vi.mocked(submitPersonalSetup).mockResolvedValue({} as never);

    await SetupRepository.createDraft({ moment_type_code: "FUTURE_BUILDING" });
    await SetupRepository.activate("moment-1", {});

    expect(invalidateBootstrapAfterMutation).not.toHaveBeenCalled();
    expect(notifyMomentMutation).toHaveBeenCalledTimes(2);
    expect(notifyMomentMutation).toHaveBeenCalledWith(
      "PERSONAL",
      expect.objectContaining({ contextState: "SETUP" }),
    );
    expect(notifyMomentMutation).toHaveBeenCalledWith(
      "PERSONAL",
      expect.objectContaining({ contextState: "ACTIVE" }),
    );
  });
});

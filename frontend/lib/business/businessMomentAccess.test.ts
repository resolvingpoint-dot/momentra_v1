import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  clearBusinessMomentReseatMarks,
  isBusinessMomentAccessDenied,
  isBusinessMomentAccessDeniedMessage,
} from "@/lib/business/businessMomentAccess";
import { ApiError } from "@/lib/api/client";

describe("businessMomentAccess", () => {
  beforeEach(() => {
    clearBusinessMomentReseatMarks();
  });

  it("detects invalid_member ApiError and membership messages", () => {
    expect(
      isBusinessMomentAccessDenied(
        new ApiError("User is not a member of this business moment.", 403, "invalid_member"),
      ),
    ).toBe(true);
    expect(isBusinessMomentAccessDeniedMessage("User is not a member of this business moment.")).toBe(
      true,
    );
    expect(isBusinessMomentAccessDenied(new ApiError("timeout", 408))).toBe(false);
  });
});

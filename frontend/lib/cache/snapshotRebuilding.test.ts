import { describe, expect, it } from "vitest";
import { ApiError, ApiErrorCode } from "@/lib/api/client";
import { isSnapshotRebuilding } from "@/lib/cache/snapshotRebuilding";

describe("isSnapshotRebuilding", () => {
  it("matches snapshot_rebuilding code", () => {
    expect(
      isSnapshotRebuilding(
        new ApiError("Rebuilding", 503, ApiErrorCode.SNAPSHOT_REBUILDING),
      ),
    ).toBe(true);
  });

  it("matches 503 with rebuild/snapshot message", () => {
    expect(isSnapshotRebuilding(new ApiError("snapshot rebuild in progress", 503))).toBe(
      true,
    );
  });

  it("rejects unrelated errors", () => {
    expect(isSnapshotRebuilding(new ApiError("Not found", 404))).toBe(false);
    expect(isSnapshotRebuilding(new Error("network"))).toBe(false);
  });
});

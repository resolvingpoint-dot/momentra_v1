import { ApiError } from "@/lib/api/client";

/** Max force-load retries while the backend rebuilds personal snapshots. */
export const SNAPSHOT_REBUILDING_MAX_ATTEMPTS = 6;
export const SNAPSHOT_REBUILDING_DELAY_MS = 1500;

export function isSnapshotRebuilding(err: unknown): boolean {
  if (!(err instanceof ApiError)) return false;
  if (err.code === "snapshot_rebuilding") return true;
  return (
    err.status === 503 &&
    /rebuild|snapshot/i.test(err.message || "")
  );
}

export function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

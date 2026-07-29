import { useSyncExternalStore } from "react";
import {
  CircleRepository,
  type CircleParticipantEntry,
  type CircleRecentActivity,
  type CircleSuggestion,
} from "@/repositories/CircleRepository";

const FRESH_MS = 60_000;

export type CircleSessionSnapshot = {
  participants: CircleParticipantEntry[];
  suggestions: CircleSuggestion[];
  recentActivity: CircleRecentActivity[];
  participantCount: number;
  activeParticipantCount: number;
  loading: boolean;
  error: string | null;
  lastLoadedAt: number | null;
  generation: number;
};

let snapshot: CircleSessionSnapshot = {
  participants: [],
  suggestions: [],
  recentActivity: [],
  participantCount: 0,
  activeParticipantCount: 0,
  loading: false,
  error: null,
  lastLoadedAt: null,
  generation: 0,
};

const listeners = new Set<() => void>();

function emit() {
  for (const listener of listeners) listener();
}

function setSnapshot(partial: Partial<CircleSessionSnapshot>) {
  snapshot = { ...snapshot, ...partial };
  emit();
}

function applyRead(
  data: Awaited<ReturnType<typeof CircleRepository.read>>,
  generation: number,
) {
  if (generation !== snapshot.generation) return;
  const participants = data.participants ?? [];
  const activeCount = participants.filter(
    (p) => p.participant.is_active !== false,
  ).length;
  setSnapshot({
    participants,
    suggestions: data.suggestions ?? [],
    recentActivity: data.recent_activity ?? [],
    participantCount: participants.length,
    activeParticipantCount: activeCount,
    loading: false,
    error: null,
    lastLoadedAt: Date.now(),
  });
}

export function getCircleSessionSnapshot(): CircleSessionSnapshot {
  return snapshot;
}

export function subscribeCircleSession(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useCircleSessionStore(): CircleSessionSnapshot {
  return useSyncExternalStore(
    subscribeCircleSession,
    getCircleSessionSnapshot,
    getCircleSessionSnapshot,
  );
}

let inFlight: Promise<void> | null = null;
let bgRefreshInFlight: Promise<void> | null = null;

/**
 * Read-first when snapshots exist (fast updated paint).
 * If read is empty, await refresh + re-read so Circle can populate from
 * Group/Business members instead of sticking on the empty screen.
 */
export async function ensureCircleSession(force = false): Promise<void> {
  const now = Date.now();
  // Never treat an empty Circle as fresh — snapshots may still need refresh.
  const isFresh =
    !force &&
    snapshot.lastLoadedAt != null &&
    now - snapshot.lastLoadedAt < FRESH_MS &&
    !snapshot.error &&
    snapshot.participantCount > 0;
  if (isFresh) return;
  if (inFlight && !force) return inFlight;

  const generation = snapshot.generation + 1;
  setSnapshot({ loading: true, error: null, generation });

  inFlight = (async () => {
    try {
      const data = await CircleRepository.read();
      if (generation !== snapshot.generation) return;

      const count = data.participants?.length ?? 0;
      if (count === 0) {
        // Cold / stale empty: rebuild snapshots before deciding empty vs updated.
        try {
          await CircleRepository.refresh();
        } catch {
          // Refresh is best-effort; re-read whatever is on disk.
        }
        if (generation !== snapshot.generation) return;
        const again = await CircleRepository.read();
        applyRead(again, generation);
        return;
      }

      applyRead(data, generation);
      void backgroundRefresh(generation);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Couldn't load Circle";
      if (generation === snapshot.generation) {
        setSnapshot({ loading: false, error: message });
      }
    } finally {
      inFlight = null;
    }
  })();

  return inFlight;
}

async function backgroundRefresh(generation: number): Promise<void> {
  if (bgRefreshInFlight) return bgRefreshInFlight;
  bgRefreshInFlight = (async () => {
    try {
      try {
        await CircleRepository.refresh();
      } catch {
        // Soft refresh — keep first paint.
      }
      if (generation !== snapshot.generation) return;
      const data = await CircleRepository.read();
      applyRead(data, generation);
    } catch {
      // Soft background failure — leave first-paint data in place.
    } finally {
      bgRefreshInFlight = null;
    }
  })();
  return bgRefreshInFlight;
}

export function resetCircleSession() {
  snapshot = {
    participants: [],
    suggestions: [],
    recentActivity: [],
    participantCount: 0,
    activeParticipantCount: 0,
    loading: false,
    error: null,
    lastLoadedAt: null,
    generation: snapshot.generation + 1,
  };
  emit();
}

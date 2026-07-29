/**
 * Authoritative Life 360 store.
 *
 * Owns: snapshot, analytics, empty/full state, load state, lastLoadedAt, generation.
 * Paint from GET /read (+ /analytics); POST /refresh is soft background reconcile only.
 */
import { useSyncExternalStore } from "react";
import { dedupeFetch } from "@/lib/cache/cacheStore";
import {
  Life360Repository,
  isLife360EmptyState,
  type Life360AnalyticsResponse,
  type Life360Snapshot,
} from "@/repositories/Life360Repository";

const FRESH_MS = 60_000;
const EMPTY_CONFIDENCE = 25;

export type Life360ViewState = "empty" | "full";

export type Life360StoreSnapshot = {
  snapshot: Life360Snapshot | null;
  analytics: Life360AnalyticsResponse | null;
  viewState: Life360ViewState | null;
  loading: boolean;
  refreshing: boolean;
  error: string | null;
  lastLoadedAt: number | null;
  generation: number;
};

let store: Life360StoreSnapshot = {
  snapshot: null,
  analytics: null,
  viewState: null,
  loading: false,
  refreshing: false,
  error: null,
  lastLoadedAt: null,
  generation: 0,
};

const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((fn) => fn());
}

function setStore(patch: Partial<Life360StoreSnapshot>) {
  store = { ...store, ...patch };
  notify();
}

export function getLife360Snapshot(): Life360StoreSnapshot {
  return store;
}

export function subscribeLife360(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useLife360Store(): Life360StoreSnapshot {
  return useSyncExternalStore(subscribeLife360, getLife360Snapshot, getLife360Snapshot);
}

export function bumpLife360Generation(): number {
  const next = store.generation + 1;
  setStore({ generation: next });
  return next;
}

function confidenceOf(snapshot: Life360Snapshot | null | undefined): number | null {
  return Life360Repository.toNumber(snapshot?.signal_confidence_score);
}

function applyFromSnapshot(
  snapshot: Life360Snapshot,
  analytics: Life360AnalyticsResponse | null,
): void {
  const confidence = confidenceOf(snapshot);
  if (confidence != null && confidence < EMPTY_CONFIDENCE) {
    setStore({
      snapshot,
      analytics: null,
      viewState: "empty",
      lastLoadedAt: Date.now(),
      error: null,
      loading: false,
    });
    return;
  }
  setStore({
    snapshot,
    analytics,
    viewState: "full",
    lastLoadedAt: Date.now(),
    error: null,
    loading: false,
  });
}

/** Shell/overlay entry — single-flight read path with 60s TTL. */
export async function ensureLife360(force = false): Promise<void> {
  const fresh =
    !force &&
    store.viewState != null &&
    store.lastLoadedAt != null &&
    Date.now() - store.lastLoadedAt < FRESH_MS &&
    store.error == null;
  if (fresh) return;

  setStore({ loading: store.viewState == null, error: null });
  try {
    await dedupeFetch("life360:ensure", async () => {
      try {
        const [snapshot, analytics] = await Promise.all([
          Life360Repository.read(),
          Life360Repository.analytics().catch(() => null),
        ]);
        applyFromSnapshot(snapshot, analytics);
        return true;
      } catch {
        const home = await Life360Repository.getHome().catch(() => null);
        if (home && !isLife360EmptyState(home.state)) {
          setStore({
            loading: false,
            error: "Could not load Life 360 snapshot",
          });
          return false;
        }
        setStore({
          snapshot: null,
          analytics: null,
          viewState: "empty",
          lastLoadedAt: Date.now(),
          error: null,
          loading: false,
        });
        return true;
      }
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Could not load Life 360";
    setStore({ loading: false, error: message });
  }
}

/** Soft background refresh — never blocks first paint. */
export async function softRefreshLife360(): Promise<void> {
  const gen = store.generation;
  setStore({ refreshing: true });
  try {
    const refreshed = await Life360Repository.refresh().catch(() => null);
    if (gen !== store.generation) return;

    let snapshot = refreshed?.snapshot ?? null;
    if (!snapshot) {
      snapshot = await Life360Repository.read().catch(() => null);
    }
    if (gen !== store.generation) return;

    if (!snapshot) {
      const home = await Life360Repository.getHome().catch(() => null);
      if (home && isLife360EmptyState(home.state)) {
        setStore({
          viewState: "empty",
          snapshot: null,
          analytics: null,
          lastLoadedAt: Date.now(),
          refreshing: false,
        });
      }
      return;
    }

    const analytics = await Life360Repository.analytics().catch(() => null);
    if (gen !== store.generation) return;
    applyFromSnapshot(snapshot, analytics);
  } finally {
    if (gen === store.generation) {
      setStore({ refreshing: false });
    }
  }
}

export async function retryLife360(): Promise<void> {
  bumpLife360Generation();
  await ensureLife360(true);
  void softRefreshLife360();
}

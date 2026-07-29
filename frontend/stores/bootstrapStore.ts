import { AppRepository } from "@/repositories/AppRepository";
import {
  cacheFetch,
  cacheInvalidate,
  cachePeek,
  cacheSet,
  diskCacheClearAll,
  diskCacheLoad,
  diskCacheSave,
  diskCacheRemove,
} from "@/lib/cache/cacheStore";
import type {
  BootstrapPreferences,
  BootstrapResponse,
  BootstrapVersionFields,
} from "@/lib/api/bootstrapTypes";
import { endSpan, startSpan } from "@/lib/telemetry/performanceTelemetry";

const CACHE_KEY = "app:bootstrap";
const DISK_KEY = "app_bootstrap";
const VERSION_DISK_KEY = "app_bootstrap_versions";

type BootstrapSnapshot = {
  data: BootstrapResponse | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  hasLoadedOnce: boolean;
};

const diskCached = diskCacheLoad<BootstrapResponse>(DISK_KEY);

let snapshot: BootstrapSnapshot = {
  data: diskCached,
  isLoading: false,
  isRefreshing: false,
  error: null,
  hasLoadedOnce: diskCached !== null,
};

/** Monotonic fetch / apply generation for last-write-wins preference merges. */
let bootstrapFetchGen = 0;
let bootstrapAppliedGen = 0;

const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((fn) => fn());
}

function setSnapshot(patch: Partial<BootstrapSnapshot>) {
  snapshot = { ...snapshot, ...patch };
  notify();
}

function preferenceTimestamp(prefs: BootstrapPreferences | undefined): number {
  if (!prefs?.updated_at) return 0;
  const t = Date.parse(prefs.updated_at);
  return Number.isFinite(t) ? t : 0;
}

/**
 * Merge an incoming bootstrap payload with the current snapshot so a stale
 * GET cannot erase a newer preference write-through.
 */
function mergeBootstrapApply(
  incoming: BootstrapResponse,
  fetchGen: number,
): BootstrapResponse | null {
  if (fetchGen < bootstrapAppliedGen) {
    return null;
  }
  const current = snapshot.data;
  if (!current) {
    bootstrapAppliedGen = Math.max(bootstrapAppliedGen, fetchGen);
    return incoming;
  }
  const incomingTs = preferenceTimestamp(incoming.preferences);
  const currentTs = preferenceTimestamp(current.preferences);
  // Prefer locally write-through prefs when they are newer than the GET payload.
  const next: BootstrapResponse =
    currentTs > incomingTs
      ? { ...incoming, preferences: current.preferences }
      : incoming;

  bootstrapAppliedGen = Math.max(bootstrapAppliedGen, fetchGen);
  return next;
}

function applyBootstrapData(incoming: BootstrapResponse, fetchGen: number): BootstrapResponse | null {
  const merged = mergeBootstrapApply(incoming, fetchGen);
  if (!merged) return null;
  cacheSet(CACHE_KEY, merged);
  diskCacheSave(DISK_KEY, merged);
  diskCacheSave(VERSION_DISK_KEY, versionSnapshotFromBootstrap(merged));
  return merged;
}

export function getBootstrapSnapshot(): BootstrapSnapshot {
  return snapshot;
}

export function subscribeBootstrap(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getBootstrap(): BootstrapResponse | null {
  return snapshot.data ?? cachePeek<BootstrapResponse>(CACHE_KEY);
}

let loadInFlight: Promise<BootstrapResponse> | null = null;

function staleBootstrap(): BootstrapResponse | null {
  return (
    cachePeek<BootstrapResponse>(CACHE_KEY) ??
    diskCacheLoad<BootstrapResponse>(DISK_KEY) ??
    snapshot.data
  );
}

function versionSnapshotFromBootstrap(data: BootstrapResponse): BootstrapVersionFields {
  return {
    reference_data_version: data.reference_data_version,
    template_version: data.template_version,
    ui_schema_version: data.ui_schema_version,
    quick_add_version: data.quick_add_version,
    setup_version: data.setup_version,
    metadata_version: data.metadata_version,
  };
}

function invalidateCachesForVersionChanges(
  previous: BootstrapVersionFields | null,
  next: BootstrapResponse,
): void {
  if (!previous) return;
  const nextVersions = versionSnapshotFromBootstrap(next);

  void import("@/lib/reference_data/referenceDataStore").then((mod) => {
    mod.invalidateReferenceDataForVersions(previous, nextVersions);
  });

  if (
    previous.quick_add_version !== undefined &&
    nextVersions.quick_add_version !== undefined &&
    previous.quick_add_version !== nextVersions.quick_add_version
  ) {
    void import("@/lib/quick_add/draftStore").then((mod) => {
      for (const key of mod.listQuickAddDraftKeys()) {
        if (typeof localStorage !== "undefined") {
          localStorage.removeItem(key);
        }
      }
    });
  }
}

export async function loadBootstrap(options: { force?: boolean } = {}): Promise<BootstrapResponse> {
  const { force = false } = options;

  if (loadInFlight) {
    return loadInFlight;
  }

  const run = async (): Promise<BootstrapResponse> => {
    const cached = staleBootstrap();
    const spanId = startSpan("bootstrap.load", { force });

    if (cached && !force) {
      setSnapshot({ data: cached, hasLoadedOnce: true, error: null });
      void refreshBootstrapInBackground();
      endSpan(spanId, { metadata: { cacheHit: true } });
      return cached;
    }

    const fetchGen = ++bootstrapFetchGen;

    if (cached) {
      setSnapshot({ data: cached, isRefreshing: true, error: null });
    } else {
      setSnapshot({ isLoading: true, error: null });
    }

    try {
      const previousVersions = diskCacheLoad<BootstrapVersionFields>(VERSION_DISK_KEY);
      const data = await cacheFetch(CACHE_KEY, () => AppRepository.getBootstrap(), { force });
      invalidateCachesForVersionChanges(previousVersions, data);
      const applied = applyBootstrapData(data, fetchGen);
      if (!applied) {
        setSnapshot({
          isLoading: false,
          isRefreshing: false,
          error: null,
          hasLoadedOnce: true,
        });
        endSpan(spanId, { metadata: { cacheHit: false, droppedStale: true } });
        return snapshot.data ?? data;
      }
      setSnapshot({
        data: applied,
        isLoading: false,
        isRefreshing: false,
        error: null,
        hasLoadedOnce: true,
      });
      endSpan(spanId, { metadata: { cacheHit: false } });
      return applied;
    } catch (err) {
      endSpan(spanId, { metadata: { failed: true } });
      const message = err instanceof Error ? err.message : "Failed to load bootstrap";
      if (cached) {
        setSnapshot({
          data: cached,
          isLoading: false,
          isRefreshing: false,
          error: message,
          hasLoadedOnce: true,
        });
        return cached;
      }
      setSnapshot({ isLoading: false, isRefreshing: false, error: message });
      throw err;
    }
  };

  const pending = run();
  loadInFlight = pending;
  try {
    return await pending;
  } finally {
    if (loadInFlight === pending) {
      loadInFlight = null;
    }
  }
}

async function refreshBootstrapInBackground(): Promise<void> {
  if (snapshot.isRefreshing) return;
  const fetchGen = ++bootstrapFetchGen;
  setSnapshot({ isRefreshing: true });
  try {
    const previousVersions = diskCacheLoad<BootstrapVersionFields>(VERSION_DISK_KEY);
    const data = await AppRepository.getBootstrap();
    invalidateCachesForVersionChanges(previousVersions, data);
    const applied = applyBootstrapData(data, fetchGen);
    if (!applied) {
      setSnapshot({ isRefreshing: false, error: null, hasLoadedOnce: true });
      return;
    }
    setSnapshot({ data: applied, isRefreshing: false, error: null, hasLoadedOnce: true });
  } catch (err) {
    setSnapshot({
      isRefreshing: false,
      error: err instanceof Error ? err.message : "Bootstrap refresh failed",
    });
  }
}

export function invalidateBootstrap(): void {
  cacheInvalidate(CACHE_KEY);
  diskCacheRemove(DISK_KEY);
  diskCacheRemove(VERSION_DISK_KEY);
  setSnapshot({ data: null, hasLoadedOnce: false });
}

/** Drop disk/memory cache and reload without blanking the current UI snapshot. */
export function invalidateBootstrapAfterMutation(): void {
  cacheInvalidate(CACHE_KEY);
  diskCacheRemove(DISK_KEY);
  diskCacheRemove(VERSION_DISK_KEY);
  void loadBootstrap({ force: true }).catch(() => {
    // loadBootstrap already records snapshot.error; avoid unhandled rejections.
  });
}

/**
 * Write-through preference update after PATCH /app/preferences.
 * Bumps applied generation so any in-flight GET that started earlier is dropped.
 */
export function patchBootstrapPreferences(preferences: BootstrapPreferences): void {
  const current = getBootstrap();
  if (!current) {
    return;
  }
  bootstrapAppliedGen = Math.max(bootstrapAppliedGen, ++bootstrapFetchGen);
  const next: BootstrapResponse = {
    ...current,
    preferences,
  };
  cacheSet(CACHE_KEY, next);
  diskCacheSave(DISK_KEY, next);
  setSnapshot({ data: next, error: null, hasLoadedOnce: true });
}

export function clearBootstrapOnLogout(): void {
  cacheInvalidate();
  diskCacheClearAll();
  bootstrapFetchGen = 0;
  bootstrapAppliedGen = 0;
  snapshot = {
    data: null,
    isLoading: false,
    isRefreshing: false,
    error: null,
    hasLoadedOnce: false,
  };
  notify();
  void import("@/stores/contextStore").then((mod) => {
    mod.resetContextOnLogout();
  });
}

/**
 * Soft post-mutation refresh: patch module/context flags and refresh the
 * context session store. Does NOT clear app bootstrap or force a full reload.
 * Reserve {@link invalidateBootstrapAfterMutation} for login, workspace switch,
 * currency/prefs, and cache-version mismatch.
 */
export function notifyMomentMutation(
  context: "PERSONAL" | "GROUP" | "BUSINESS",
  states?: {
    contextState?: string;
    pulse?: string;
    moments?: string;
    memory?: string;
  },
): void {
  if (context === "PERSONAL") {
    if (states?.contextState || states?.pulse || states?.moments || states?.memory) {
      patchMyMoneyModuleStateInBootstrap({
        myMoney: states.contextState,
        pulse: states.pulse,
        moments: states.moments,
        memory: states.memory,
      });
    }
    void import("@/stores/personalSessionStore").then((m) => {
      void m.softRefreshPersonalSession().catch(() => {});
    });
    return;
  }
  if (context === "GROUP") {
    if (states?.contextState || states?.pulse || states?.moments) {
      patchGroupModuleStateInBootstrap({
        group: states.contextState,
        pulse: states.pulse,
        moments: states.moments,
      });
    }
    void import("@/stores/groupSessionStore").then((m) => {
      void m.softRefreshGroupSession().catch(() => {});
    });
    return;
  }
  if (states?.contextState) {
    const current = getBootstrap();
    if (current) {
      bootstrapAppliedGen = Math.max(bootstrapAppliedGen, ++bootstrapFetchGen);
      const contexts = current.contexts.map((c) =>
        c.key === "BUSINESS" ? { ...c, state: states.contextState! } : c,
      );
      const next: BootstrapResponse = { ...current, contexts };
      cacheSet(CACHE_KEY, next);
      diskCacheSave(DISK_KEY, next);
      setSnapshot({ data: next, error: null, hasLoadedOnce: true });
    }
  }
  void import("@/stores/businessSessionStore").then((m) => {
    void m.softRefreshBusinessSession().catch(() => {});
  });
}

export function contextStateFor(key: string): string {
  return snapshot.data?.contexts.find((c) => c.key === key)?.state ?? "EMPTY";
}

export function moduleStateFor(moduleKey: string): string {
  return snapshot.data?.modules[moduleKey]?.state ?? "EMPTY";
}

/** Patch Group module/context states without refetching full app bootstrap. */
export function patchGroupModuleStateInBootstrap(
  states: Partial<{
    group: string;
    pulse: string;
    moments: string;
  }>,
): void {
  const current = getBootstrap();
  if (!current) return;
  bootstrapAppliedGen = Math.max(bootstrapAppliedGen, ++bootstrapFetchGen);
  const contexts = current.contexts.map((c) =>
    c.key === "GROUP" && states.group
      ? { ...c, state: states.group }
      : c,
  );
  const modules = { ...current.modules };
  if (states.pulse) modules.pulse = { state: states.pulse };
  if (states.moments) modules.moments = { state: states.moments };
  const next: BootstrapResponse = { ...current, contexts, modules };
  cacheSet(CACHE_KEY, next);
  diskCacheSave(DISK_KEY, next);
  setSnapshot({ data: next, error: null, hasLoadedOnce: true });
}

/** Patch My Money module/context states without refetching full app bootstrap. */
export function patchMyMoneyModuleStateInBootstrap(
  states: Partial<{
    myMoney: string;
    pulse: string;
    moments: string;
    memory: string;
  }>,
): void {
  const current = getBootstrap();
  if (!current) return;
  bootstrapAppliedGen = Math.max(bootstrapAppliedGen, ++bootstrapFetchGen);
  const contexts = current.contexts.map((c) =>
    c.key === "MY_MONEY" && states.myMoney
      ? { ...c, state: states.myMoney }
      : c,
  );
  const modules = { ...current.modules };
  if (states.pulse) modules.pulse = { state: states.pulse };
  if (states.moments) modules.moments = { state: states.moments };
  if (states.memory) modules.memory = { state: states.memory };
  const next: BootstrapResponse = { ...current, contexts, modules };
  cacheSet(CACHE_KEY, next);
  diskCacheSave(DISK_KEY, next);
  setSnapshot({ data: next, error: null, hasLoadedOnce: true });
}

export function selectedBackendContext(): string {
  return snapshot.data?.preferences.selected_context ?? "MY_MONEY";
}

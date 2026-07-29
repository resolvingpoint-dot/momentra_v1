"use client";

/**
 * Business Team Ops SWR hooks — selected-tab-only, user-scoped keys, abort, reloadKey.
 *
 * Keys:
 *   business:v{SCHEMA}:{userId}:{momentId}:TEAM_OPERATIONS:pulse|moments
 *   business:v{SCHEMA}:{userId}:life|memory
 *   business:v{SCHEMA}:{userId}:{momentId}:activity:{filterKey}
 */
import { useCallback, useEffect, useRef, useState } from "react";
import {
  dedupeFetch,
  diskCacheLoad,
  diskCacheSave,
  isInflight,
} from "@/lib/cache/cacheStore";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";
import { businessProjectionSchemaSegment } from "@/lib/business/businessProjectionSchema";
import type {
  BusinessActivityListItem,
  BusinessLifeResponse,
  BusinessMemoryResponse,
  OpsMomentsResponse,
  OpsPulseResponse,
  RunwayMomentsResponse,
  RunwayPulseResponse,
  TeamOpsMomentsResponse,
  TeamOpsPulseResponse,
} from "@/lib/api/businessActive";
import {
  activityFilterKey,
  DEFAULT_ACTIVITY_PAGE_SIZE,
  type BusinessActivityFilters,
  type BusinessActivityPage,
} from "@/lib/business/activityFilters";
import {
  BusinessActiveRepository,
  type ActivityListResult,
} from "@/repositories/BusinessActiveRepository";
import { logBusinessLoad } from "@/lib/telemetry/businessLoadTelemetry";
import { useBusinessSessionStore } from "@/stores/businessSessionStore";
import { ApiError } from "@/lib/api/client";
import { isBusinessMomentAccessDenied, wasBusinessMomentReseated } from "@/lib/business/businessMomentAccess";
import { handleBusinessMomentInaccessible, getBusinessSessionSnapshot } from "@/stores/businessSessionStore";

type CacheEntry<T> = { data: T; at: number };

const pulseCache = new Map<string, CacheEntry<TeamOpsPulseResponse>>();
const momentsCache = new Map<string, CacheEntry<TeamOpsMomentsResponse>>();
const runwayPulseCache = new Map<string, CacheEntry<RunwayPulseResponse>>();
const runwayMomentsCache = new Map<string, CacheEntry<RunwayMomentsResponse>>();
const opsPulseCache = new Map<string, CacheEntry<OpsPulseResponse>>();
const opsMomentsCache = new Map<string, CacheEntry<OpsMomentsResponse>>();
const activityCache = new Map<string, CacheEntry<ActivityListResult>>();
const activityDetailCache = new Map<string, CacheEntry<BusinessActivityListItem>>();
const lifeCache = new Map<string, CacheEntry<BusinessLifeResponse>>();
const memoryCache = new Map<string, CacheEntry<BusinessMemoryResponse>>();

export const businessDedupeMetrics = {
  pulse: { requested: 0, coalesced: 0 },
  moments: { requested: 0, coalesced: 0 },
  activity: { requested: 0, coalesced: 0 },
  activityDetail: { requested: 0, coalesced: 0 },
  life: { requested: 0, coalesced: 0 },
  memory: { requested: 0, coalesced: 0 },
};

type Tab = keyof typeof businessDedupeMetrics;

function trackDedupe(tab: Tab, key: string) {
  businessDedupeMetrics[tab].requested += 1;
  if (isInflight(key)) businessDedupeMetrics[tab].coalesced += 1;
}

function uid(userId?: string | null) {
  return userId && userId.length > 0 ? userId : "anon";
}

export function businessCacheKey(
  userId: string | null | undefined,
  parts: string[],
): string {
  return ["business", businessProjectionSchemaSegment(), uid(userId), ...parts].join(":");
}

type LoadState<T> = {
  data: T | null;
  loading: boolean;
  refreshing: boolean;
  error: string | null;
  reload: (force?: boolean) => Promise<void>;
};

function useAbortableTabCache<T>(
  tab: Tab,
  cache: Map<string, CacheEntry<T>>,
  cacheId: string,
  enabled: boolean,
  fetcher: (signal: AbortSignal, force: boolean) => Promise<T>,
  reloadKey = 0,
  generation = 0,
  momentId: string | null = null,
): LoadState<T> {
  const disk = cacheId ? diskCacheLoad<T>(cacheId, STALE_TTL_MS) : null;
  const mem = cacheId ? cache.get(cacheId) : undefined;
  const initial = mem?.data ?? disk ?? null;
  const [data, setData] = useState<T | null>(initial);
  // Show content when stale/disk exists — never full-page skeleton over cached data.
  const [loading, setLoading] = useState(!initial && enabled && Boolean(cacheId));
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;
  const abortRef = useRef<AbortController | null>(null);
  const generationRef = useRef(generation);
  generationRef.current = generation;
  const momentIdRef = useRef(momentId);
  momentIdRef.current = momentId;

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      abortRef.current?.abort();
    };
  }, []);

  const load = useCallback(
    async (force = false) => {
      if (!enabled || !cacheId) return;
      const mid = momentIdRef.current;
      if (mid && wasBusinessMomentReseated(mid)) {
        if (mounted.current) {
          setLoading(false);
          setRefreshing(false);
        }
        return;
      }
      const sessionSnap = getBusinessSessionSnapshot();
      const sessionBootstrap = sessionSnap.bootstrap;
      if (sessionBootstrap) {
        const moments = sessionBootstrap.moments ?? [];
        const home = sessionBootstrap.moments_home;
        const inventoryEmpty =
          home?.is_empty === true ||
          (typeof home?.active_moment_count === "number" &&
            home.active_moment_count === 0) ||
          moments.length === 0;
        if (inventoryEmpty || sessionSnap.selectedMomentId == null) {
          if (mounted.current) {
            setLoading(false);
            setRefreshing(false);
            setData(null);
          }
          return;
        }
      }
      const requestGen = generation;
      const entry = cache.get(cacheId);
      const age = entry ? Date.now() - entry.at : Infinity;
      if (!force && entry && age < FRESH_TTL_MS) {
        setData(entry.data);
        setLoading(false);
        setRefreshing(false);
        logBusinessLoad({
          tab,
          requestKey: cacheId,
          reason: "fresh_ttl",
          cacheSource: "memory",
          isStale: false,
          durationMs: 0,
          generation: requestGen,
          success: true,
          momentId: cacheId.split(":")[2] ?? null,
        });
        return;
      }
      const diskStale = !force ? diskCacheLoad<T>(cacheId, STALE_TTL_MS) : null;
      const t0 = performance.now();
      let cacheSource: "memory" | "disk" | "network" = "network";
      if ((!force && entry) || diskStale) {
        const stale = entry?.data ?? diskStale;
        if (stale) {
          cacheSource = entry ? "memory" : "disk";
          setData(stale);
          setLoading(false);
          setRefreshing(true);
        } else {
          setLoading(true);
        }
      } else {
        setLoading(true);
      }
      setError(null);
      abortRef.current?.abort();
      const ac = new AbortController();
      abortRef.current = ac;
      const inflightKey = `fetch:${cacheId}`;
      trackDedupe(tab, inflightKey);
      try {
        const result = await dedupeFetch(inflightKey, () =>
          fetcherRef.current(ac.signal, force),
        );
        if (ac.signal.aborted) return;
        if (requestGen !== generationRef.current) {
          logBusinessLoad({
            tab,
            requestKey: cacheId,
            reason: "generation_mismatch",
            cacheSource: "network",
            durationMs: Math.round(performance.now() - t0),
            generation: requestGen,
            success: false,
            errorCode: "stale_generation",
          });
          return;
        }
        cache.set(cacheId, { data: result, at: Date.now() });
        diskCacheSave(cacheId, result);
        if (mounted.current) setData(result);
        logBusinessLoad({
          tab,
          requestKey: cacheId,
          reason: force ? "force" : "load",
          cacheSource,
          isStale: cacheSource !== "network",
          durationMs: Math.round(performance.now() - t0),
          generation: requestGen,
          success: true,
        });
      } catch (err) {
        if (ac.signal.aborted) return;
        if (requestGen !== generationRef.current) return;
        const inaccessible = isBusinessMomentAccessDenied(err);
        const mid = momentIdRef.current;
        if (inaccessible && mid) {
          if (mounted.current) {
            setError(null);
            setData(null);
          }
          void handleBusinessMomentInaccessible(
            mid,
            err instanceof ApiError ? err.code || "access_denied" : "access_denied",
          );
          logBusinessLoad({
            tab,
            requestKey: cacheId,
            reason: force ? "force" : "load",
            cacheSource: "network",
            durationMs: Math.round(performance.now() - t0),
            generation: requestGen,
            success: false,
            errorCode: "moment_inaccessible",
            momentId: mid,
          });
        } else if (mounted.current) {
          setError(err instanceof Error ? err.message : "Unable to load this section.");
          logBusinessLoad({
            tab,
            requestKey: cacheId,
            reason: force ? "force" : "load",
            cacheSource: "network",
            durationMs: Math.round(performance.now() - t0),
            generation: requestGen,
            success: false,
            errorCode: "fetch_failed",
          });
        }
      } finally {
        if (!ac.signal.aborted && mounted.current && requestGen === generationRef.current) {
          setLoading(false);
          setRefreshing(false);
        }
      }
    },
    [cache, cacheId, enabled, tab, generation],
  );

  useEffect(() => {
    if (!enabled || !cacheId) return;
    void load(reloadKey > 0);
  }, [enabled, cacheId, load, reloadKey]);

  return {
    data,
    loading,
    refreshing,
    error,
    reload: async (force = true) => {
      await load(force);
    },
  };
}

export function useBusinessPulse(
  momentId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = momentId
    ? businessCacheKey(userId, [momentId, "TEAM_OPERATIONS", "pulse"])
    : "";
  return useAbortableTabCache(
    "pulse",
    pulseCache,
    cacheId,
    enabled && Boolean(momentId),
    async (_signal, force) => BusinessActiveRepository.getPulse(momentId!, force),
    reloadKey,
    generation,
    momentId ?? null,
  );
}

export function useBusinessMoments(
  momentId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = momentId
    ? businessCacheKey(userId, [momentId, "TEAM_OPERATIONS", "moments"])
    : "";
  return useAbortableTabCache(
    "moments",
    momentsCache,
    cacheId,
    enabled && Boolean(momentId),
    async (_signal, force) => BusinessActiveRepository.getMoments(momentId!, force),
    reloadKey,
    generation,
    momentId ?? null,
  );
}

export function useRunwayPulse(
  momentId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = momentId
    ? businessCacheKey(userId, [momentId, "BUSINESS_RUNWAY", "pulse"])
    : "";
  return useAbortableTabCache(
    "pulse",
    runwayPulseCache,
    cacheId,
    enabled && Boolean(momentId),
    async (_signal, force) => BusinessActiveRepository.getRunwayPulse(momentId!, force),
    reloadKey,
    generation,
    momentId ?? null,
  );
}

export function useRunwayMoments(
  momentId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = momentId
    ? businessCacheKey(userId, [momentId, "BUSINESS_RUNWAY", "moments"])
    : "";
  return useAbortableTabCache(
    "moments",
    runwayMomentsCache,
    cacheId,
    enabled && Boolean(momentId),
    async (_signal, force) => BusinessActiveRepository.getRunwayMoments(momentId!, force),
    reloadKey,
    generation,
    momentId ?? null,
  );
}

export function useOpsPulse(
  momentId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = momentId
    ? businessCacheKey(userId, [momentId, "BUSINESS_OPERATIONS", "pulse"])
    : "";
  return useAbortableTabCache(
    "pulse",
    opsPulseCache,
    cacheId,
    enabled && Boolean(momentId),
    async (_signal, force) => BusinessActiveRepository.getOpsPulse(momentId!, force),
    reloadKey,
    generation,
    momentId ?? null,
  );
}

export function useOpsMoments(
  momentId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = momentId
    ? businessCacheKey(userId, [momentId, "BUSINESS_OPERATIONS", "moments"])
    : "";
  return useAbortableTabCache(
    "moments",
    opsMomentsCache,
    cacheId,
    enabled && Boolean(momentId),
    async (_signal, force) => BusinessActiveRepository.getOpsMoments(momentId!, force),
    reloadKey,
    generation,
    momentId ?? null,
  );
}

export function useBusinessLife(
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = businessCacheKey(userId, ["life"]);
  return useAbortableTabCache(
    "life",
    lifeCache,
    cacheId,
    enabled,
    async (_signal, force) => BusinessActiveRepository.getLife(force),
    reloadKey,
    generation,
  );
}

export function useBusinessMemory(
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const generation = useBusinessSessionStore().generation;
  const cacheId = businessCacheKey(userId, ["memory"]);
  return useAbortableTabCache(
    "memory",
    memoryCache,
    cacheId,
    enabled,
    async (_signal, force) => BusinessActiveRepository.getMemory(force),
    reloadKey,
    generation,
  );
}

export function useBusinessActivity(
  momentId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
  filters?: BusinessActivityFilters | null,
  page?: BusinessActivityPage | null,
) {
  const generation = useBusinessSessionStore().generation;
  const pageSize = page?.pageSize ?? DEFAULT_ACTIVITY_PAGE_SIZE;
  const pageNum = Math.max(1, page?.page ?? 1);
  const filterKey = activityFilterKey(filters, { page: pageNum, pageSize });
  const listKey = momentId
    ? businessCacheKey(userId, [momentId, "activity", filterKey])
    : "";

  const state = useAbortableTabCache(
    "activity",
    activityCache,
    listKey,
    enabled && Boolean(momentId),
    async (_signal, force) =>
      BusinessActiveRepository.listActivity(
        momentId!,
        filters,
        { page: pageNum, pageSize },
        force,
      ),
    reloadKey,
    generation,
    momentId ?? null,
  );

  return {
    data: state.data,
    items: state.data?.items ?? [],
    total: state.data?.total ?? 0,
    loading: state.loading,
    refreshing: state.refreshing,
    error: state.error,
    reload: state.reload,
  };
}

export function useBusinessActivityDetail(
  momentId: string | null | undefined,
  eventId: string | null | undefined,
  enabled = true,
  reloadKey = 0,
  userId?: string | null,
) {
  const cacheId =
    momentId && eventId
      ? businessCacheKey(userId, [momentId, "activity_detail", eventId])
      : "";
  return useAbortableTabCache(
    "activityDetail",
    activityDetailCache,
    cacheId,
    enabled && Boolean(momentId && eventId),
    async (_signal, force) =>
      BusinessActiveRepository.getActivity(momentId!, eventId!, force),
    reloadKey,
  );
}

/** Surfaces invalidated after Action Center / activity mutation. */
export const BUSINESS_ACTIVE_REFRESH_SURFACES = [
  "activity",
  "pulse",
  "moments",
  "life",
  "memory",
] as const;

/** Invalidate after Action Center / activity mutation — no session bootstrap.
 * Prefer [applyBusinessMutationSuccess] then soft agg invalidate so Pulse/Moments
 * stay painted until silent SWR reconcile.
 */
export function invalidateBusinessActiveCaches(momentId?: string, userId?: string | null) {
  const u = uid(userId);
  const clearMatching = (cache: Map<string, CacheEntry<unknown>>, needle: string) => {
    for (const key of [...cache.keys()]) {
      if (key.includes(needle)) cache.delete(key);
    }
  };

  if (momentId) {
    clearMatching(pulseCache, `${u}:${momentId}`);
    clearMatching(momentsCache, `${u}:${momentId}`);
    clearMatching(runwayPulseCache, `${u}:${momentId}`);
    clearMatching(runwayMomentsCache, `${u}:${momentId}`);
    clearMatching(opsPulseCache, `${u}:${momentId}`);
    clearMatching(opsMomentsCache, `${u}:${momentId}`);
    clearMatching(activityCache, `${u}:${momentId}`);
    clearMatching(activityDetailCache, `${u}:${momentId}`);
  } else {
    pulseCache.clear();
    momentsCache.clear();
    runwayPulseCache.clear();
    runwayMomentsCache.clear();
    opsPulseCache.clear();
    opsMomentsCache.clear();
    activityCache.clear();
    activityDetailCache.clear();
  }
  lifeCache.clear();
  memoryCache.clear();
}

/** Clear only Life/Memory after mutation — Pulse/Moments already patched. */
export function softInvalidateBusinessAggCaches(_userId?: string | null) {
  lifeCache.clear();
  memoryCache.clear();
}

export function peekBusinessPulseCache(
  momentId: string,
  momentTypeCode: string,
  userId?: string | null,
): TeamOpsPulseResponse | RunwayPulseResponse | OpsPulseResponse | null {
  const code = (momentTypeCode || "TEAM_OPERATIONS").toUpperCase();
  const kind =
    code === "BUSINESS_RUNWAY"
      ? "BUSINESS_RUNWAY"
      : code === "BUSINESS_OPERATIONS" || code === "DEPARTMENT_OPERATIONS"
        ? "BUSINESS_OPERATIONS"
        : "TEAM_OPERATIONS";
  const key = businessCacheKey(userId, [momentId, kind, "pulse"]);
  const cache =
    kind === "BUSINESS_RUNWAY"
      ? runwayPulseCache
      : kind === "BUSINESS_OPERATIONS"
        ? opsPulseCache
        : pulseCache;
  return cache.get(key)?.data ?? diskCacheLoad(key, STALE_TTL_MS);
}

export function peekBusinessMomentsCache(
  momentId: string,
  momentTypeCode: string,
  userId?: string | null,
): TeamOpsMomentsResponse | RunwayMomentsResponse | OpsMomentsResponse | null {
  const code = (momentTypeCode || "TEAM_OPERATIONS").toUpperCase();
  const kind =
    code === "BUSINESS_RUNWAY"
      ? "BUSINESS_RUNWAY"
      : code === "BUSINESS_OPERATIONS" || code === "DEPARTMENT_OPERATIONS"
        ? "BUSINESS_OPERATIONS"
        : "TEAM_OPERATIONS";
  const key = businessCacheKey(userId, [momentId, kind, "moments"]);
  const cache =
    kind === "BUSINESS_RUNWAY"
      ? runwayMomentsCache
      : kind === "BUSINESS_OPERATIONS"
        ? opsMomentsCache
        : momentsCache;
  return cache.get(key)?.data ?? diskCacheLoad(key, STALE_TTL_MS);
}

export function seedBusinessPulseCache(
  momentId: string,
  data: TeamOpsPulseResponse,
  userId?: string | null,
) {
  const key = businessCacheKey(userId, [momentId, "TEAM_OPERATIONS", "pulse"]);
  pulseCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedBusinessMomentsCache(
  momentId: string,
  data: TeamOpsMomentsResponse,
  userId?: string | null,
) {
  const key = businessCacheKey(userId, [momentId, "TEAM_OPERATIONS", "moments"]);
  momentsCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedRunwayPulseCache(
  momentId: string,
  data: RunwayPulseResponse,
  userId?: string | null,
) {
  const key = businessCacheKey(userId, [momentId, "BUSINESS_RUNWAY", "pulse"]);
  runwayPulseCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedRunwayMomentsCache(
  momentId: string,
  data: RunwayMomentsResponse,
  userId?: string | null,
) {
  const key = businessCacheKey(userId, [momentId, "BUSINESS_RUNWAY", "moments"]);
  runwayMomentsCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedOpsPulseCache(
  momentId: string,
  data: OpsPulseResponse,
  userId?: string | null,
) {
  const key = businessCacheKey(userId, [momentId, "BUSINESS_OPERATIONS", "pulse"]);
  opsPulseCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedOpsMomentsCache(
  momentId: string,
  data: OpsMomentsResponse,
  userId?: string | null,
) {
  const key = businessCacheKey(userId, [momentId, "BUSINESS_OPERATIONS", "moments"]);
  opsMomentsCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedBusinessLifeCache(data: BusinessLifeResponse, userId?: string | null) {
  const key = businessCacheKey(userId, ["life"]);
  lifeCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedBusinessMemoryCache(data: BusinessMemoryResponse, userId?: string | null) {
  const key = businessCacheKey(userId, ["memory"]);
  memoryCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function seedBusinessActivityCache(
  momentId: string,
  data: ActivityListResult,
  userId?: string | null,
  filters?: BusinessActivityFilters | null,
  page?: BusinessActivityPage | null,
) {
  const pageSize = page?.pageSize ?? DEFAULT_ACTIVITY_PAGE_SIZE;
  const pageNum = Math.max(1, page?.page ?? 1);
  const filterKey = activityFilterKey(filters, { page: pageNum, pageSize });
  const key = businessCacheKey(userId, [momentId, "activity", filterKey]);
  activityCache.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

/**
 * @deprecated P0: do not prefetch all surfaces on Business open.
 * Selected-tab hooks load on demand. Kept as no-op for any leftover callers.
 */
export async function prefetchBusinessActiveSurfaces(_options: {
  momentId: string;
  momentTypeCode: string;
  userId?: string | null;
}): Promise<void> {
  return;
}

/** Disk warm for selected moment pulse/moments only — no Life/Memory prefetch. */
export function warmUpBusinessSessionFromDisk(options: {
  momentId: string;
  momentTypeCode: string;
  userId?: string | null;
}): void {
  const { momentId, userId } = options;
  const code = (options.momentTypeCode || "").toUpperCase();
  if (code === "BUSINESS_RUNWAY") {
    const p = diskCacheLoad<RunwayPulseResponse>(
      businessCacheKey(userId, [momentId, "BUSINESS_RUNWAY", "pulse"]),
      STALE_TTL_MS,
    );
    if (p) seedRunwayPulseCache(momentId, p, userId);
    const m = diskCacheLoad<RunwayMomentsResponse>(
      businessCacheKey(userId, [momentId, "BUSINESS_RUNWAY", "moments"]),
      STALE_TTL_MS,
    );
    if (m) seedRunwayMomentsCache(momentId, m, userId);
    return;
  }
  if (code === "BUSINESS_OPERATIONS" || code === "DEPARTMENT_OPERATIONS") {
    const p = diskCacheLoad<OpsPulseResponse>(
      businessCacheKey(userId, [momentId, "BUSINESS_OPERATIONS", "pulse"]),
      STALE_TTL_MS,
    );
    if (p) seedOpsPulseCache(momentId, p, userId);
    const m = diskCacheLoad<OpsMomentsResponse>(
      businessCacheKey(userId, [momentId, "BUSINESS_OPERATIONS", "moments"]),
      STALE_TTL_MS,
    );
    if (m) seedOpsMomentsCache(momentId, m, userId);
    return;
  }
  const p = diskCacheLoad<TeamOpsPulseResponse>(
    businessCacheKey(userId, [momentId, "TEAM_OPERATIONS", "pulse"]),
    STALE_TTL_MS,
  );
  if (p) seedBusinessPulseCache(momentId, p, userId);
  const m = diskCacheLoad<TeamOpsMomentsResponse>(
    businessCacheKey(userId, [momentId, "TEAM_OPERATIONS", "moments"]),
    STALE_TTL_MS,
  );
  if (m) seedBusinessMomentsCache(momentId, m, userId);
}

/** Test helpers — seed then invalidate to verify all five surfaces reload. */
export function __seedBusinessActiveCachesForTest(momentId: string, userId?: string | null) {
  const u = uid(userId);
  const at = Date.now();
  const stub = { data: {} as never, at };
  pulseCache.set(`business:${u}:${momentId}:TEAM_OPERATIONS:pulse`, stub);
  momentsCache.set(`business:${u}:${momentId}:TEAM_OPERATIONS:moments`, stub);
  runwayPulseCache.set(`business:${u}:${momentId}:BUSINESS_RUNWAY:pulse`, stub);
  runwayMomentsCache.set(`business:${u}:${momentId}:BUSINESS_RUNWAY:moments`, stub);
  opsPulseCache.set(`business:${u}:${momentId}:BUSINESS_OPERATIONS:pulse`, stub);
  opsMomentsCache.set(`business:${u}:${momentId}:BUSINESS_OPERATIONS:moments`, stub);
  activityCache.set(`business:${u}:${momentId}:activity:test`, stub);
  activityDetailCache.set(`business:${u}:${momentId}:activity_detail:e1`, stub);
  lifeCache.set(`business:${u}:life`, stub);
  memoryCache.set(`business:${u}:memory`, stub);
}

export function businessActiveCacheSnapshot(momentId: string, userId?: string | null) {
  const u = uid(userId);
  const has = (cache: Map<string, unknown>, needle: string) =>
    [...cache.keys()].some((k) => k.includes(needle));
  return {
    activity: has(activityCache, `${u}:${momentId}`),
    pulse: has(pulseCache, `${u}:${momentId}`),
    moments: has(momentsCache, `${u}:${momentId}`),
    life: lifeCache.size > 0,
    memory: memoryCache.size > 0,
  };
}

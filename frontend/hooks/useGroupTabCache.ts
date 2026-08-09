"use client";

/**
 * Group tab SWR hooks — reuse cacheStore.dedupeFetch + disk cache (no parallel cache system).
 */
import { useCallback, useEffect, useRef, useState } from "react";
import {
  dedupeFetch,
  diskCacheLoad,
  diskCacheRemove,
  diskCacheSave,
  isInflight,
} from "@/lib/cache/cacheStore";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";
import {
  getActiveMemory,
  getActivePulse,
  getLivingMomentsView,
  getLivingPulse,
  getPurchaseMomentsView,
  getPurchasePulse,
  getSessionBootstrap,
  getTripMomentsView,
  getTripPulse,
  type ActiveMemoryResponse,
  type ActivePulseResponse,
  type LivingMomentsViewResponse,
  type LivingPulseResponse,
  type PurchaseMomentsViewResponse,
  type PurchasePulseResponse,
  type SessionBootstrapResponse,
  type TripMomentsViewResponse,
  type TripPulseResponse,
} from "@/lib/api/group";
import { getGroupLife, type GroupLifeResponse } from "@/lib/api/groupLife";
import { subscribeTripMomentStream } from "@/lib/api/groupStream";
import { useGroupSessionStore } from "@/stores/groupSessionStore";

type CacheEntry<T> = { data: T; at: number };

const pulseCache = new Map<string, CacheEntry<ActivePulseResponse>>();
const tripPulseCache = new Map<string, CacheEntry<TripPulseResponse>>();
const purchasePulseCache = new Map<string, CacheEntry<PurchasePulseResponse>>();
const livingPulseCache = new Map<string, CacheEntry<LivingPulseResponse>>();
const momentsCache = new Map<string, CacheEntry<TripMomentsViewResponse>>();
const purchaseMomentsCache = new Map<string, CacheEntry<PurchaseMomentsViewResponse>>();
const livingMomentsCache = new Map<string, CacheEntry<LivingMomentsViewResponse>>();
const memoryCache = new Map<string, CacheEntry<ActiveMemoryResponse>>();
const lifeCache = new Map<string, CacheEntry<GroupLifeResponse>>();

/** Dev/debug counters for GROUP_PERFORMANCE_REPORT */
export const groupDedupeMetrics = {
  pulse: { requested: 0, coalesced: 0 },
  moments: { requested: 0, coalesced: 0 },
  memory: { requested: 0, coalesced: 0 },
  life: { requested: 0, coalesced: 0 },
  session: { requested: 0, coalesced: 0 },
};

function trackDedupe(tab: keyof typeof groupDedupeMetrics, key: string) {
  groupDedupeMetrics[tab].requested += 1;
  if (isInflight(key)) groupDedupeMetrics[tab].coalesced += 1;
}

function diskKey(tab: string, momentId: string) {
  return `group:${tab}:${momentId}`;
}

function useGroupTabCache<T>(
  tab: keyof typeof groupDedupeMetrics,
  cache: Map<string, CacheEntry<T>>,
  momentId: string | null | undefined,
  fetcher: (id: string, forceRefresh?: boolean) => Promise<T>,
  enabled: boolean,
  generation = 0,
) {
  const id = momentId ?? "";
  const disk = id ? diskCacheLoad<T>(diskKey(tab, id), STALE_TTL_MS) : null;
  const mem = id ? cache.get(id) : undefined;
  const initial = mem?.data ?? disk ?? null;
  const [data, setData] = useState<T | null>(initial);
  const [loading, setLoading] = useState(!initial && enabled && Boolean(id));
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);
  const hasDataRef = useRef(Boolean(initial));
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;
  hasDataRef.current = Boolean(data);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const load = useCallback(
    async (force = false) => {
      if (!enabled || !id) return;

      // Stale-while-revalidate: paint cached data immediately; never blank usable data
      // before refresh completes. Force clears storage only for explicit reload paths.
      let entry = cache.get(id);
      if (!entry && !force) {
        const fromDisk = diskCacheLoad<T>(diskKey(tab, id), STALE_TTL_MS);
        if (fromDisk) {
          entry = { data: fromDisk, at: Date.now() };
          cache.set(id, entry);
        }
      }
      const cachedValue = entry?.data ?? null;
      const hadUsable = Boolean(cachedValue) || hasDataRef.current;

      if (cachedValue) {
        setData(cachedValue);
        setLoading(false);
      }

      const age = entry ? Date.now() - entry.at : Infinity;
      if (!force && entry && age < FRESH_TTL_MS) {
        setRefreshing(false);
        return;
      }

      if (hadUsable) {
        setRefreshing(true);
        setLoading(false);
      } else {
        setLoading(true);
      }

      if (force) {
        cache.delete(id);
        diskCacheRemove(diskKey(tab, id));
      }

      setError(null);
      const key = `group:${tab}:${id}${force ? ":force" : ""}`;
      trackDedupe(tab, key);
      try {
        const result = await dedupeFetch(key, () => fetcherRef.current(id, force));
        cache.set(id, { data: result, at: Date.now() });
        diskCacheSave(diskKey(tab, id), result);
        if (mounted.current) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (mounted.current && !hadUsable) {
          setError(err instanceof Error ? err.message : "Unable to load this section.");
        }
      } finally {
        if (mounted.current) {
          setLoading(false);
          setRefreshing(false);
        }
      }
    },
    [cache, enabled, id, tab],
  );

  useEffect(() => {
    if (!enabled || !id) return;
    // Mount always uses SWR. Force only via reload() (pull-to-refresh / retry / mutation).
    void load(false);
  }, [enabled, id, load, generation, tab]);

  return {
    data,
    loading,
    refreshing,
    error,
    /** Pull-to-refresh / explicit retry — bypasses client+server cache. */
    reload: () => load(true),
    /** SSE / mutation invalidate — soft SWR revalidate (no force_refresh). */
    revalidate: () => load(false),
  };
}

export function useGroupPulse(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "pulse",
    pulseCache,
    momentId,
    getActivePulse,
    enabled,
    generation,
  );
}

export function useGroupTripPulse(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "pulse",
    tripPulseCache,
    momentId,
    getTripPulse,
    enabled,
    generation,
  );
}

export function useGroupPurchasePulse(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "pulse",
    purchasePulseCache,
    momentId,
    getPurchasePulse,
    enabled,
    generation,
  );
}

export function useGroupMoments(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "moments",
    momentsCache,
    momentId,
    getTripMomentsView,
    enabled,
    generation,
  );
}

export function useGroupPurchaseMoments(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "moments",
    purchaseMomentsCache,
    momentId,
    getPurchaseMomentsView,
    enabled,
    generation,
  );
}

export function useGroupLivingPulse(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "pulse",
    livingPulseCache,
    momentId,
    getLivingPulse,
    enabled,
    generation,
  );
}

export function useGroupLivingMoments(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "moments",
    livingMomentsCache,
    momentId,
    getLivingMomentsView,
    enabled,
    generation,
  );
}

export function useGroupMemory(momentId: string | null | undefined, enabled = true) {
  const generation = useGroupSessionStore().generation;
  return useGroupTabCache(
    "memory",
    memoryCache,
    momentId,
    getActiveMemory,
    enabled,
    generation,
  );
}

export function useGroupLife(enabled = true) {
  const generation = useGroupSessionStore().generation;
  const cacheKey = "life";
  const mem = lifeCache.get(cacheKey);
  const disk = diskCacheLoad<GroupLifeResponse>(diskKey("life", "aggregate"), STALE_TTL_MS);
  const initial = mem?.data ?? disk ?? null;
  const [data, setData] = useState<GroupLifeResponse | null>(initial);
  const [loading, setLoading] = useState(!initial && enabled);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const hasDataRef = useRef(Boolean(initial));
  hasDataRef.current = Boolean(data);

  const load = useCallback(
    async (force = false) => {
      if (!enabled) return;
      let entry = lifeCache.get(cacheKey);
      if (!entry && !force) {
        const fromDisk = diskCacheLoad<GroupLifeResponse>(diskKey("life", "aggregate"), STALE_TTL_MS);
        if (fromDisk) {
          entry = { data: fromDisk, at: Date.now() };
          lifeCache.set(cacheKey, entry);
        }
      }
      const cachedValue = entry?.data ?? null;
      const hadUsable = Boolean(cachedValue) || hasDataRef.current;
      if (cachedValue) {
        setData(cachedValue);
        setLoading(false);
      }
      const age = entry ? Date.now() - entry.at : Infinity;
      if (!force && entry && age < FRESH_TTL_MS) {
        setRefreshing(false);
        return;
      }
      if (hadUsable) {
        setRefreshing(true);
        setLoading(false);
      } else {
        setLoading(true);
      }
      if (force) {
        lifeCache.delete(cacheKey);
      }
      const key = force ? "group:life:aggregate:force" : "group:life:aggregate";
      trackDedupe("life", key);
      try {
        const result = await dedupeFetch(key, () => getGroupLife());
        lifeCache.set(cacheKey, { data: result, at: Date.now() });
        diskCacheSave(diskKey("life", "aggregate"), result);
        setData(result);
      } catch (err) {
        if (!hadUsable) {
          setError(err instanceof Error ? err.message : "Unable to load this section.");
        }
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [enabled],
  );

  useEffect(() => {
    if (!enabled) return;
    void load(false);
  }, [enabled, load, generation]);

  return {
    data,
    loading,
    refreshing,
    error,
    reload: () => load(true),
    revalidate: () => load(false),
  };
}

export async function fetchGroupSessionBootstrapDeduped(): Promise<SessionBootstrapResponse> {
  const key = "group:session_bootstrap";
  trackDedupe("session", key);
  return dedupeFetch(key, () => getSessionBootstrap());
}

export function invalidateGroupTabCaches(momentId?: string) {
  if (momentId) {
    pulseCache.delete(momentId);
    tripPulseCache.delete(momentId);
    purchasePulseCache.delete(momentId);
    livingPulseCache.delete(momentId);
    momentsCache.delete(momentId);
    purchaseMomentsCache.delete(momentId);
    livingMomentsCache.delete(momentId);
    memoryCache.delete(momentId);
    diskCacheRemove(diskKey("pulse", momentId));
    diskCacheRemove(diskKey("moments", momentId));
    diskCacheRemove(diskKey("memory", momentId));
  } else {
    pulseCache.clear();
    tripPulseCache.clear();
    purchasePulseCache.clear();
    livingPulseCache.clear();
    momentsCache.clear();
    purchaseMomentsCache.clear();
    livingMomentsCache.clear();
    memoryCache.clear();
  }
  lifeCache.clear();
  diskCacheRemove(diskKey("life", "aggregate"));
}

/**
 * Subscribe to trip moment SSE invalidate events.
 * Clears pulse/moments/memory caches for the id; optional callback should soft-revalidate
 * (bump reloadKey → load(false)), not force_refresh.
 */
export function useTripMomentStream(
  momentId: string | null | undefined,
  onInvalidate?: () => void,
  enabled = true,
) {
  const onInvalidateRef = useRef(onInvalidate);
  onInvalidateRef.current = onInvalidate;

  useEffect(() => {
    if (!enabled || !momentId) return;
    return subscribeTripMomentStream(momentId, () => {
      invalidateGroupTabCaches(momentId);
      onInvalidateRef.current?.();
    });
  }, [momentId, enabled]);
}

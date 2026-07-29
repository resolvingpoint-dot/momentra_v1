"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { dedupeFetch } from "@/lib/cache/cacheStore";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import {
  getTemplateLife,
} from "@/lib/api/client";
import type {
  TemplateLifeResponse,
  TemplateMemoryResponse,
  TemplateMomentsResponse,
} from "@/lib/api/personal";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";
import {
  delay,
  isSnapshotRebuilding,
  SNAPSHOT_REBUILDING_DELAY_MS,
  SNAPSHOT_REBUILDING_MAX_ATTEMPTS,
} from "@/lib/cache/snapshotRebuilding";
import {
  persistTemplateMemory,
  persistTemplateMoments,
  persistTemplatePulse,
  usePersonalSessionStore,
} from "@/stores/personalSessionStore";

const TTL_MS = FRESH_TTL_MS;

type CacheEntry<T> = { data: T; at: number; projectionVersion?: number };

const momentsCache = new Map<PersonalMomentTypeCode, CacheEntry<TemplateMomentsResponse>>();
const pulseCache = new Map<PersonalMomentTypeCode, CacheEntry<Record<string, unknown>>>();
const lifeCache = new Map<PersonalMomentTypeCode, CacheEntry<TemplateLifeResponse>>();
const memoryCache = new Map<PersonalMomentTypeCode, CacheEntry<TemplateMemoryResponse>>();

export function invalidateTemplateMomentsCache(typeCode?: PersonalMomentTypeCode) {
  if (typeCode) momentsCache.delete(typeCode);
  else momentsCache.clear();
}

export function invalidateTemplateLifeCache(typeCode?: PersonalMomentTypeCode) {
  if (typeCode) lifeCache.delete(typeCode);
  else lifeCache.clear();
}

export function invalidateTemplateMemoryCache(typeCode?: PersonalMomentTypeCode) {
  if (typeCode) memoryCache.delete(typeCode);
  else memoryCache.clear();
}

export function invalidateTemplatePulseCache(typeCode?: PersonalMomentTypeCode) {
  if (typeCode) pulseCache.delete(typeCode);
  else pulseCache.clear();
}

export function invalidateTemplateProjectionCaches(typeCode?: PersonalMomentTypeCode) {
  invalidateTemplateMomentsCache(typeCode);
  invalidateTemplatePulseCache(typeCode);
  invalidateTemplateLifeCache(typeCode);
  invalidateTemplateMemoryCache(typeCode);
}

export function seedTemplateMomentsCache(
  typeCode: PersonalMomentTypeCode,
  data: TemplateMomentsResponse,
) {
  momentsCache.set(typeCode, {
    data,
    at: Date.now(),
    projectionVersion: data.projection_version,
  });
}

export function seedTemplateMemoryCache(
  typeCode: PersonalMomentTypeCode,
  data: TemplateMemoryResponse,
) {
  memoryCache.set(typeCode, {
    data,
    at: Date.now(),
    projectionVersion: data.projection_version,
  });
}

export function seedTemplatePulseCache(
  typeCode: PersonalMomentTypeCode,
  data: Record<string, unknown>,
) {
  pulseCache.set(typeCode, {
    data,
    at: Date.now(),
    projectionVersion: data.projection_version as number | undefined,
  });
}

export function getTemplateMomentsCache(
  typeCode: PersonalMomentTypeCode,
): TemplateMomentsResponse | null {
  return momentsCache.get(typeCode)?.data ?? null;
}

export function getTemplateMemoryCache(
  typeCode: PersonalMomentTypeCode,
): TemplateMemoryResponse | null {
  return memoryCache.get(typeCode)?.data ?? null;
}

export function getTemplatePulseCache(
  typeCode: PersonalMomentTypeCode,
): Record<string, unknown> | null {
  return pulseCache.get(typeCode)?.data ?? null;
}

function dedupeKey(
  resource: string,
  momentTypeCode: PersonalMomentTypeCode,
  forceAttempt?: number,
): string {
  const base = `personal:template_${resource}:${momentTypeCode}`;
  return forceAttempt === undefined ? base : `${base}:force:${forceAttempt}`;
}

function useTemplateCache<T extends { projection_version?: number }>(
  resource: string,
  cache: Map<PersonalMomentTypeCode, CacheEntry<T>>,
  fetcher: (code: PersonalMomentTypeCode) => Promise<T>,
  momentTypeCode: PersonalMomentTypeCode,
  enabled: boolean,
  onPersist?: (code: PersonalMomentTypeCode, data: T) => void,
) {
  const generation = usePersonalSessionStore().generation;
  const cached = cache.get(momentTypeCode);
  const [data, setData] = useState<T | null>(cached?.data ?? null);
  const [loading, setLoading] = useState(!cached);
  const [refreshing, setRefreshing] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadGeneration = useRef(0);

  const load = useCallback(
    async (force = false) => {
      const gen = ++loadGeneration.current;
      const entry = cache.get(momentTypeCode);
      const age = entry ? Date.now() - entry.at : Infinity;
      const fresh = !force && entry && age < TTL_MS;
      const staleUsable = !force && entry && age < STALE_TTL_MS;
      if (fresh && entry) {
        setData(entry.data);
        setLoading(false);
        setRefreshing(false);
        setRebuilding(false);
        return;
      }
      if (staleUsable && entry) {
        setData(entry.data);
        setRefreshing(true);
        setLoading(false);
      } else if (entry && !force) {
        setData(entry.data);
        setLoading(false);
        setRefreshing(false);
      } else {
        setLoading(true);
        setRefreshing(false);
      }
      setError(null);

      let attempt = 0;
      while (true) {
        try {
          const result = await dedupeFetch(
            dedupeKey(resource, momentTypeCode, force ? attempt : undefined),
            () => fetcher(momentTypeCode),
          );
          if (gen !== loadGeneration.current) return;
          const prev = cache.get(momentTypeCode);
          const nextVersion = result.projection_version;
          if (
            !force &&
            prev &&
            nextVersion !== undefined &&
            prev.projectionVersion === nextVersion
          ) {
            cache.set(momentTypeCode, {
              data: prev.data,
              at: Date.now(),
              projectionVersion: nextVersion,
            });
            setData(prev.data);
            setRebuilding(false);
            break;
          }
          cache.set(momentTypeCode, {
            data: result,
            at: Date.now(),
            projectionVersion: nextVersion,
          });
          onPersist?.(momentTypeCode, result);
          setData(result);
          setRebuilding(false);
          break;
        } catch (err) {
          if (gen !== loadGeneration.current) return;
          if (force && isSnapshotRebuilding(err) && attempt < SNAPSHOT_REBUILDING_MAX_ATTEMPTS) {
            attempt += 1;
            setRebuilding(true);
            setRefreshing(true);
            setLoading(false);
            setError(null);
            await delay(SNAPSHOT_REBUILDING_DELAY_MS);
            if (gen !== loadGeneration.current) return;
            continue;
          }
          setRebuilding(false);
          setError(err instanceof Error ? err.message : "Failed to load");
          break;
        }
      }

      if (gen !== loadGeneration.current) return;
      setLoading(false);
      setRefreshing(false);
      setRebuilding(false);
    },
    [cache, fetcher, momentTypeCode, onPersist, resource],
  );

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      setRefreshing(false);
      setRebuilding(false);
      return;
    }
    const entry = cache.get(momentTypeCode);
    setData(entry?.data ?? null);
    setLoading(!entry);
    setRefreshing(false);
    setRebuilding(false);
    void load(false);
  }, [momentTypeCode, load, enabled, generation]);

  const refreshAfterSetup = useCallback(() => {
    cache.delete(momentTypeCode);
    return load(false);
  }, [cache, load, momentTypeCode]);

  return {
    data,
    loading,
    refreshing,
    rebuilding,
    error,
    reload: () => load(true),
    revalidate: () => load(false),
    refreshAfterSetup,
  };
}

export function useTemplatePulse(
  momentTypeCode: PersonalMomentTypeCode,
  options?: { enabled?: boolean },
) {
  return useTemplateCache(
    "pulse",
    pulseCache,
    (code) => PersonalRepository.getTemplatePulse(code),
    momentTypeCode,
    options?.enabled ?? true,
    (code, data) => persistTemplatePulse(code, data as Record<string, unknown>),
  );
}

export function useTemplateMoments(
  momentTypeCode: PersonalMomentTypeCode,
  options?: { enabled?: boolean },
) {
  return useTemplateCache(
    "moments",
    momentsCache,
    (code) => PersonalRepository.getTemplateMoments(code),
    momentTypeCode,
    options?.enabled ?? true,
    persistTemplateMoments,
  );
}

export function useTemplateLife(
  momentTypeCode: PersonalMomentTypeCode,
  options?: { enabled?: boolean },
) {
  return useTemplateCache("life", lifeCache, getTemplateLife, momentTypeCode, options?.enabled ?? true);
}

export function useTemplateMemory(
  momentTypeCode: PersonalMomentTypeCode,
  options?: { enabled?: boolean },
) {
  return useTemplateCache(
    "memory",
    memoryCache,
    (code) => PersonalRepository.getTemplateMemory(code),
    momentTypeCode,
    options?.enabled ?? true,
    persistTemplateMemory,
  );
}

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { dedupeFetch, isInflight } from "@/lib/cache/cacheStore";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import type { PersonalMomentsHomeResponse } from "@/lib/api/personal";
import { usePersonalMomentSession } from "@/hooks/usePersonalMomentSession";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";
import {
  delay,
  isSnapshotRebuilding,
  SNAPSHOT_REBUILDING_DELAY_MS,
  SNAPSHOT_REBUILDING_MAX_ATTEMPTS,
} from "@/lib/cache/snapshotRebuilding";
import {
  ensurePersonalSessionBootstrap,
  loadMomentsFromDisk,
  persistMoments,
  usePersonalSessionStore,
} from "@/stores/personalSessionStore";

const TTL_MS = FRESH_TTL_MS;

type CacheEntry = { data: PersonalMomentsHomeResponse; at: number };
const cache = new Map<PersonalMomentTypeCode, CacheEntry>();

export function invalidatePersonalMomentsCache(typeCode?: PersonalMomentTypeCode) {
  if (typeCode) {
    cache.delete(typeCode);
    return;
  }
  cache.clear();
}

export function seedPersonalMomentsCache(
  typeCode: PersonalMomentTypeCode,
  data: PersonalMomentsHomeResponse,
) {
  cache.set(typeCode, { data, at: Date.now() });
}

export function getPersonalMomentsCache(
  typeCode: PersonalMomentTypeCode,
): PersonalMomentsHomeResponse | null {
  return cache.get(typeCode)?.data ?? null;
}

function getInitialPersonalMoments(typeCode: PersonalMomentTypeCode): CacheEntry | null {
  const memoryValue = cache.get(typeCode);
  if (memoryValue) return memoryValue;
  const diskValue = loadMomentsFromDisk(typeCode);
  if (diskValue) {
    const entry = { data: diskValue, at: Date.now() };
    cache.set(typeCode, entry);
    return entry;
  }
  return null;
}

export function usePersonalMoments(options?: { enabled?: boolean }) {
  const enabled = options?.enabled ?? true;
  const momentTypeCode = usePersonalMomentSession();
  const generation = usePersonalSessionStore().generation;
  const initialCache = getInitialPersonalMoments(momentTypeCode);
  const [moments, setMoments] = useState<PersonalMomentsHomeResponse | null>(
    () => initialCache?.data ?? null,
  );
  const [loading, setLoading] = useState(() => !initialCache?.data);
  const [refreshing, setRefreshing] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadGeneration = useRef(0);

  const load = useCallback(
    async (force = false) => {
      const gen = ++loadGeneration.current;
      let entry = cache.get(momentTypeCode);
      if (!entry && !force) {
        entry = getInitialPersonalMoments(momentTypeCode) ?? undefined;
      }
      const age = entry ? Date.now() - entry.at : Infinity;
      const fresh = !force && entry && age < TTL_MS;
      const staleUsable = !force && entry && age < STALE_TTL_MS;
      if (fresh && entry) {
        setMoments(entry.data);
        setLoading(false);
        setRefreshing(false);
        setRebuilding(false);
        return;
      }
      if (entry) {
        setMoments(entry.data);
        setLoading(false);
        setRefreshing(Boolean(staleUsable) || age >= TTL_MS);
      } else {
        setLoading(true);
        setRefreshing(false);
      }
      setError(null);

      let attempt = 0;
      while (true) {
        try {
          const bootstrapKey = `personal:session_bootstrap:${momentTypeCode}`;
          const shouldTryBootstrap =
            !force &&
            !entry &&
            attempt === 0 &&
            (isInflight(bootstrapKey) || !isInflight(`personal:moments:${momentTypeCode}`));
          let data: PersonalMomentsHomeResponse;
          if (shouldTryBootstrap) {
            const bootstrap = await ensurePersonalSessionBootstrap(momentTypeCode, force);
            data = bootstrap.moments_home;
          } else {
            data = await dedupeFetch(
              `personal:moments:${momentTypeCode}${force ? `:force:${attempt}` : ""}`,
              () =>
                PersonalRepository.getMomentsHome({
                  momentTypeCode,
                  forceRefresh: force,
                }),
            );
          }
          if (gen !== loadGeneration.current) return;
          cache.set(momentTypeCode, { data, at: Date.now() });
          persistMoments(momentTypeCode, data);
          setMoments(data);
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
          if (!entry) {
            setError(err instanceof Error ? err.message : "Failed to load moments");
          }
          break;
        }
      }

      if (gen !== loadGeneration.current) return;
      setLoading(false);
      setRefreshing(false);
      setRebuilding(false);
    },
    [momentTypeCode],
  );

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      setRefreshing(false);
      setRebuilding(false);
      return;
    }
    const entry = getInitialPersonalMoments(momentTypeCode);
    setMoments(entry?.data ?? null);
    setLoading(!entry?.data);
    setRefreshing(false);
    setRebuilding(false);
    void load(false);
  }, [momentTypeCode, load, enabled, generation]);

  const refreshAfterSetup = useCallback(() => {
    invalidatePersonalMomentsCache(momentTypeCode);
    return load(false);
  }, [load, momentTypeCode]);

  return {
    moments,
    loading,
    refreshing,
    rebuilding,
    error,
    momentTypeCode,
    reload: () => load(true),
    revalidate: () => load(false),
    refreshAfterSetup,
  };
}

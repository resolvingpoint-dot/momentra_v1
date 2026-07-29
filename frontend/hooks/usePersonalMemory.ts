"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { dedupeFetch } from "@/lib/cache/cacheStore";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import type { PersonalMemoryResponse } from "@/lib/api/personal";
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
  loadMemoryFromDisk,
  persistMemory,
  usePersonalSessionStore,
} from "@/stores/personalSessionStore";

const TTL_MS = FRESH_TTL_MS;

type CacheEntry = { data: PersonalMemoryResponse; at: number };
const cache = new Map<PersonalMomentTypeCode, CacheEntry>();

export function invalidatePersonalMemoryCache(typeCode?: PersonalMomentTypeCode) {
  if (typeCode) {
    cache.delete(typeCode);
    return;
  }
  cache.clear();
}

export function seedPersonalMemoryCache(
  typeCode: PersonalMomentTypeCode,
  data: PersonalMemoryResponse,
) {
  cache.set(typeCode, { data, at: Date.now() });
}

export function getPersonalMemoryCache(
  typeCode: PersonalMomentTypeCode,
): PersonalMemoryResponse | null {
  return cache.get(typeCode)?.data ?? null;
}

function getInitialPersonalMemory(typeCode: PersonalMomentTypeCode): CacheEntry | null {
  const memoryValue = cache.get(typeCode);
  if (memoryValue) return memoryValue;
  const diskValue = loadMemoryFromDisk(typeCode);
  if (diskValue) {
    const entry = { data: diskValue, at: Date.now() };
    cache.set(typeCode, entry);
    return entry;
  }
  return null;
}

export function usePersonalMemory(options?: { enabled?: boolean }) {
  const enabled = options?.enabled ?? true;
  const momentTypeCode = usePersonalMomentSession();
  const generation = usePersonalSessionStore().generation;
  const initialCache = getInitialPersonalMemory(momentTypeCode);
  const [memory, setMemory] = useState<PersonalMemoryResponse | null>(
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
        entry = getInitialPersonalMemory(momentTypeCode) ?? undefined;
      }
      const age = entry ? Date.now() - entry.at : Infinity;
      const fresh = !force && entry && age < TTL_MS;
      const staleUsable = !force && entry && age < STALE_TTL_MS;
      if (fresh && entry) {
        setMemory(entry.data);
        setLoading(false);
        setRefreshing(false);
        setRebuilding(false);
        return;
      }
      if (entry) {
        setMemory(entry.data);
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
          const data = await dedupeFetch(
            `personal:memory:${momentTypeCode}${force ? `:force:${attempt}` : ""}`,
            () =>
              PersonalRepository.getMemory({
                momentTypeCode,
                forceRefresh: force,
              }),
          );
          if (gen !== loadGeneration.current) return;
          cache.set(momentTypeCode, { data, at: Date.now() });
          persistMemory(momentTypeCode, data);
          setMemory(data);
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
            setError(err instanceof Error ? err.message : "Failed to load memory");
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
    const entry = getInitialPersonalMemory(momentTypeCode);
    setMemory(entry?.data ?? null);
    setLoading(!entry?.data);
    setRefreshing(false);
    setRebuilding(false);
    void load(false);
  }, [momentTypeCode, load, enabled, generation]);

  const refreshAfterSetup = useCallback(() => {
    invalidatePersonalMemoryCache(momentTypeCode);
    return load(false);
  }, [load, momentTypeCode]);

  return {
    memory,
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

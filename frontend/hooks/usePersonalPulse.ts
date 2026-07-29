"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import type { PersonalPulseResponse } from "@/lib/api/personal";
import { usePersonalMomentSession } from "@/hooks/usePersonalMomentSession";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import {
  applyOptimisticPatch,
  reconcilePatch,
  rollbackPatch,
  subscribeOptimisticPulse,
} from "@/lib/telemetry/optimisticPulse";
import { endLoginToPulseSpan, markPulseLoadStart, markPulseTimeToVisible } from "@/lib/telemetry/performanceTelemetry";

import { dedupeFetch, isInflight } from "@/lib/cache/cacheStore";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";
import {
  delay,
  isSnapshotRebuilding,
  SNAPSHOT_REBUILDING_DELAY_MS,
  SNAPSHOT_REBUILDING_MAX_ATTEMPTS,
} from "@/lib/cache/snapshotRebuilding";
import {
  ensurePersonalSessionBootstrap,
  loadPulseFromDisk,
  persistPulse,
  usePersonalSessionStore,
} from "@/stores/personalSessionStore";

const TTL_MS = FRESH_TTL_MS;

type CacheEntry = { data: PersonalPulseResponse; at: number };
const cache = new Map<PersonalMomentTypeCode, CacheEntry>();

export function invalidatePersonalPulseCache(typeCode?: PersonalMomentTypeCode) {
  if (typeCode) {
    cache.delete(typeCode);
    return;
  }
  cache.clear();
}

export function seedPersonalPulseCache(
  typeCode: PersonalMomentTypeCode,
  data: PersonalPulseResponse,
) {
  cache.set(typeCode, { data, at: Date.now() });
}

export function getPersonalPulseCache(
  typeCode: PersonalMomentTypeCode,
): PersonalPulseResponse | null {
  return cache.get(typeCode)?.data ?? null;
}

function getInitialPersonalPulse(typeCode: PersonalMomentTypeCode): CacheEntry | null {
  const memoryValue = cache.get(typeCode);
  if (memoryValue) return memoryValue;
  const diskValue = loadPulseFromDisk(typeCode);
  if (diskValue) {
    const entry = { data: diskValue, at: Date.now() };
    cache.set(typeCode, entry);
    return entry;
  }
  return null;
}

export function usePersonalPulse(options?: { enabled?: boolean }) {
  const enabled = options?.enabled ?? true;
  const momentTypeCode = usePersonalMomentSession();
  const generation = usePersonalSessionStore().generation;
  const initialCache = getInitialPersonalPulse(momentTypeCode);
  const [pulse, setPulse] = useState<PersonalPulseResponse | null>(
    () => initialCache?.data ?? null,
  );
  const [loading, setLoading] = useState(() => !initialCache?.data);
  const [refreshing, setRefreshing] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadGeneration = useRef(0);
  const paintedVisible = useRef(false);

  useEffect(() => {
    markPulseLoadStart();
    paintedVisible.current = false;
  }, [momentTypeCode]);

  useEffect(() => {
    if (pulse && !loading && !paintedVisible.current) {
      paintedVisible.current = true;
      markPulseTimeToVisible({
        source: refreshing ? "stale-while-revalidate" : "ready",
        momentTypeCode,
      });
    }
  }, [pulse, loading, refreshing, momentTypeCode]);

  useEffect(() => {
    return subscribeOptimisticPulse((typeCode, nextPulse) => {
      if (typeCode !== momentTypeCode) return;
      setPulse(nextPulse);
      if (nextPulse) {
        cache.set(momentTypeCode, { data: nextPulse, at: Date.now() });
      }
    });
  }, [momentTypeCode]);

  const load = useCallback(
    async (force = false) => {
      const gen = ++loadGeneration.current;
      let entry = cache.get(momentTypeCode);
      if (!entry && !force) {
        entry = getInitialPersonalPulse(momentTypeCode) ?? undefined;
      }
      const age = entry ? Date.now() - entry.at : Infinity;
      const fresh = !force && entry && age < TTL_MS;
      const staleUsable = !force && entry && age < STALE_TTL_MS;
      if (fresh && entry) {
        setPulse(entry.data);
        setLoading(false);
        setRefreshing(false);
        setRebuilding(false);
        return;
      }
      if (entry) {
        setPulse(entry.data);
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
            (isInflight(bootstrapKey) || !isInflight(`personal:pulse:${momentTypeCode}`));
          let data: PersonalPulseResponse;
          if (shouldTryBootstrap) {
            const bootstrap = await ensurePersonalSessionBootstrap(momentTypeCode, force);
            data = bootstrap.pulse;
          } else {
            data = await dedupeFetch(
              `personal:pulse:${momentTypeCode}${force ? `:force:${attempt}` : ""}`,
              () =>
                PersonalRepository.getPulse({
                  momentTypeCode,
                  forceRefresh: force,
                }),
            );
          }
          if (gen !== loadGeneration.current) return;
          cache.set(momentTypeCode, { data, at: Date.now() });
          persistPulse(momentTypeCode, data);
          setPulse(data);
          setRebuilding(false);
          endLoginToPulseSpan();
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
          setError(err instanceof Error ? err.message : "Failed to load pulse");
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
    const entry = getInitialPersonalPulse(momentTypeCode);
    setPulse(entry?.data ?? null);
    setLoading(!entry?.data);
    setRefreshing(false);
    setRebuilding(false);
    // Prefer skipping cold bootstrap when cache was just invalidated (no entry):
    // callers that need force use reload/refreshAfterSetup.
    void load(false);
  }, [momentTypeCode, load, enabled, generation]);

  const refreshAfterSetup = useCallback(() => {
    invalidatePersonalPulseCache(momentTypeCode);
    return load(false);
  }, [load, momentTypeCode]);

  const applyOptimistic = useCallback(
    (clientRequestId: string, patch: Partial<PersonalPulseResponse>) => {
      const current = cache.get(momentTypeCode)?.data ?? pulse;
      const merged = applyOptimisticPatch(momentTypeCode, clientRequestId, current, patch);
      if (merged) {
        setPulse(merged);
        cache.set(momentTypeCode, { data: merged, at: Date.now() });
      }
      return merged;
    },
    [momentTypeCode, pulse],
  );

  const reconcile = useCallback(
    (clientRequestId: string, serverPulse: PersonalPulseResponse) => {
      const next = reconcilePatch(clientRequestId, serverPulse);
      setPulse(next);
      cache.set(momentTypeCode, { data: next, at: Date.now() });
      return next;
    },
    [momentTypeCode],
  );

  const rollback = useCallback(
    (clientRequestId: string) => {
      const previous = rollbackPatch(clientRequestId);
      setPulse(previous);
      if (previous) {
        cache.set(momentTypeCode, { data: previous, at: Date.now() });
      } else {
        cache.delete(momentTypeCode);
      }
      return previous;
    },
    [momentTypeCode],
  );

  return {
    pulse,
    loading,
    refreshing,
    rebuilding,
    error,
    momentTypeCode,
    reload: () => load(true),
    revalidate: () => load(false),
    refreshAfterSetup,
    applyOptimisticPatch: applyOptimistic,
    reconcilePatch: reconcile,
    rollbackPatch: rollback,
  };
}

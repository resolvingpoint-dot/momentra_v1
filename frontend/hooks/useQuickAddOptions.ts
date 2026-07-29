"use client";

import { useCallback, useEffect, useState } from "react";
import { getPersonalQuickAddOptions, type PersonalQuickAddOptionsResponse } from "@/lib/api/client";

const TTL_MS = 5 * 60 * 1000;

type CacheEntry = { data: PersonalQuickAddOptionsResponse; at: number };
const cache = new Map<string, CacheEntry>();

function cacheKey(momentId?: string | null) {
  return momentId ?? "__all__";
}

export function invalidateQuickAddOptionsCache(momentId?: string | null) {
  if (momentId) {
    cache.delete(cacheKey(momentId));
    cache.delete(cacheKey(null));
    return;
  }
  cache.clear();
}

export function getQuickAddOptionsCache(
  momentId?: string | null,
): PersonalQuickAddOptionsResponse | null {
  return cache.get(cacheKey(momentId))?.data ?? null;
}

export function prefetchQuickAddOptions(momentId?: string | null, force = false) {
  const key = cacheKey(momentId);
  const entry = cache.get(key);
  const fresh = !force && entry && Date.now() - entry.at < TTL_MS;
  if (fresh) return Promise.resolve(entry!.data);

  return getPersonalQuickAddOptions(momentId ?? undefined).then((data) => {
    cache.set(key, { data, at: Date.now() });
    return data;
  });
}

export function useQuickAddOptions(options?: {
  momentId?: string | null;
  enabled?: boolean;
}) {
  const momentId = options?.momentId ?? null;
  const enabled = options?.enabled ?? true;
  const key = cacheKey(momentId);
  const cached = cache.get(key);
  const [data, setData] = useState<PersonalQuickAddOptionsResponse | null>(cached?.data ?? null);
  const [loading, setLoading] = useState(!cached);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (force = false) => {
      const entry = cache.get(key);
      const fresh = !force && entry && Date.now() - entry.at < TTL_MS;
      if (fresh && entry) {
        setData(entry.data);
        setLoading(false);
        setRefreshing(false);
        return entry.data;
      }
      if (entry) {
        setData(entry.data);
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      try {
        const next = await getPersonalQuickAddOptions(momentId ?? undefined);
        cache.set(key, { data: next, at: Date.now() });
        setData(next);
        return next;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load options");
        return null;
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [key, momentId],
  );

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    const entry = cache.get(key);
    setData(entry?.data ?? null);
    setLoading(!entry);
    void load(false);
  }, [enabled, key, load]);

  return {
    options: data,
    loading,
    refreshing,
    error,
    reload: () => load(true),
  };
}

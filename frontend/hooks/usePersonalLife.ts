"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { dedupeFetch } from "@/lib/cache/cacheStore";
import { getPersonalLife } from "@/lib/api/client";
import type { PersonalLifeResponse } from "@/lib/api/personal";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";
import {
  delay,
  isSnapshotRebuilding,
  SNAPSHOT_REBUILDING_DELAY_MS,
  SNAPSHOT_REBUILDING_MAX_ATTEMPTS,
} from "@/lib/cache/snapshotRebuilding";
import { loadLifeFromDisk, persistLife, usePersonalSessionStore } from "@/stores/personalSessionStore";

let cachedLife: PersonalLifeResponse | null = null;
let cachedAt = 0;
let cachedProjectionVersion: number | undefined;
const TTL_MS = FRESH_TTL_MS;

function ensureLifeMemoryFromDisk(): PersonalLifeResponse | null {
  if (cachedLife) return cachedLife;
  const disk = loadLifeFromDisk();
  if (disk) {
    cachedLife = disk;
    cachedAt = Date.now();
    cachedProjectionVersion = disk.projection_version;
  }
  return cachedLife;
}

export function invalidatePersonalLifeCache() {
  cachedLife = null;
  cachedAt = 0;
  cachedProjectionVersion = undefined;
}

export function seedPersonalLifeCache(data: PersonalLifeResponse) {
  cachedLife = data;
  cachedAt = Date.now();
  cachedProjectionVersion = data.projection_version;
}

export function getPersonalLifeCache(): PersonalLifeResponse | null {
  return cachedLife ?? loadLifeFromDisk();
}

export function usePersonalLife(options?: { enabled?: boolean }) {
  const enabled = options?.enabled ?? true;
  const generation = usePersonalSessionStore().generation;
  const initial = ensureLifeMemoryFromDisk();
  const [life, setLife] = useState<PersonalLifeResponse | null>(() => initial);
  const [loading, setLoading] = useState(() => !initial);
  const [refreshing, setRefreshing] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadGeneration = useRef(0);

  const load = useCallback(async (force = false) => {
    const gen = ++loadGeneration.current;
    if (!cachedLife && !force) {
      ensureLifeMemoryFromDisk();
    }
    const age = cachedLife ? Date.now() - cachedAt : Infinity;
    const fresh = !force && cachedLife && age < TTL_MS;
    const staleUsable = !force && cachedLife && age < STALE_TTL_MS;
    if (fresh && cachedLife) {
      setLife(cachedLife);
      setLoading(false);
      setRefreshing(false);
      setRebuilding(false);
      return;
    }
    if (cachedLife) {
      setLife(cachedLife);
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
          `personal:life${force ? `:force:${attempt}` : ""}`,
          () => getPersonalLife({ forceRefresh: force }),
        );
        if (gen !== loadGeneration.current) return;
        const nextVersion = data.projection_version;
        if (
          !force &&
          cachedLife &&
          nextVersion !== undefined &&
          cachedProjectionVersion === nextVersion
        ) {
          cachedAt = Date.now();
          setLife(cachedLife);
          setRebuilding(false);
          break;
        }
        cachedLife = data;
        cachedAt = Date.now();
        cachedProjectionVersion = nextVersion;
        persistLife(data);
        setLife(data);
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
        if (!cachedLife) {
          const message = err instanceof Error ? err.message : "Failed to load life";
          setError(
            message.includes("timed out") || message.includes("CORS") || message.includes("Failed to fetch")
              ? `${message} — check that the API (ngrok) is up and restarted after recent backend changes.`
              : message,
          );
        }
        break;
      }
    }

    if (gen !== loadGeneration.current) return;
    setLoading(false);
    setRefreshing(false);
    setRebuilding(false);
  }, []);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      setRefreshing(false);
      setRebuilding(false);
      return;
    }
    const current = ensureLifeMemoryFromDisk();
    setLife(current);
    setLoading(!current);
    setRefreshing(false);
    setRebuilding(false);
    void load(false);
  }, [load, enabled, generation]);

  const refreshAfterSetup = useCallback(() => {
    invalidatePersonalLifeCache();
    return load(false);
  }, [load]);

  return {
    life,
    loading,
    refreshing,
    rebuilding,
    error,
    reload: () => load(true),
    revalidate: () => load(false),
    refreshAfterSetup,
  };
}

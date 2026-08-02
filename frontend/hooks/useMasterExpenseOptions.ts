"use client";

import { useCallback, useEffect, useState } from "react";
import { getMasterExpenseOptions, type PersonalMasterExpenseOptionsResponse } from "@/lib/api/client";
import { diskCacheLoad, diskCacheSave, dedupeFetch } from "@/lib/cache/cacheStore";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";

const TTL_MS = 5 * 60 * 1000; // match Personal Quick Add options
const CACHE_KEY = "personal:master_expense_options:v1";

type CacheEntry = { data: PersonalMasterExpenseOptionsResponse; at: number };
let mem: CacheEntry | null = null;

export function invalidateMasterExpenseOptionsCache() {
  mem = null;
  try {
    diskCacheSave(CACHE_KEY, null as unknown as PersonalMasterExpenseOptionsResponse);
  } catch {
    /* ignore */
  }
}

export function peekMasterExpenseOptions(): PersonalMasterExpenseOptionsResponse | null {
  if (mem && Date.now() - mem.at < STALE_TTL_MS) return mem.data;
  const disk = diskCacheLoad<PersonalMasterExpenseOptionsResponse>(CACHE_KEY, STALE_TTL_MS);
  if (disk) {
    mem = { data: disk, at: Date.now() };
    return disk;
  }
  return null;
}

export async function prefetchMasterExpenseOptions(force = false): Promise<PersonalMasterExpenseOptionsResponse | null> {
  if (!force && mem && Date.now() - mem.at < FRESH_TTL_MS) return mem.data;
  try {
    const data = await dedupeFetch(`fetch:${CACHE_KEY}`, () => getMasterExpenseOptions());
    mem = { data, at: Date.now() };
    diskCacheSave(CACHE_KEY, data);
    return data;
  } catch {
    return peekMasterExpenseOptions();
  }
}

/** Load only when Master Expense sheet is open (`enabled`). */
export function useMasterExpenseOptions(options?: { enabled?: boolean }) {
  const enabled = options?.enabled ?? true;
  const seeded = peekMasterExpenseOptions();
  const [data, setData] = useState<PersonalMasterExpenseOptionsResponse | null>(seeded);
  const [loading, setLoading] = useState(enabled && !seeded);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (force = false) => {
    const fresh = !force && mem && Date.now() - mem.at < TTL_MS;
    if (fresh && mem) {
      setData(mem.data);
      setLoading(false);
      return mem.data;
    }
    if (mem) setData(mem.data);
    else setLoading(true);
    setError(null);
    try {
      const next = await dedupeFetch(`fetch:${CACHE_KEY}`, () => getMasterExpenseOptions());
      mem = { data: next, at: Date.now() };
      diskCacheSave(CACHE_KEY, next);
      setData(next);
      return next;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load options");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    const peek = peekMasterExpenseOptions();
    setData(peek);
    setLoading(!peek);
    void load(false);
  }, [enabled, load]);

  return { options: data, loading, error, reload: load };
}

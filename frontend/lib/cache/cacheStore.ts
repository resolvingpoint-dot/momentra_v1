type CacheEntry<T> = {
  data: T;
  fetchedAt: number;
};

const DEFAULT_TTL_MS = 5 * 60 * 1000;
const memory = new Map<string, CacheEntry<unknown>>();
const inflight = new Map<string, Promise<unknown>>();

export function cacheGet<T>(key: string, ttlMs = DEFAULT_TTL_MS): T | null {
  const entry = memory.get(key) as CacheEntry<T> | undefined;
  if (!entry) return null;
  if (Date.now() - entry.fetchedAt > ttlMs) return null;
  return entry.data;
}

export function cachePeek<T>(key: string): T | null {
  const entry = memory.get(key) as CacheEntry<T> | undefined;
  return entry?.data ?? null;
}

export function cacheSet<T>(key: string, data: T): void {
  memory.set(key, { data, fetchedAt: Date.now() });
}

export function cacheInvalidate(prefix?: string): void {
  if (!prefix) {
    memory.clear();
    inflight.clear();
    return;
  }
  for (const key of memory.keys()) {
    if (key.startsWith(prefix)) memory.delete(key);
  }
  for (const key of inflight.keys()) {
    if (key.startsWith(prefix)) inflight.delete(key);
  }
}

export async function cacheFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: { force?: boolean; ttlMs?: number } = {},
): Promise<T> {
  const { force = false, ttlMs = DEFAULT_TTL_MS } = options;
  if (!force) {
    const cached = cacheGet<T>(key, ttlMs);
    if (cached !== null) return cached;
    const stale = cachePeek<T>(key);
    if (stale !== null) {
      void dedupeFetch(key, fetcher).then((data) => cacheSet(key, data)).catch(() => {});
      return stale;
    }
  }
  const data = await dedupeFetch(key, fetcher);
  cacheSet(key, data);
  return data;
}

export async function dedupeFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const existing = inflight.get(key) as Promise<T> | undefined;
  if (existing) return existing;
  const promise = fetcher().finally(() => inflight.delete(key));
  inflight.set(key, promise);
  return promise;
}

export function isInflight(key: string): boolean {
  return inflight.has(key);
}

const DISK_PREFIX = "momentra:cache:";

type DiskCacheEnvelope<T> = {
  v: 1;
  data: T;
  savedAt: number;
};

function isDiskEnvelope<T>(value: unknown): value is DiskCacheEnvelope<T> {
  return (
    typeof value === "object" &&
    value !== null &&
    (value as DiskCacheEnvelope<T>).v === 1 &&
    "data" in value &&
    "savedAt" in value
  );
}

export function diskCacheLoad<T>(key: string, ttlMs?: number): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(`${DISK_PREFIX}${key}`);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    if (isDiskEnvelope<T>(parsed)) {
      if (ttlMs != null && Date.now() - parsed.savedAt > ttlMs) return null;
      return parsed.data;
    }
    return parsed as T;
  } catch {
    return null;
  }
}

export function diskCacheSave<T>(key: string, data: T): void {
  if (typeof window === "undefined") return;
  try {
    const envelope: DiskCacheEnvelope<T> = { v: 1, data, savedAt: Date.now() };
    window.localStorage.setItem(`${DISK_PREFIX}${key}`, JSON.stringify(envelope));
  } catch {
    // quota or private mode — ignore
  }
}

export function diskCacheRemove(key: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(`${DISK_PREFIX}${key}`);
}

export function diskCacheClearAll(): void {
  if (typeof window === "undefined") return;
  const keys: string[] = [];
  for (let i = 0; i < window.localStorage.length; i += 1) {
    const k = window.localStorage.key(i);
    if (k?.startsWith(DISK_PREFIX)) keys.push(k);
  }
  keys.forEach((k) => window.localStorage.removeItem(k));
}

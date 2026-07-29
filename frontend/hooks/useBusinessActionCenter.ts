"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchCatalog,
  fetchRendererMeta,
  createAction,
  type BusinessActionCatalogResponse,
  type BusinessCatalogAction,
  type BusinessRendererMeta,
  type BusinessActivityPayload,
} from "@/repositories/BusinessActionRepository";
import {
  getFavoriteActionIds,
  getRecentActionIds,
  toggleFavoriteAction,
} from "@/lib/action-center/actionCenterPrefs";
import { diskCacheLoad, diskCacheSave, dedupeFetch } from "@/lib/cache/cacheStore";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";

type CatalogEntry = { data: BusinessActionCatalogResponse; at: number };
const catalogMem = new Map<string, CatalogEntry>();

function catalogKey(momentId: string) {
  return `business:action_catalog:${momentId}`;
}

export function seedBusinessActionCatalog(
  momentId: string,
  data: BusinessActionCatalogResponse,
) {
  const key = catalogKey(momentId);
  catalogMem.set(key, { data, at: Date.now() });
  diskCacheSave(key, data);
}

export function peekBusinessActionCatalog(
  momentId: string,
): BusinessActionCatalogResponse | null {
  const key = catalogKey(momentId);
  const mem = catalogMem.get(key);
  if (mem && Date.now() - mem.at < STALE_TTL_MS) return mem.data;
  const disk = diskCacheLoad<BusinessActionCatalogResponse>(key, STALE_TTL_MS);
  if (disk) {
    catalogMem.set(key, { data: disk, at: Date.now() });
    return disk;
  }
  return null;
}

export async function prefetchBusinessActionCatalog(momentId: string): Promise<void> {
  if (!momentId) return;
  const key = catalogKey(momentId);
  const mem = catalogMem.get(key);
  if (mem && Date.now() - mem.at < FRESH_TTL_MS) return;
  try {
    const data = await dedupeFetch(`fetch:${key}`, () => fetchCatalog(momentId));
    seedBusinessActionCatalog(momentId, data);
  } catch {
    // Warm path — ignore; Action Center will surface errors on open.
  }
}

export type UseBusinessActionCenterReturn = {
  catalog: BusinessActionCatalogResponse | null;
  loading: boolean;
  error: string | null;
  selectedAction: BusinessCatalogAction | null;
  rendererMeta: BusinessRendererMeta | null;
  rendererLoading: boolean;
  favorites: string[];
  recentIds: string[];
  selectAction: (actionId: string | null) => void;
  toggleFavorite: (actionId: string) => void;
  submitAction: (payload: Record<string, unknown>) => Promise<void>;
};

export function useBusinessActionCenter(
  momentId: string,
  userId = "local",
): UseBusinessActionCenterReturn {
  const seeded = peekBusinessActionCatalog(momentId);
  const [catalog, setCatalog] = useState<BusinessActionCatalogResponse | null>(seeded);
  const [loading, setLoading] = useState(!seeded);
  const [error, setError] = useState<string | null>(null);

  const [selectedActionId, setSelectedActionId] = useState<string | null>(null);
  const [rendererMeta, setRendererMeta] = useState<BusinessRendererMeta | null>(null);
  const [rendererLoading, setRendererLoading] = useState(false);

  const templateId = catalog?.template_id ?? "business.default";
  const [favorites, setFavorites] = useState<string[]>(() =>
    seeded ? getFavoriteActionIds(userId, seeded.template_id) : [],
  );
  const recentIds = useMemo(
    () => (catalog ? getRecentActionIds(userId, templateId) : []),
    [catalog, userId, templateId],
  );

  useEffect(() => {
    let cancelled = false;
    const peek = peekBusinessActionCatalog(momentId);
    if (peek) {
      setCatalog(peek);
      setFavorites(getFavoriteActionIds(userId, peek.template_id));
      setLoading(false);
    } else {
      setLoading(true);
    }
    setError(null);
    void (async () => {
      try {
        const data = await dedupeFetch(`fetch:${catalogKey(momentId)}`, () =>
          fetchCatalog(momentId),
        );
        if (cancelled) return;
        seedBusinessActionCatalog(momentId, data);
        setCatalog(data);
        setFavorites(getFavoriteActionIds(userId, data.template_id));
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load catalog");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [momentId, userId]);

  const selectedAction = useMemo(() => {
    if (!selectedActionId || !catalog) return null;
    return catalog.actions.find((a) => a.action_id === selectedActionId) ?? null;
  }, [selectedActionId, catalog]);

  useEffect(() => {
    if (!selectedAction) {
      setRendererMeta(null);
      return;
    }
    let cancelled = false;
    setRendererLoading(true);
    void (async () => {
      try {
        const meta = await fetchRendererMeta(momentId, selectedAction.action_id);
        if (!cancelled) setRendererMeta(meta);
      } catch {
        if (!cancelled) setRendererMeta(null);
      } finally {
        if (!cancelled) setRendererLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [selectedAction, momentId]);

  const selectAction = useCallback((id: string | null) => {
    setSelectedActionId(id);
  }, []);

  const toggleFav = useCallback(
    (actionId: string) => {
      setFavorites(toggleFavoriteAction(userId, templateId, actionId));
    },
    [userId, templateId],
  );

  const submitAction = useCallback(
    async (payload: Record<string, unknown>) => {
      if (!selectedAction) throw new Error("No action selected");
      const clientRequestId =
        typeof crypto !== "undefined" && "randomUUID" in crypto
          ? crypto.randomUUID()
          : `biz-${Date.now()}`;
      const body: BusinessActivityPayload = {
        action_type: selectedAction.action_type,
        title: String(payload.title ?? selectedAction.label),
        subtitle: payload.subtitle ? String(payload.subtitle) : undefined,
        payload,
        client_request_id: clientRequestId,
        source: "action_center",
      };
      return createAction(momentId, body);
    },
    [selectedAction, momentId],
  );

  return {
    catalog,
    loading,
    error,
    selectedAction,
    rendererMeta,
    rendererLoading,
    favorites,
    recentIds,
    selectAction,
    toggleFavorite: toggleFav,
    submitAction,
  };
}

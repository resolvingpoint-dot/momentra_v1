/**
 * Authoritative Business session store.
 *
 * Owns: moments inventory, selectedMomentId/Type, createOptions, load state, lastLoadedAt.
 * Clients must not keep a separate selected-moment copy.
 */
import { useSyncExternalStore } from "react";
import { dedupeFetch } from "@/lib/cache/cacheStore";
import type {
  BusinessCreateOptionsResponse,
  BusinessMomentResponse,
  BusinessSessionBootstrapResponse,
  BusinessWorkspaceSummary,
} from "@/lib/api/business";
import { BusinessRepository } from "@/repositories/BusinessRepository";
import { logBusinessLoad } from "@/lib/telemetry/businessLoadTelemetry";
import {
  isActiveBusinessMomentStatus,
  resolveBusinessMomentSwitcherOptions,
  type BusinessMomentSwitcherOption,
} from "@/components/business/shared/businessMomentRouting";
import {
  areAllBusinessMomentsReseated,
  clearBusinessMomentReseatMarks,
  getBusinessMomentReseatedIds,
} from "@/lib/business/businessMomentAccess";

const CREATE_OPTIONS_FRESH_MS = 60_000;
const BOOTSTRAP_FRESH_MS = 60_000;

export type BusinessSessionSnapshot = {
  bootstrap: BusinessSessionBootstrapResponse | null;
  createOptions: BusinessCreateOptionsResponse | null;
  selectedMomentId: string | null;
  selectedMomentType: string;
  selectedWorkspaceId: string | null;
  loading: boolean;
  createOptionsLoading: boolean;
  error: string | null;
  lastLoadedAt: number | null;
  createOptionsLastLoadedAt: number | null;
  generation: number;
};

let snapshot: BusinessSessionSnapshot = {
  bootstrap: null,
  createOptions: null,
  selectedMomentId: null,
  selectedMomentType: "",
  selectedWorkspaceId: null,
  loading: false,
  createOptionsLoading: false,
  error: null,
  lastLoadedAt: null,
  createOptionsLastLoadedAt: null,
  generation: 0,
};

const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((fn) => fn());
}

function setSnapshot(patch: Partial<BusinessSessionSnapshot>) {
  snapshot = { ...snapshot, ...patch };
  notify();
}

export function getBusinessSessionSnapshot(): BusinessSessionSnapshot {
  return snapshot;
}

export function subscribeBusinessSession(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useBusinessSessionStore(): BusinessSessionSnapshot {
  return useSyncExternalStore(
    subscribeBusinessSession,
    getBusinessSessionSnapshot,
    getBusinessSessionSnapshot,
  );
}

export function bumpBusinessSessionGeneration(): number {
  const next = snapshot.generation + 1;
  setSnapshot({ generation: next });
  return next;
}

function inventoryMoments(): BusinessMomentResponse[] {
  return snapshot.bootstrap?.moments ?? [];
}

/**
 * Selection fallback (once per inventory change):
 * persisted valid → first ACTIVE → PAUSED/COMPLETED → setup draft → none
 * Never silently re-resolve by type alone after validation.
 */
export function validateBusinessSelection(
  moments: BusinessMomentResponse[],
  currentId: string | null,
  currentType: string,
): { selectedMomentId: string | null; selectedMomentType: string } {
  const activeFamily = moments.filter((m) => {
    const status = (m.status ?? "").trim();
    if (!status) return true;
    return isActiveBusinessMomentStatus(status);
  });

  if (currentId) {
    const persisted = activeFamily.find((m) => m.moment_id === currentId);
    if (persisted) {
      return {
        selectedMomentId: persisted.moment_id,
        selectedMomentType:
          (persisted.moment_type_code ?? "").trim() || currentType,
      };
    }
  }

  const firstActive = activeFamily.find(
    (m) => (m.status ?? "").trim().toUpperCase() === "ACTIVE" || !(m.status ?? "").trim(),
  );
  if (firstActive?.moment_id) {
    return {
      selectedMomentId: firstActive.moment_id,
      selectedMomentType: (firstActive.moment_type_code ?? "").trim(),
    };
  }

  const firstPausedOrCompleted = activeFamily.find((m) => {
    const s = (m.status ?? "").trim().toUpperCase();
    return s === "PAUSED" || s === "COMPLETED";
  });
  if (firstPausedOrCompleted?.moment_id) {
    return {
      selectedMomentId: firstPausedOrCompleted.moment_id,
      selectedMomentType: (firstPausedOrCompleted.moment_type_code ?? "").trim(),
    };
  }

  const draft = moments.find((m) => {
    const s = (m.status ?? "").trim().toUpperCase();
    return s === "SETUP" || s === "DRAFT";
  });
  if (draft?.moment_id) {
    // Setup draft for routing only — not switcher chips.
    return {
      selectedMomentId: draft.moment_id,
      selectedMomentType: (draft.moment_type_code ?? "").trim() || currentType,
    };
  }

  return { selectedMomentId: null, selectedMomentType: currentType };
}

function isBusinessInventoryEmpty(
  bootstrap: BusinessSessionBootstrapResponse | null | undefined,
): boolean {
  if (!bootstrap) return true;
  const moments = bootstrap.moments ?? [];
  const home = bootstrap.moments_home;
  return (
    home?.is_empty === true ||
    (typeof home?.active_moment_count === "number" && home.active_moment_count === 0) ||
    moments.length === 0
  );
}

function filterBootstrapByExcludedIds(
  bootstrap: BusinessSessionBootstrapResponse,
  excludeIds: ReadonlySet<string>,
): BusinessSessionBootstrapResponse {
  if (excludeIds.size === 0) return bootstrap;
  const moments = (bootstrap.moments ?? []).filter((m) => !excludeIds.has(m.moment_id));
  const cards = (bootstrap.moments_home?.cards ?? []).filter(
    (c) => !c.linked_moment_id || !excludeIds.has(c.linked_moment_id),
  );
  const activeCount = moments.filter((m) =>
    isActiveBusinessMomentStatus(m.status ?? ""),
  ).length;
  const empty = moments.length === 0 || activeCount === 0;
  return {
    ...bootstrap,
    moments,
    moments_home: bootstrap.moments_home
      ? {
          ...bootstrap.moments_home,
          cards,
          active_moment_count: activeCount,
          is_empty: empty,
        }
      : bootstrap.moments_home,
  };
}

function applyInventorySelection(bootstrap: BusinessSessionBootstrapResponse) {
  const reseated = getBusinessMomentReseatedIds();
  const inventory =
    reseated.size > 0 ? filterBootstrapByExcludedIds(bootstrap, reseated) : bootstrap;
  const moments = inventory.moments ?? [];
  const next = validateBusinessSelection(
    moments,
    isBusinessInventoryEmpty(inventory) ? null : snapshot.selectedMomentId,
    snapshot.selectedMomentType,
  );
  const selectedWorkspaceId =
    inventory.selected_workspace?.id ?? snapshot.selectedWorkspaceId;
  setSnapshot({
    bootstrap: inventory,
    selectedMomentId: next.selectedMomentId,
    selectedMomentType: next.selectedMomentType,
    selectedWorkspaceId,
    lastLoadedAt: Date.now(),
    error: null,
  });
}

function applyEmptyBusinessSession(typeCode: string): void {
  bumpBusinessSessionGeneration();
  setSnapshot({
    selectedMomentId: null,
    selectedMomentType: typeCode,
    bootstrap: snapshot.bootstrap
      ? {
          ...snapshot.bootstrap,
          moments: [],
          moments_home: snapshot.bootstrap.moments_home
            ? {
                ...snapshot.bootstrap.moments_home,
                cards: [],
                is_empty: true,
                active_moment_count: 0,
              }
            : snapshot.bootstrap.moments_home,
        }
      : null,
  });
}

export function setBusinessSelection(
  typeCode: string,
  momentId: string | null,
): void {
  bumpBusinessSessionGeneration();
  setSnapshot({
    selectedMomentType: typeCode,
    selectedMomentId: momentId,
  });
}

export function getBusinessSwitcherOptions(): BusinessMomentSwitcherOption[] {
  return resolveBusinessMomentSwitcherOptions(
    snapshot.bootstrap?.moments_home?.cards ?? [],
    snapshot.createOptions?.cards ?? [],
    inventoryMoments(),
  );
}

export async function ensureBusinessBootstrap(
  force = false,
  workspaceId?: string | null,
): Promise<BusinessSessionBootstrapResponse | null> {
  const gen = snapshot.generation;
  const targetWs = workspaceId ?? snapshot.selectedWorkspaceId;
  const fresh =
    !force &&
    snapshot.bootstrap != null &&
    snapshot.lastLoadedAt != null &&
    Date.now() - snapshot.lastLoadedAt < BOOTSTRAP_FRESH_MS &&
    snapshot.error == null &&
    (targetWs == null ||
      snapshot.bootstrap.selected_workspace?.id === targetWs ||
      snapshot.selectedWorkspaceId === targetWs);
  if (fresh) return snapshot.bootstrap;

  setSnapshot({ loading: true, error: null });
  const t0 = performance.now();
  try {
    const cacheKey = targetWs
      ? `business:session_bootstrap:${targetWs}`
      : "business:session_bootstrap";
    const bootstrap = await dedupeFetch(cacheKey, () =>
      BusinessRepository.getSessionBootstrap(
        targetWs ? { workspaceId: targetWs } : undefined,
      ),
    );
    if (gen !== snapshot.generation && !force) {
      applyInventorySelection(bootstrap);
    } else {
      applyInventorySelection(bootstrap);
    }
    setSnapshot({ loading: false });
    logBusinessLoad({
      tab: "session",
      requestKey: "session_bootstrap",
      reason: force ? "force" : "open",
      cacheSource: "network",
      durationMs: Math.round(performance.now() - t0),
      generation: snapshot.generation,
      success: true,
      momentId: snapshot.selectedMomentId,
      momentType: snapshot.selectedMomentType,
    });
    return snapshot.bootstrap;
  } catch (e) {
    const message = e instanceof Error ? e.message : "Failed to load Business";
    setSnapshot({ loading: false, error: message });
    logBusinessLoad({
      tab: "session",
      requestKey: "session_bootstrap",
      reason: force ? "force" : "open",
      cacheSource: "network",
      durationMs: Math.round(performance.now() - t0),
      generation: snapshot.generation,
      success: false,
      errorCode: "bootstrap_failed",
    });
    return null;
  }
}

export function getSelectedBusinessWorkspace(): BusinessWorkspaceSummary | null {
  return snapshot.bootstrap?.selected_workspace ?? null;
}

export function getBusinessWorkspaces(): BusinessWorkspaceSummary[] {
  return snapshot.bootstrap?.workspaces ?? [];
}

export async function switchBusinessWorkspace(
  workspaceId: string,
): Promise<BusinessSessionBootstrapResponse | null> {
  bumpBusinessSessionGeneration();
  setSnapshot({ selectedWorkspaceId: workspaceId, selectedMomentId: null });
  try {
    await BusinessRepository.selectWorkspace(workspaceId);
  } catch {
    // Preference persist may fail offline; still reload scoped bootstrap.
  }
  return ensureBusinessBootstrap(true, workspaceId);
}

export async function createAndSelectBusinessWorkspace(name: string): Promise<
  BusinessSessionBootstrapResponse | null
> {
  const created = await BusinessRepository.createWorkspace({ name });
  bumpBusinessSessionGeneration();
  const prev = snapshot.bootstrap;
  const workspaces = [...(prev?.workspaces ?? []).filter((w) => w.id !== created.id), created];
  setSnapshot({
    selectedWorkspaceId: created.id,
    selectedMomentId: null,
    selectedMomentType: "",
    bootstrap: {
      moments_home: prev?.moments_home ?? {
        is_empty: true,
        active_moment_count: 0,
        cards: [],
      },
      moments: [],
      selected_workspace: created,
      workspaces,
      module_tiles: prev?.module_tiles ?? [],
      dashboard: prev?.dashboard ?? {
        open_moments: 0,
        pending_approvals: 0,
        member_count: 1,
      },
    },
    lastLoadedAt: Date.now(),
    error: null,
  });
  // Background soft reconcile — do not block create UX on a forced bootstrap.
  void softRefreshBusinessSession(created.id);
  return snapshot.bootstrap;
}

/**
 * Soft background refresh: prefers workspace moments/overview endpoints when
 * a company is selected; falls back to cached bootstrap TTL (never force).
 */
export async function softRefreshBusinessSession(
  workspaceId?: string | null,
): Promise<void> {
  const wsId =
    workspaceId ??
    snapshot.selectedWorkspaceId ??
    snapshot.bootstrap?.selected_workspace?.id ??
    null;
  if (!wsId) {
    await ensureBusinessBootstrap(false);
    return;
  }
  const gen = snapshot.generation;
  try {
    const [momentsPayload, overview] = await Promise.all([
      BusinessRepository.getWorkspaceMoments(wsId),
      BusinessRepository.getWorkspaceOverview(wsId),
    ]);
    if (gen !== snapshot.generation) return;
    const prev = snapshot.bootstrap;
    const next: BusinessSessionBootstrapResponse = {
      moments_home:
        momentsPayload.moments_home ??
        prev?.moments_home ?? {
          is_empty: true,
          active_moment_count: 0,
          cards: [],
        },
      moments: momentsPayload.moments ?? prev?.moments ?? [],
      selected_workspace: prev?.selected_workspace ?? null,
      workspaces: prev?.workspaces ?? [],
      module_tiles: prev?.module_tiles ?? [],
      dashboard: overview.dashboard ?? prev?.dashboard,
    };
    if (prev?.selected_workspace?.id === wsId || !prev?.selected_workspace) {
      applyInventorySelection(next);
    } else {
      setSnapshot({
        bootstrap: {
          ...next,
          selected_workspace: prev.selected_workspace,
          workspaces: prev.workspaces,
          module_tiles: prev.module_tiles,
        },
        lastLoadedAt: Date.now(),
      });
    }
  } catch {
    await ensureBusinessBootstrap(false, wsId);
  }
}

/** Bootstrap only after manage/setup — soft by default (force reserved for recovery). */
export async function refreshBusinessSessionInventory(
  force = false,
): Promise<void> {
  if (force) {
    await ensureBusinessBootstrap(true);
    return;
  }
  await softRefreshBusinessSession();
}

export function patchBusinessWorkspaceInStore(
  workspace: BusinessWorkspaceSummary,
): void {
  const prev = snapshot.bootstrap;
  if (!prev) {
    setSnapshot({
      selectedWorkspaceId: workspace.id,
      bootstrap: {
        moments_home: { is_empty: true, active_moment_count: 0, cards: [] },
        moments: [],
        selected_workspace: workspace,
        workspaces: [workspace],
        module_tiles: [],
        dashboard: {
          open_moments: 0,
          pending_approvals: 0,
          member_count: 1,
        },
      },
      lastLoadedAt: Date.now(),
    });
    return;
  }
  const workspaces = (prev.workspaces ?? []).map((w) =>
    w.id === workspace.id ? { ...w, ...workspace } : w,
  );
  const has = workspaces.some((w) => w.id === workspace.id);
  setSnapshot({
    bootstrap: {
      ...prev,
      selected_workspace:
        prev.selected_workspace?.id === workspace.id
          ? { ...prev.selected_workspace, ...workspace }
          : prev.selected_workspace,
      workspaces: has ? workspaces : [...workspaces, workspace],
    },
  });
}

export function patchBusinessMomentInInventory(
  moment: BusinessMomentResponse,
): void {
  const prev = snapshot.bootstrap;
  if (!prev) return;
  const moments = [...(prev.moments ?? [])];
  const idx = moments.findIndex((m) => m.moment_id === moment.moment_id);
  if (idx >= 0) moments[idx] = { ...moments[idx], ...moment };
  else moments.unshift(moment);
  const activeCount = moments.filter((m) =>
    isActiveBusinessMomentStatus(m.status ?? ""),
  ).length;
  setSnapshot({
    bootstrap: {
      ...prev,
      moments,
      moments_home: prev.moments_home
        ? {
            ...prev.moments_home,
            is_empty: activeCount === 0,
            active_moment_count: activeCount,
          }
        : prev.moments_home,
      dashboard: prev.dashboard
        ? { ...prev.dashboard, open_moments: moments.length }
        : prev.dashboard,
    },
    lastLoadedAt: Date.now(),
  });
}

export async function ensureBusinessCreateOptions(
  force = false,
): Promise<BusinessCreateOptionsResponse | null> {
  const fresh =
    !force &&
    snapshot.createOptions != null &&
    snapshot.createOptionsLastLoadedAt != null &&
    Date.now() - snapshot.createOptionsLastLoadedAt < CREATE_OPTIONS_FRESH_MS;
  if (fresh) return snapshot.createOptions;

  const gen = snapshot.generation;
  setSnapshot({ createOptionsLoading: true });
  const t0 = performance.now();
  try {
    const options = await dedupeFetch("business:create_options", () =>
      BusinessRepository.getCreateOptions(),
    );
    if (gen !== snapshot.generation) {
      // Still cache catalog; selection is authoritative elsewhere.
    }
    setSnapshot({
      createOptions: options,
      createOptionsLastLoadedAt: Date.now(),
    });
    logBusinessLoad({
      tab: "create",
      requestKey: "create_options",
      reason: force ? "force" : "lazy_create",
      cacheSource: "network",
      durationMs: Math.round(performance.now() - t0),
      generation: snapshot.generation,
      success: true,
    });
    return options;
  } catch (err) {
    logBusinessLoad({
      tab: "create",
      requestKey: "create_options",
      reason: force ? "force" : "lazy_create",
      cacheSource: "network",
      durationMs: Math.round(performance.now() - t0),
      generation: snapshot.generation,
      success: false,
      errorCode: "create_options_failed",
    });
    return snapshot.createOptions;
  } finally {
    setSnapshot({ createOptionsLoading: false });
  }
}

export function clearBusinessSessionStore(): void {
  snapshot = {
    bootstrap: null,
    createOptions: null,
    selectedMomentId: null,
    selectedMomentType: "",
    selectedWorkspaceId: null,
    loading: false,
    createOptionsLoading: false,
    error: null,
    lastLoadedAt: null,
    createOptionsLastLoadedAt: null,
    generation: snapshot.generation + 1,
  };
  notify();
}

/**
 * Selected moment is deleted / archived / membership revoked (403).
 * Remove from local inventory, clear selection, pick replacement or empty, refresh once.
 */
export async function handleBusinessMomentInaccessible(
  momentId: string,
  reason = "access_denied",
): Promise<{
  selectedMomentId: string | null;
  selectedMomentType: string;
}> {
  const {
    markBusinessMomentReseated,
    wasBusinessMomentReseated,
    clearBusinessMomentReseatMarks,
    areAllBusinessMomentsReseated: allMomentsReseated,
  } = await import("@/lib/business/businessMomentAccess");

  if (!momentId) {
    const snap = getBusinessSessionSnapshot();
    return {
      selectedMomentId: snap.selectedMomentId,
      selectedMomentType: snap.selectedMomentType,
    };
  }

  const inventoryEmptyNow = isBusinessInventoryEmpty(snapshot.bootstrap);

  if (wasBusinessMomentReseated(momentId)) {
    // Ghost selection: prior reseat early-returned without clearing — force clear.
    if (snapshot.selectedMomentId === momentId || inventoryEmptyNow) {
      const remaining = (snapshot.bootstrap?.moments ?? []).filter(
        (m) => m.moment_id !== momentId,
      );
      const forceEmpty =
        remaining.length === 0 || allMomentsReseated(remaining);
      if (forceEmpty) {
        clearBusinessMomentReseatMarks();
        applyEmptyBusinessSession(snapshot.selectedMomentType);
      } else {
        const remainingActive = remaining.filter((m) =>
          isActiveBusinessMomentStatus(m.status ?? ""),
        ).length;
        const empty = remaining.length === 0 || remainingActive === 0;
        bumpBusinessSessionGeneration();
        setSnapshot({
          selectedMomentId: null,
          selectedMomentType: snapshot.selectedMomentType,
          bootstrap: snapshot.bootstrap
            ? {
                ...snapshot.bootstrap,
                moments: remaining,
                moments_home: snapshot.bootstrap.moments_home
                  ? {
                      ...snapshot.bootstrap.moments_home,
                      is_empty: empty,
                      active_moment_count: remainingActive,
                      cards: (snapshot.bootstrap.moments_home.cards ?? []).filter(
                        (c) => c.linked_moment_id !== momentId,
                      ),
                    }
                  : snapshot.bootstrap.moments_home,
              }
            : null,
        });
      }
      try {
        const { invalidateBusinessActiveCaches } = await import(
          "@/hooks/useBusinessActiveTabs"
        );
        invalidateBusinessActiveCaches(momentId);
      } catch {
        /* ignore */
      }
    }
    const snap = getBusinessSessionSnapshot();
    return {
      selectedMomentId: snap.selectedMomentId,
      selectedMomentType: snap.selectedMomentType,
    };
  }
  markBusinessMomentReseated(momentId);

  const bootstrap = snapshot.bootstrap;
  const filteredMoments = (bootstrap?.moments ?? []).filter(
    (m) => m.moment_id !== momentId,
  );
  const filteredCards = (bootstrap?.moments_home?.cards ?? []).filter(
    (c) => c.linked_moment_id !== momentId,
  );
  const effectiveEmpty =
    filteredMoments.length === 0 || allMomentsReseated(filteredMoments);

  if (effectiveEmpty) {
    clearBusinessMomentReseatMarks();
    applyEmptyBusinessSession(snapshot.selectedMomentType);
    try {
      const { invalidateBusinessActiveCaches } = await import(
        "@/hooks/useBusinessActiveTabs"
      );
      invalidateBusinessActiveCaches(momentId);
    } catch {
      /* ignore */
    }
    logBusinessLoad({
      tab: "session",
      requestKey: "moment_inaccessible",
      reason,
      cacheSource: "network",
      durationMs: 0,
      generation: snapshot.generation,
      success: true,
      momentId,
      momentType: snapshot.selectedMomentType,
    });
    const snap = getBusinessSessionSnapshot();
    return {
      selectedMomentId: snap.selectedMomentId,
      selectedMomentType: snap.selectedMomentType,
    };
  }

  const reseated = getBusinessMomentReseatedIds();
  const accessibleMoments = filteredMoments.filter(
    (m) => !reseated.has(m.moment_id),
  );
  if (accessibleMoments.length === 0) {
    clearBusinessMomentReseatMarks();
    applyEmptyBusinessSession(snapshot.selectedMomentType);
    try {
      const { invalidateBusinessActiveCaches } = await import(
        "@/hooks/useBusinessActiveTabs"
      );
      invalidateBusinessActiveCaches(momentId);
    } catch {
      /* ignore */
    }
    logBusinessLoad({
      tab: "session",
      requestKey: "moment_inaccessible",
      reason,
      cacheSource: "network",
      durationMs: 0,
      generation: snapshot.generation,
      success: true,
      momentId,
      momentType: snapshot.selectedMomentType,
    });
    const snap = getBusinessSessionSnapshot();
    return {
      selectedMomentId: snap.selectedMomentId,
      selectedMomentType: snap.selectedMomentType,
    };
  }

  const activeCount = filteredMoments.filter((m) =>
    isActiveBusinessMomentStatus(m.status ?? ""),
  ).length;
  const emptyAfterFilter = filteredMoments.length === 0 || activeCount === 0;

  const nextBootstrap: BusinessSessionBootstrapResponse | null = bootstrap
    ? {
        ...bootstrap,
        moments: filteredMoments,
        moments_home: bootstrap.moments_home
          ? {
              ...bootstrap.moments_home,
              cards: filteredCards,
              active_moment_count: activeCount,
              is_empty: emptyAfterFilter,
            }
          : bootstrap.moments_home,
      }
    : null;

  const next = emptyAfterFilter
    ? { selectedMomentId: null as string | null, selectedMomentType: snapshot.selectedMomentType }
    : validateBusinessSelection(
        accessibleMoments,
        snapshot.selectedMomentId === momentId ? null : snapshot.selectedMomentId,
        snapshot.selectedMomentType,
      );

  bumpBusinessSessionGeneration();
  setSnapshot({
    bootstrap: nextBootstrap,
    selectedMomentId: next.selectedMomentId,
    selectedMomentType: next.selectedMomentType,
  });

  try {
    const { invalidateBusinessActiveCaches } = await import(
      "@/hooks/useBusinessActiveTabs"
    );
    invalidateBusinessActiveCaches(momentId);
  } catch {
    // ignore circular import timing
  }

  logBusinessLoad({
    tab: "session",
    requestKey: "moment_inaccessible",
    reason,
    cacheSource: "network",
    durationMs: 0,
    generation: snapshot.generation,
    success: true,
    momentId,
    momentType: snapshot.selectedMomentType,
  });

  // One forced inventory refresh — applyInventorySelection excludes reseated ids.
  await ensureBusinessBootstrap(true);

  const snap = getBusinessSessionSnapshot();
  return {
    selectedMomentId: snap.selectedMomentId,
    selectedMomentType: snap.selectedMomentType,
  };
}

/** Test helper */
export function resetBusinessSessionStoreForTests(): void {
  clearBusinessSessionStore();
  clearBusinessMomentReseatMarks();
}

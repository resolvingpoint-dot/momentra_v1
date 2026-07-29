/**
 * Authoritative Group session store.
 *
 * Owns: moments inventory, selectedMomentId/Type, load state, lastLoadedAt.
 * Home shells must not keep a parallel session bootstrap copy.
 */
import { useSyncExternalStore } from "react";
import { dedupeFetch } from "@/lib/cache/cacheStore";
import type {
  GroupInventoryResponse,
  GroupSessionMomentItem,
  GroupSessionResponse,
  SessionBootstrapResponse,
} from "@/lib/api/group";
import {
  reconcileSelectedGroupMomentType,
  resolveGroupMomentSwitcherOptions,
  switcherOptionForType,
} from "@/components/group/shared/groupMomentRouting";
import {
  getSelectedGroupMomentTypeCode,
  isGroupMomentTypeCode,
  setSelectedGroupMomentTypeCode,
  type GroupMomentTypeCode,
} from "@/lib/group/groupMomentSession";
import { GroupRepository } from "@/repositories/GroupRepository";
import { SetupRepository } from "@/repositories/SetupRepository";
import { patchGroupModuleStateInBootstrap } from "@/stores/bootstrapStore";

const BOOTSTRAP_FRESH_MS = 60_000;

export type GroupSessionSnapshot = {
  session: SessionBootstrapResponse | null;
  selectedMomentId: string | null;
  selectedMomentType: GroupMomentTypeCode;
  loading: boolean;
  error: string | null;
  lastLoadedAt: number | null;
  generation: number;
};

let snapshot: GroupSessionSnapshot = {
  session: null,
  selectedMomentId: null,
  selectedMomentType: "SHARED_EXPERIENCE",
  loading: false,
  error: null,
  lastLoadedAt: null,
  generation: 0,
};

const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((fn) => fn());
}

function setSnapshot(patch: Partial<GroupSessionSnapshot>) {
  snapshot = { ...snapshot, ...patch };
  notify();
}

export function getGroupSessionSnapshot(): GroupSessionSnapshot {
  return snapshot;
}

export function subscribeGroupSession(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useGroupSessionStore(): GroupSessionSnapshot {
  return useSyncExternalStore(
    subscribeGroupSession,
    getGroupSessionSnapshot,
    getGroupSessionSnapshot,
  );
}

export function bumpGroupSessionGeneration(): number {
  const next = snapshot.generation + 1;
  setSnapshot({ generation: next });
  return next;
}

function mergeInventoryIntoSession(
  prev: SessionBootstrapResponse | null,
  inventory: GroupInventoryResponse,
  sessionFields?: GroupSessionResponse | null,
): SessionBootstrapResponse {
  const base = prev ?? {
    is_empty: true,
    active_moment_count: 0,
    active_moment_id: null,
    moment_type: null,
    moment_profile: null,
    setup_step: "",
    create_options: [],
    pulse_data: null,
    moments_data: null,
    memory_data: null,
  };
  return {
    ...base,
    ...(sessionFields ?? {}),
    pulse: inventory.pulse,
    moments: inventory.moments,
    live_overview: inventory.live_overview,
    is_empty: sessionFields?.is_empty ?? base.is_empty,
    active_moment_count:
      sessionFields?.active_moment_count ?? base.active_moment_count,
    active_moment_id:
      sessionFields?.active_moment_id ?? base.active_moment_id,
    focus_moment_id:
      sessionFields?.focus_moment_id ?? base.focus_moment_id,
    moment_type: sessionFields?.moment_type ?? base.moment_type,
    draft_moment_id: sessionFields?.draft_moment_id ?? base.draft_moment_id,
    draft_moment_type:
      sessionFields?.draft_moment_type ?? base.draft_moment_type,
    has_draft: sessionFields?.has_draft ?? base.has_draft,
    linked_moment_status:
      sessionFields?.linked_moment_status ?? base.linked_moment_status,
  };
}

function applyInventorySelection(session: SessionBootstrapResponse): void {
  const options = resolveGroupMomentSwitcherOptions(session);
  const currentType = getSelectedGroupMomentTypeCode();
  const reconciled = reconcileSelectedGroupMomentType(options, currentType);
  if (reconciled !== currentType) {
    setSelectedGroupMomentTypeCode(reconciled);
  }

  const selectedOption = switcherOptionForType(options, reconciled);
  const selectedMomentId = selectedOption?.momentId ?? null;
  const selectedMomentType = selectedOption?.typeCode ?? reconciled;

  if (selectedOption) {
    SetupRepository.rememberGroupMoment(
      selectedOption.momentId,
      selectedOption.typeCode,
    );
  }

  setSnapshot({
    session,
    selectedMomentId,
    selectedMomentType,
    lastLoadedAt: Date.now(),
    error: null,
  });
}

export function setGroupSelection(
  typeCode: GroupMomentTypeCode,
  momentId: string | null,
): void {
  bumpGroupSessionGeneration();
  setSelectedGroupMomentTypeCode(typeCode);
  if (momentId) {
    SetupRepository.rememberGroupMoment(momentId, typeCode);
  }
  setSnapshot({
    selectedMomentType: typeCode,
    selectedMomentId: momentId,
  });
}

export async function ensureGroupSession(
  force = false,
): Promise<SessionBootstrapResponse | null> {
  const fresh =
    !force &&
    snapshot.session != null &&
    snapshot.lastLoadedAt != null &&
    Date.now() - snapshot.lastLoadedAt < BOOTSTRAP_FRESH_MS &&
    snapshot.error == null;
  if (fresh) return snapshot.session;

  setSnapshot({ loading: true, error: null });
  try {
    const session = await dedupeFetch("group:session_bootstrap", () =>
      GroupRepository.getSessionBootstrap(),
    );
    applyInventorySelection(session);
    setSnapshot({ loading: false });
    return snapshot.session;
  } catch (e) {
    const message = e instanceof Error ? e.message : "Failed to load Group";
    setSnapshot({ loading: false, error: message });
    return null;
  }
}

/**
 * Soft background refresh: inventory (+ session if counts may have drifted).
 * Falls back to composer bootstrap on error.
 */
export async function softRefreshGroupSession(): Promise<void> {
  const gen = snapshot.generation;
  try {
    const [inventory, sessionFields] = await Promise.all([
      GroupRepository.getInventory(),
      GroupRepository.getSession(),
    ]);
    if (gen !== snapshot.generation) return;
    const merged = mergeInventoryIntoSession(
      snapshot.session,
      inventory,
      sessionFields,
    );
    applyInventorySelection(merged);
  } catch {
    await ensureGroupSession(false);
  }
}

export async function refreshGroupSessionInventory(
  force = false,
): Promise<void> {
  if (force) {
    await ensureGroupSession(true);
    return;
  }
  await softRefreshGroupSession();
}

export function patchGroupMomentInInventory(
  momentId: string,
  patch: Partial<GroupSessionMomentItem> & {
    moment_type?: string | null;
    lifecycle_status?: string | null;
    name?: string;
  },
): void {
  const prev = snapshot.session;
  if (!prev) return;
  const moments = [...(prev.moments ?? [])];
  const idx = moments.findIndex((m) => m.id === momentId);
  const item: GroupSessionMomentItem = {
    id: momentId,
    name: patch.name,
    moment_type: patch.moment_type,
    lifecycle_status: patch.lifecycle_status,
    ...(idx >= 0 ? moments[idx] : {}),
    ...patch,
  };
  if (idx >= 0) moments[idx] = item;
  else moments.unshift(item);

  const activeCount = moments.filter((m) => {
    const s = (m.lifecycle_status ?? "").trim().toUpperCase();
    return s === "ACTIVE" || s === "PAUSED" || s === "LIVE" || !s;
  }).length;

  const next: SessionBootstrapResponse = {
    ...prev,
    moments,
    active_moment_count: activeCount,
    is_empty: activeCount === 0 && !prev.has_draft,
    live_overview: prev.live_overview
      ? {
          ...prev.live_overview,
          live_cards: moments.filter((m) => {
            const s = (m.lifecycle_status ?? "").trim().toUpperCase();
            return s === "ACTIVE" || s === "LIVE" || !s;
          }),
        }
      : prev.live_overview,
  };
  applyInventorySelection(next);
}

export function patchGroupDraftInStore(
  momentId: string,
  momentType: GroupMomentTypeCode,
  name?: string,
): void {
  const prev = snapshot.session;
  const draftItem: GroupSessionMomentItem = {
    id: momentId,
    moment_type: momentType,
    lifecycle_status: "DRAFT",
    name,
  };
  if (!prev) {
    const session: SessionBootstrapResponse = {
      is_empty: true,
      active_moment_count: 0,
      active_moment_id: null,
      moment_type: momentType,
      moment_profile: null,
      setup_step: "",
      create_options: [],
      pulse_data: null,
      moments_data: null,
      memory_data: null,
      has_draft: true,
      draft_moment_id: momentId,
      draft_moment_type: momentType,
      moments: [draftItem],
    };
    applyInventorySelection(session);
    patchGroupModuleStateInBootstrap({ group: "SETUP", pulse: "SETUP", moments: "SETUP" });
    return;
  }
  patchGroupMomentInInventory(momentId, draftItem);
  setSnapshot({
    session: {
      ...snapshot.session!,
      has_draft: true,
      draft_moment_id: momentId,
      draft_moment_type: momentType,
    },
  });
  patchGroupModuleStateInBootstrap({ group: "SETUP", pulse: "SETUP", moments: "SETUP" });
}

export function patchGroupMomentActivated(
  momentId: string,
  momentType: GroupMomentTypeCode,
  momentName?: string,
): void {
  patchGroupMomentInInventory(momentId, {
    moment_type: momentType,
    lifecycle_status: "ACTIVE",
    name: momentName,
  });
  patchGroupModuleStateInBootstrap({ group: "ACTIVE", pulse: "ACTIVE", moments: "ACTIVE" });
  setGroupSelection(momentType, momentId);
}

export function applyGroupLifecyclePatch(
  momentId: string,
  status: string,
  replacementMomentId: string | null,
  replacementMomentTypeCode: string | null,
): void {
  patchGroupMomentInInventory(momentId, { lifecycle_status: status });
  if (replacementMomentId && isGroupMomentTypeCode(replacementMomentTypeCode)) {
    setGroupSelection(replacementMomentTypeCode, replacementMomentId);
  } else if (!replacementMomentId) {
    bumpGroupSessionGeneration();
    setSnapshot({
      selectedMomentId: null,
    });
    const activeLeft = (snapshot.session?.moments ?? []).some((m) => {
      const s = (m.lifecycle_status ?? "").trim().toUpperCase();
      return m.id !== momentId && (s === "ACTIVE" || s === "PAUSED" || s === "LIVE");
    });
    if (!activeLeft) {
      patchGroupModuleStateInBootstrap({ group: "SETUP", pulse: "SETUP", moments: "SETUP" });
    }
  } else {
    bumpGroupSessionGeneration();
  }
}

export function clearGroupSessionStore(): void {
  snapshot = {
    session: null,
    selectedMomentId: null,
    selectedMomentType: "SHARED_EXPERIENCE",
    loading: false,
    error: null,
    lastLoadedAt: null,
    generation: snapshot.generation + 1,
  };
  notify();
}

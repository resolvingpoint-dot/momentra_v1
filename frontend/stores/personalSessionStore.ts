import {
  dedupeFetch,
  diskCacheLoad,
  diskCacheRemove,
  diskCacheSave,
} from "@/lib/cache/cacheStore";
import {
  getPersonalCreateOptions,
  getPersonalInventory,
  getPersonalSession,
  getPersonalSessionBootstrap,
} from "@/lib/api/client";
import type {
  PersonalCreateOptionCard,
  PersonalCreateOptionsResponse,
  PersonalMemoryResponse,
  PersonalMomentsHomeResponse,
  PersonalPulseResponse,
  PersonalLifeResponse,
  TemplateMemoryResponse,
  TemplateMomentsResponse,
} from "@/lib/api/personal";
import type { PersonalSessionBootstrapResponse } from "@/lib/api/client";
import {
  getSelectedMomentTypeCode,
  setSelectedMomentTypeCode,
  type PersonalMomentTypeCode,
} from "@/lib/personal/personalMomentSession";
import { FRESH_TTL_MS, STALE_TTL_MS } from "@/lib/cache/personalCacheTtl";
import {
  memoryHasTypePayload,
  momentsHasTypePayload,
  pulseHasTypePayload,
} from "@/components/personal/shared/personalMomentRouting";
import {
  parsePersonalMemoryResponse,
  parsePersonalMomentsHomeResponse,
  parsePersonalPulseResponse,
  parseTemplateMemoryResponse,
  parseTemplateMomentsResponse,
  parseTemplatePulseResponse,
} from "@/lib/personal/personalApiMappers";
import { useSyncExternalStore } from "react";
import { patchMyMoneyModuleStateInBootstrap } from "@/stores/bootstrapStore";

export { FRESH_TTL_MS, STALE_TTL_MS };

const LIFE_DISK_KEY = "personal_life:v1";
const BOOTSTRAP_FRESH_MS = 180_000;
const CREATE_OPTIONS_FRESH_MS = 60_000;

// --------------------------------------------------------------------------- #
// Authoritative session snapshot
// --------------------------------------------------------------------------- #
export type PersonalSessionSnapshot = {
  session: PersonalSessionBootstrapResponse | null;
  createOptions: PersonalCreateOptionsResponse | null;
  selectedMomentType: PersonalMomentTypeCode;
  loading: boolean;
  createOptionsLoading: boolean;
  error: string | null;
  lastLoadedAt: number | null;
  createOptionsLastLoadedAt: number | null;
  generation: number;
};

let snapshot: PersonalSessionSnapshot = {
  session: null,
  createOptions: null,
  selectedMomentType: "LIFE_OPERATIONS",
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

function setSnapshot(patch: Partial<PersonalSessionSnapshot>) {
  snapshot = { ...snapshot, ...patch };
  notify();
}

export function getPersonalSessionSnapshot(): PersonalSessionSnapshot {
  return snapshot;
}

export function subscribePersonalSession(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function usePersonalSessionStore(): PersonalSessionSnapshot {
  return useSyncExternalStore(
    subscribePersonalSession,
    getPersonalSessionSnapshot,
    getPersonalSessionSnapshot,
  );
}

export function bumpPersonalSessionGeneration(): number {
  const next = snapshot.generation + 1;
  setSnapshot({ generation: next });
  return next;
}

export function setPersonalMomentType(typeCode: PersonalMomentTypeCode): void {
  bumpPersonalSessionGeneration();
  setSelectedMomentTypeCode(typeCode);
  setSnapshot({ selectedMomentType: typeCode });
}

function applySession(
  session: PersonalSessionBootstrapResponse,
  code?: PersonalMomentTypeCode,
): void {
  const typeCode = code ?? getSelectedMomentTypeCode();
  persistPulse(typeCode, parsePersonalPulseResponse(session.pulse));
  persistMoments(typeCode, parsePersonalMomentsHomeResponse(session.moments_home));
  setSnapshot({
    session,
    selectedMomentType: typeCode,
    lastLoadedAt: Date.now(),
    error: null,
  });
  void Promise.all([
    import("@/hooks/usePersonalPulse"),
    import("@/hooks/usePersonalMoments"),
  ]).then(([pulseMod, momentsMod]) => {
    pulseMod.seedPersonalPulseCache(typeCode, parsePersonalPulseResponse(session.pulse));
    momentsMod.seedPersonalMomentsCache(
      typeCode,
      parsePersonalMomentsHomeResponse(session.moments_home),
    );
  });
}

/** Shell entry — prefer thin session + inventory; fall back to bootstrap. */
export async function ensurePersonalSession(
  force = false,
): Promise<PersonalSessionBootstrapResponse | null> {
  const code = getSelectedMomentTypeCode();
  const fresh =
    !force &&
    snapshot.session != null &&
    snapshot.lastLoadedAt != null &&
    Date.now() - snapshot.lastLoadedAt < BOOTSTRAP_FRESH_MS &&
    snapshot.error == null;
  if (fresh) return snapshot.session;

  setSnapshot({ loading: true, error: null, selectedMomentType: code });
  try {
    const session = await dedupeFetch(`personal:session_chrome:${code}`, async () => {
      try {
        const [inventory] = await Promise.all([
          getPersonalInventory({ momentTypeCode: code }),
          getPersonalSession().catch(() => null),
        ]);
        return {
          pulse: inventory.pulse,
          moments_home: inventory.moments_home,
        } satisfies PersonalSessionBootstrapResponse;
      } catch {
        return getPersonalSessionBootstrap({ momentTypeCode: code, forceRefresh: force });
      }
    });
    applySession(session, code);
    setSnapshot({ loading: false });
    return snapshot.session;
  } catch (e) {
    const message = e instanceof Error ? e.message : "Failed to load My Money";
    setSnapshot({ loading: false, error: message });
    return null;
  }
}

/** Soft background refresh via split inventory + session endpoints. */
export async function softRefreshPersonalSession(): Promise<void> {
  const gen = snapshot.generation;
  const code = getSelectedMomentTypeCode();
  try {
    const [inventory] = await Promise.all([
      getPersonalInventory({ momentTypeCode: code }),
      getPersonalSession().catch(() => null),
    ]);
    if (gen !== snapshot.generation) return;
    applySession(
      { pulse: inventory.pulse, moments_home: inventory.moments_home },
      code,
    );
  } catch {
    await ensurePersonalSession(false);
  }
}

export async function refreshPersonalSessionInventory(force = false): Promise<void> {
  if (force) {
    await ensurePersonalSession(true);
    return;
  }
  await softRefreshPersonalSession();
}

export async function ensurePersonalCreateOptions(
  force = false,
): Promise<PersonalCreateOptionsResponse | null> {
  const fresh =
    !force &&
    snapshot.createOptions != null &&
    snapshot.createOptionsLastLoadedAt != null &&
    Date.now() - snapshot.createOptionsLastLoadedAt < CREATE_OPTIONS_FRESH_MS;
  if (fresh) return snapshot.createOptions;

  setSnapshot({ createOptionsLoading: true });
  try {
    const options = force
      ? await getPersonalCreateOptions()
      : await dedupeFetch("personal:create_options", () => getPersonalCreateOptions());
    setSnapshot({
      createOptions: options,
      createOptionsLastLoadedAt: Date.now(),
      createOptionsLoading: false,
    });
    return options;
  } catch {
    setSnapshot({ createOptionsLoading: false });
    return snapshot.createOptions;
  }
}

export function patchPersonalCreateOptionsCard(
  typeCode: PersonalMomentTypeCode,
  patch: Partial<PersonalCreateOptionCard>,
): void {
  const prev = snapshot.createOptions;
  if (!prev?.cards) return;
  const cards = prev.cards.map((c) =>
    c.moment_type_code === typeCode ? { ...c, ...patch } : c,
  );
  setSnapshot({ createOptions: { ...prev, cards } });
}

export function patchPersonalMomentInInventory(
  typeCode: PersonalMomentTypeCode,
  patch: {
    linked_moment_id?: string | null;
    linked_moment_status?: string | null;
    moment_name?: string | null;
    is_active?: boolean;
  },
): void {
  const prev = snapshot.session;
  if (!prev?.moments_home?.cards) {
    patchPersonalCreateOptionsCard(typeCode, {
      linked_moment_id: patch.linked_moment_id,
      linked_moment_status: patch.linked_moment_status,
      has_draft: patch.linked_moment_status === "DRAFT",
    });
    return;
  }
  const cards = prev.moments_home.cards.map((c) =>
    c.moment_type_code === typeCode
      ? {
          ...c,
          linked_moment_id:
            patch.linked_moment_id !== undefined
              ? patch.linked_moment_id
              : c.linked_moment_id,
          linked_moment_status:
            patch.linked_moment_status !== undefined
              ? patch.linked_moment_status
              : c.linked_moment_status,
          moment_name:
            patch.moment_name !== undefined ? patch.moment_name : c.moment_name,
          is_active:
            patch.is_active !== undefined
              ? patch.is_active
              : patch.linked_moment_status
                ? ["ACTIVE", "PAUSED", "COMPLETED"].includes(
                    patch.linked_moment_status,
                  )
                : c.is_active,
        }
      : c,
  );
  const activeCount = cards.filter((c) => c.is_active).length;
  setSnapshot({
    session: {
      ...prev,
      moments_home: {
        ...prev.moments_home,
        cards,
        active_moment_count: activeCount,
        is_empty: activeCount === 0,
      },
      pulse: {
        ...prev.pulse,
        active_moment_count: activeCount,
        is_empty: activeCount === 0,
      },
    },
    lastLoadedAt: Date.now(),
  });
  patchPersonalCreateOptionsCard(typeCode, {
    linked_moment_id: patch.linked_moment_id,
    linked_moment_status: patch.linked_moment_status,
    has_draft: patch.linked_moment_status === "DRAFT",
  });
}

export function patchPersonalMomentActivated(
  typeCode: PersonalMomentTypeCode,
  momentId: string,
  momentName?: string,
): void {
  bumpPersonalSessionGeneration();
  setSelectedMomentTypeCode(typeCode);
  patchPersonalMomentInInventory(typeCode, {
    linked_moment_id: momentId,
    linked_moment_status: "ACTIVE",
    moment_name: momentName ?? null,
    is_active: true,
  });
  setSnapshot({ selectedMomentType: typeCode });
  patchMyMoneyModuleStateInBootstrap({
    myMoney: "ACTIVE",
    pulse: "ACTIVE",
    moments: "ACTIVE",
    memory: "ACTIVE",
  });
}

export function patchPersonalDraftCreated(
  typeCode: PersonalMomentTypeCode,
  momentId: string,
): void {
  patchPersonalMomentInInventory(typeCode, {
    linked_moment_id: momentId,
    linked_moment_status: "DRAFT",
    is_active: false,
  });
  patchMyMoneyModuleStateInBootstrap({
    myMoney: "SETUP",
    pulse: "SETUP",
    moments: "SETUP",
  });
}

export function clearPersonalSessionStore(): void {
  snapshot = {
    session: null,
    createOptions: null,
    selectedMomentType: "LIFE_OPERATIONS",
    loading: false,
    createOptionsLoading: false,
    error: null,
    lastLoadedAt: null,
    createOptionsLastLoadedAt: null,
    generation: snapshot.generation + 1,
  };
  notify();
}

// --------------------------------------------------------------------------- #
// Disk / cache helpers (unchanged contract)
// --------------------------------------------------------------------------- #
function typeSlug(code: PersonalMomentTypeCode): string {
  return code.toLowerCase();
}

export function pulseDiskKey(code: PersonalMomentTypeCode): string {
  return `personal_pulse:${typeSlug(code)}`;
}

export function momentsDiskKey(code: PersonalMomentTypeCode): string {
  return `personal_moments:${typeSlug(code)}`;
}

export function memoryDiskKey(code: PersonalMomentTypeCode): string {
  return `personal_memory:${typeSlug(code)}:v2`;
}

export function templateMomentsDiskKey(code: PersonalMomentTypeCode): string {
  return `personal_template_moments:${typeSlug(code)}`;
}

export function templateMemoryDiskKey(code: PersonalMomentTypeCode): string {
  return `personal_template_memory:${typeSlug(code)}`;
}

export function templatePulseDiskKey(code: PersonalMomentTypeCode): string {
  return `personal_template_pulse:${typeSlug(code)}`;
}

export function loadPulseFromDisk(code: PersonalMomentTypeCode): PersonalPulseResponse | null {
  const raw = diskCacheLoad<unknown>(pulseDiskKey(code), STALE_TTL_MS);
  return raw ? parsePersonalPulseResponse(raw) : null;
}

export function loadMomentsFromDisk(
  code: PersonalMomentTypeCode,
): PersonalMomentsHomeResponse | null {
  const raw = diskCacheLoad<unknown>(momentsDiskKey(code), STALE_TTL_MS);
  return raw ? parsePersonalMomentsHomeResponse(raw) : null;
}

export function loadMemoryFromDisk(code: PersonalMomentTypeCode): PersonalMemoryResponse | null {
  const raw = diskCacheLoad<unknown>(memoryDiskKey(code), STALE_TTL_MS);
  return raw ? parsePersonalMemoryResponse(raw) : null;
}

export function loadLifeFromDisk(): PersonalLifeResponse | null {
  return diskCacheLoad<PersonalLifeResponse>(LIFE_DISK_KEY, STALE_TTL_MS);
}

export function loadTemplateMomentsFromDisk(
  code: PersonalMomentTypeCode,
): TemplateMomentsResponse | null {
  const raw = diskCacheLoad<unknown>(templateMomentsDiskKey(code), STALE_TTL_MS);
  return raw ? parseTemplateMomentsResponse(raw) : null;
}

export function loadTemplateMemoryFromDisk(
  code: PersonalMomentTypeCode,
): TemplateMemoryResponse | null {
  const raw = diskCacheLoad<unknown>(templateMemoryDiskKey(code), STALE_TTL_MS);
  return raw ? parseTemplateMemoryResponse(raw) : null;
}

export function loadTemplatePulseFromDisk(
  code: PersonalMomentTypeCode,
): Record<string, unknown> | null {
  const raw = diskCacheLoad<unknown>(templatePulseDiskKey(code), STALE_TTL_MS);
  return raw ? parseTemplatePulseResponse(raw) : null;
}

export function persistPulse(code: PersonalMomentTypeCode, data: PersonalPulseResponse): void {
  diskCacheSave(pulseDiskKey(code), data);
}

export function persistMoments(
  code: PersonalMomentTypeCode,
  data: PersonalMomentsHomeResponse,
): void {
  diskCacheSave(momentsDiskKey(code), data);
}

export function persistMemory(code: PersonalMomentTypeCode, data: PersonalMemoryResponse): void {
  diskCacheSave(memoryDiskKey(code), data);
}

export function persistLife(data: PersonalLifeResponse): void {
  diskCacheSave(LIFE_DISK_KEY, data);
}

export function persistTemplateMoments(
  code: PersonalMomentTypeCode,
  data: TemplateMomentsResponse,
): void {
  diskCacheSave(templateMomentsDiskKey(code), data);
}

export function persistTemplateMemory(
  code: PersonalMomentTypeCode,
  data: TemplateMemoryResponse,
): void {
  diskCacheSave(templateMemoryDiskKey(code), data);
}

export function persistTemplatePulse(
  code: PersonalMomentTypeCode,
  data: Record<string, unknown>,
): void {
  diskCacheSave(templatePulseDiskKey(code), data);
}

export function warmUpPersonalSessionFromDisk(code: PersonalMomentTypeCode): {
  pulse: PersonalPulseResponse | null;
  moments: PersonalMomentsHomeResponse | null;
  memory: PersonalMemoryResponse | null;
  life: PersonalLifeResponse | null;
  templateMoments: TemplateMomentsResponse | null;
  templateMemory: TemplateMemoryResponse | null;
  templatePulse: Record<string, unknown> | null;
} {
  return {
    pulse: loadPulseFromDisk(code),
    moments: loadMomentsFromDisk(code),
    memory: loadMemoryFromDisk(code),
    life: loadLifeFromDisk(),
    templateMoments: loadTemplateMomentsFromDisk(code),
    templateMemory: loadTemplateMemoryFromDisk(code),
    templatePulse: loadTemplatePulseFromDisk(code),
  };
}

export async function ensurePersonalSessionBootstrap(
  code: PersonalMomentTypeCode,
  force = false,
): Promise<{
  pulse: PersonalPulseResponse;
  moments_home: PersonalMomentsHomeResponse;
}> {
  const session = await ensurePersonalSession(force);
  if (session && getSelectedMomentTypeCode() === code) {
    return {
      pulse: parsePersonalPulseResponse(session.pulse),
      moments_home: parsePersonalMomentsHomeResponse(session.moments_home),
    };
  }
  const bootstrap = await dedupeFetch(`personal:session_bootstrap:${code}`, () =>
    getPersonalSessionBootstrap({ momentTypeCode: code, forceRefresh: force }),
  );
  const pulse = parsePersonalPulseResponse(bootstrap.pulse);
  const moments_home = parsePersonalMomentsHomeResponse(bootstrap.moments_home);
  persistPulse(code, pulse);
  persistMoments(code, moments_home);
  const [pulseMod, momentsMod] = await Promise.all([
    import("@/hooks/usePersonalPulse"),
    import("@/hooks/usePersonalMoments"),
  ]);
  pulseMod.seedPersonalPulseCache(code, pulse);
  momentsMod.seedPersonalMomentsCache(code, moments_home);
  if (!snapshot.session) {
    applySession(bootstrap, code);
  }
  return { pulse, moments_home };
}

export async function warmStartPersonalSession(
  code: PersonalMomentTypeCode,
  force = false,
): Promise<void> {
  setSelectedMomentTypeCode(code);
  await ensurePersonalSession(force);
}

export function clearPersonalSessionDisk(code?: PersonalMomentTypeCode): void {
  if (code) {
    diskCacheRemove(pulseDiskKey(code));
    diskCacheRemove(momentsDiskKey(code));
    diskCacheRemove(memoryDiskKey(code));
    diskCacheRemove(templateMomentsDiskKey(code));
    diskCacheRemove(templateMemoryDiskKey(code));
    diskCacheRemove(templatePulseDiskKey(code));
    return;
  }
  diskCacheRemove(LIFE_DISK_KEY);
}

export function clearAllPersonalSessionOnLogout(): void {
  clearPersonalSessionStore();
  void Promise.all([
    import("@/hooks/usePersonalPulse"),
    import("@/hooks/usePersonalMoments"),
    import("@/hooks/usePersonalMemory"),
    import("@/hooks/usePersonalLife"),
    import("@/hooks/useTemplateProjection"),
  ]).then(([pulse, moments, memory, life, template]) => {
    pulse.invalidatePersonalPulseCache();
    moments.invalidatePersonalMomentsCache();
    memory.invalidatePersonalMemoryCache();
    life.invalidatePersonalLifeCache();
    template.invalidateTemplateProjectionCaches();
  });
  const types: PersonalMomentTypeCode[] = [
    "LIFE_OPERATIONS",
    "FUTURE_BUILDING",
    "LIFESTYLE",
    "RELATIONSHIPS",
  ];
  types.forEach((code) => clearPersonalSessionDisk(code));
  clearPersonalSessionDisk();
}

export function hasCachedActiveSessionHint(code: PersonalMomentTypeCode): boolean {
  const pulse = loadPulseFromDisk(code);
  const moments = loadMomentsFromDisk(code);
  const memory = loadMemoryFromDisk(code);
  const templateMoments = loadTemplateMomentsFromDisk(code);
  const templateMemory = loadTemplateMemoryFromDisk(code);
  return (
    Boolean(pulse && pulseHasTypePayload(pulse, code)) ||
    Boolean(moments && momentsHasTypePayload(moments, code)) ||
    Boolean(memory && memoryHasTypePayload(memory, code)) ||
    Boolean(templateMoments?.moment_projection) ||
    Boolean(templateMemory?.memory_projection)
  );
}

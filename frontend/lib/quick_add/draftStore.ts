/** Local draft persistence for Quick Add network-loss recovery. */

const STORAGE_PREFIX = "quick_add_draft:";

export type QuickAddDraft = {
  momentId: string;
  tab: string;
  form: Record<string, unknown>;
  payload: Record<string, unknown>;
  clientRequestId: string;
  savedAt: string;
};

export function draftStorageKey(momentId: string, tab: string): string {
  return `${STORAGE_PREFIX}${momentId}:${tab}`;
}

export function saveQuickAddDraft(draft: QuickAddDraft): void {
  if (typeof localStorage === "undefined") return;
  try {
    localStorage.setItem(draftStorageKey(draft.momentId, draft.tab), JSON.stringify(draft));
  } catch {
    // Quota or private mode — best effort only.
  }
}

export function loadQuickAddDraft(momentId: string, tab: string): QuickAddDraft | null {
  if (typeof localStorage === "undefined") return null;
  try {
    const raw = localStorage.getItem(draftStorageKey(momentId, tab));
    if (!raw) return null;
    return JSON.parse(raw) as QuickAddDraft;
  } catch {
    return null;
  }
}

export function clearQuickAddDraft(momentId: string, tab: string): void {
  if (typeof localStorage === "undefined") return;
  try {
    localStorage.removeItem(draftStorageKey(momentId, tab));
  } catch {
    // ignore
  }
}

export function hasQuickAddDraft(momentId: string, tab: string): boolean {
  return loadQuickAddDraft(momentId, tab) !== null;
}

export function listQuickAddDraftKeys(): string[] {
  if (typeof localStorage === "undefined") return [];
  const keys: string[] = [];
  for (let i = 0; i < localStorage.length; i += 1) {
    const key = localStorage.key(i);
    if (key?.startsWith(STORAGE_PREFIX)) keys.push(key);
  }
  return keys;
}

export function subscribeOnlineRetry(onRetry: () => void): () => void {
  if (typeof window === "undefined") return () => undefined;
  const handler = () => onRetry();
  window.addEventListener("online", handler);
  return () => window.removeEventListener("online", handler);
}

export function isNetworkFailure(err: unknown): boolean {
  if (err instanceof TypeError) return true;
  if (err instanceof Error) {
    const msg = err.message.toLowerCase();
    return (
      msg === "failed to fetch" ||
      msg.includes("network") ||
      msg.includes("load failed") ||
      msg.includes("timed out")
    );
  }
  return false;
}

export function createClientRequestId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `client-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

/** Serialize LifeOps form state (rhythmActions Set → array). */
export function serializeQuickAddForm(form: {
  rhythmActions: Set<string>;
  [key: string]: unknown;
}): Record<string, unknown> {
  return {
    ...form,
    rhythmActions: Array.from(form.rhythmActions),
  };
}

/** Restore LifeOps form state from draft storage. */
export function deserializeQuickAddForm<T extends { rhythmActions: Set<string> }>(
  stored: Record<string, unknown>,
  defaults: T,
): T {
  const rhythm = stored.rhythmActions;
  return {
    ...defaults,
    ...stored,
    rhythmActions: new Set(Array.isArray(rhythm) ? (rhythm as string[]) : []),
  } as T;
}

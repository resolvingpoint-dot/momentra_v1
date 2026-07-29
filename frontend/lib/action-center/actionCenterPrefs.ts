/** Client-only Action Center prefs: favorites, recent, analytics helpers. */

const FAV_PREFIX = "ac:fav:";
const RECENT_PREFIX = "ac:recent:";
const RECENT_CAP = 8;

function readJson<T>(key: string, fallback: T): T {
  if (typeof localStorage === "undefined") return fallback;
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown): void {
  if (typeof localStorage === "undefined") return;
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore quota
  }
}

export function favKey(userId: string, templateId: string) {
  return `${FAV_PREFIX}${userId}:${templateId}`;
}

export function recentKey(userId: string, templateId: string) {
  return `${RECENT_PREFIX}${userId}:${templateId}`;
}

export function getFavoriteActionIds(userId: string, templateId: string): string[] {
  return readJson<string[]>(favKey(userId, templateId), []);
}

export function toggleFavoriteAction(userId: string, templateId: string, actionId: string): string[] {
  const current = getFavoriteActionIds(userId, templateId);
  const next = current.includes(actionId)
    ? current.filter((id) => id !== actionId)
    : [...current, actionId];
  writeJson(favKey(userId, templateId), next);
  return next;
}

export function getRecentActionIds(userId: string, templateId: string): string[] {
  return readJson<string[]>(recentKey(userId, templateId), []);
}

export function pushRecentAction(userId: string, templateId: string, actionId: string): string[] {
  const next = [actionId, ...getRecentActionIds(userId, templateId).filter((id) => id !== actionId)].slice(
    0,
    RECENT_CAP,
  );
  writeJson(recentKey(userId, templateId), next);
  return next;
}

export type ActionAnalyticsEvent =
  | "started"
  | "completed"
  | "abandoned"
  | "draft_restored"
  | "validation_failed";

export type ActionAnalyticsPayload = {
  analytics_id: string;
  event: ActionAnalyticsEvent;
  duration_ms?: number;
  action_id?: string;
  template_id?: string;
};

type Listener = (payload: ActionAnalyticsPayload) => void;
const listeners = new Set<Listener>();

export function subscribeActionAnalytics(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function emitActionAnalytics(payload: ActionAnalyticsPayload): void {
  if (typeof window !== "undefined" && process.env.NODE_ENV !== "production") {
    // eslint-disable-next-line no-console
    console.debug("[ActionCenter]", payload);
  }
  listeners.forEach((l) => l(payload));
}

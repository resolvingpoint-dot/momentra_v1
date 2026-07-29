import { refreshAccessToken } from "@/lib/api/client";
import {
  getAccessToken,
  getExpiresAt,
  hasStoredSession,
} from "@/lib/auth/tokens";

const REFRESH_PADDING_MS = 60_000;
let refreshTimer: ReturnType<typeof setTimeout> | null = null;

export function isAccessTokenNearExpiry(): boolean {
  const expiresAt = getExpiresAt();
  if (expiresAt === null) return true;
  return Date.now() >= expiresAt - REFRESH_PADDING_MS;
}

export function clearProactiveTokenRefresh(): void {
  if (refreshTimer !== null) {
    clearTimeout(refreshTimer);
    refreshTimer = null;
  }
}

export function scheduleProactiveTokenRefresh(): void {
  clearProactiveTokenRefresh();
  // Cookie-based refresh: we only need an access token + expiry in memory.
  if (!hasStoredSession() && !getAccessToken()) return;

  const expiresAt = getExpiresAt();
  if (expiresAt === null) return;

  const delay = Math.max(expiresAt - REFRESH_PADDING_MS - Date.now(), 0);
  refreshTimer = setTimeout(() => {
    void refreshAccessToken()
      .then(() => scheduleProactiveTokenRefresh())
      .catch(() => clearProactiveTokenRefresh());
  }, delay);
}

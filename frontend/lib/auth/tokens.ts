/** In-memory access token + HttpOnly refresh cookie (web). */

import type { UserResponse } from "@/lib/api/types";

const ACCESS_TOKEN_KEY = "momentra_access_token";
const REFRESH_TOKEN_KEY = "momentra_refresh_token";
const EXPIRES_AT_KEY = "momentra_token_expires_at";
/** Non-secret UX hint so splash/restore know to try the refresh cookie. */
const SESSION_HINT_KEY = "momentra_session_hint";
const CACHED_USER_KEY = "momentra_cached_user";

let memoryAccessToken: string | null = null;
let memoryExpiresAt: number | null = null;

function canUseStorage(): boolean {
  return typeof window !== "undefined";
}

export function getAccessToken(): string | null {
  return memoryAccessToken;
}

/** Legacy localStorage refresh (pre-HttpOnly migration). */
export function getLegacyRefreshToken(): string | null {
  if (!canUseStorage()) return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  // Web refresh lives in an HttpOnly cookie on the API host; JS cannot read it.
  // Return legacy value only so one-time migration can POST it once.
  return getLegacyRefreshToken();
}

export function getExpiresAt(): number | null {
  return memoryExpiresAt;
}

export function saveAccessToken(accessToken: string, expiresIn: number): void {
  memoryAccessToken = accessToken;
  memoryExpiresAt = Date.now() + expiresIn * 1000;
  if (canUseStorage()) {
    localStorage.setItem(SESSION_HINT_KEY, "1");
    // Clear any leftover access/refresh from older builds.
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(EXPIRES_AT_KEY);
  }
}

/** @deprecated Prefer saveAccessToken — refresh is cookie-based on web. */
export function saveTokens(
  accessToken: string,
  _refreshToken: string,
  expiresIn: number,
): void {
  saveAccessToken(accessToken, expiresIn);
}

export function clearTokens(): void {
  memoryAccessToken = null;
  memoryExpiresAt = null;
  if (!canUseStorage()) return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(EXPIRES_AT_KEY);
  localStorage.removeItem(SESSION_HINT_KEY);
  localStorage.removeItem(CACHED_USER_KEY);
}

export function hasStoredSession(): boolean {
  if (memoryAccessToken) return true;
  if (!canUseStorage()) return false;
  return (
    localStorage.getItem(SESSION_HINT_KEY) === "1" ||
    localStorage.getItem(REFRESH_TOKEN_KEY) !== null ||
    localStorage.getItem(ACCESS_TOKEN_KEY) !== null
  );
}

export function clearLegacyRefreshToken(): void {
  if (!canUseStorage()) return;
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(EXPIRES_AT_KEY);
}

export function saveCachedUser(user: UserResponse): void {
  if (!canUseStorage()) return;
  try {
    localStorage.setItem(CACHED_USER_KEY, JSON.stringify(user));
  } catch {
    // ignore quota / private mode
  }
}

export function loadCachedUser(): UserResponse | null {
  if (!canUseStorage()) return null;
  try {
    const raw = localStorage.getItem(CACHED_USER_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as UserResponse;
  } catch {
    return null;
  }
}

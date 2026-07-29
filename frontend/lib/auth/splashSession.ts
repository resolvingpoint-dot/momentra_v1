const SPLASH_SEEN_KEY = "momentra_splash_seen";

export function shouldSkipSplash(): boolean {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem(SPLASH_SEEN_KEY) === "1";
}

export function markSplashSeen(): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(SPLASH_SEEN_KEY, "1");
}

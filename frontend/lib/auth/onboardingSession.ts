const ONBOARDING_SEEN_KEY = "momentra_onboarding_seen";

export function shouldSkipOnboarding(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(ONBOARDING_SEEN_KEY) === "1";
}

export function markOnboardingSeen(): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ONBOARDING_SEEN_KEY, "1");
}

export function isOnboardingSeen(): boolean {
  return shouldSkipOnboarding();
}

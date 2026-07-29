import { liveActivity } from "@/lib/marketing/copy";

/**
 * Marketing social-proof count for “moments active today”.
 * Override in staging/testing with NEXT_PUBLIC_MARKETING_ACTIVE_MOMENTS
 * (e.g. 150 or 4286). Ready to swap for an API later.
 */
export function getActiveMomentsCount(): string {
  const env = process.env.NEXT_PUBLIC_MARKETING_ACTIVE_MOMENTS?.trim();
  if (env) {
    const numeric = Number(env.replace(/,/g, ""));
    if (Number.isFinite(numeric)) {
      return numeric.toLocaleString("en-IN");
    }
    return env;
  }
  return liveActivity.count;
}

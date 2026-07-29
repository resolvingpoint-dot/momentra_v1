/** Marketing CTA analytics — Firebase Analytics + optional window hook. */

import { MomentraAnalytics } from "@/lib/analytics";

export type MarketingCtaEvent =
  | "start_a_moment"
  | "start_first_moment"
  | "open_app"
  | "explore_personal"
  | "explore_group"
  | "explore_business"
  | "read_the_book"
  | "see_how_moments_work";

declare global {
  interface Window {
    momentraMarketing?: {
      track?: (event: string, props?: Record<string, unknown>) => void;
    };
  }
}

function toStringParams(
  props?: Record<string, unknown>,
): Record<string, string> {
  if (!props) return {};
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(props)) {
    if (value === undefined || value === null) continue;
    out[key] = String(value);
  }
  return out;
}

/**
 * Track a marketing CTA (or related marketing event).
 * Sends to Firebase Analytics when configured; also dispatches a DOM hook for local tooling.
 */
export function trackMarketingCta(
  event: string,
  props?: Record<string, unknown>,
) {
  if (typeof window === "undefined") return;

  const params = toStringParams(props);

  try {
    window.momentraMarketing?.track?.(event, props);
    window.dispatchEvent(
      new CustomEvent("momentra:cta", { detail: { event, ...props } }),
    );
  } catch {
    /* no-op */
  }

  void MomentraAnalytics.logCustomEvent(event, {
    surface: "marketing",
    ...params,
  });
}

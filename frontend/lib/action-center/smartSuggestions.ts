/**
 * Smart suggestions — client heuristics from already-loaded projection/pulse signals.
 * No new APIs.
 */
import type { QuickAddActionTemplate } from "@/lib/quick_add/types";

export type SuggestionSignals = {
  /** Experience: no bookings / accommodation */
  missingBookings?: boolean;
  /** Purchase: funded percent 0–100 */
  fundedPercent?: number;
  /** Living: rent overdue / unpaid */
  rentOverdue?: boolean;
};

export function rankSmartSuggestions(
  templateId: string,
  actions: QuickAddActionTemplate[],
  signals: SuggestionSignals,
): QuickAddActionTemplate[] {
  const byId = new Map(actions.map((a) => [a.action_id, a]));
  const out: QuickAddActionTemplate[] = [];

  if (templateId === "group.trip" && signals.missingBookings) {
    const booking = byId.get("BOOKING");
    if (booking) out.push(booking);
  }
  if (templateId === "group.purchase" && (signals.fundedPercent ?? 0) >= 90) {
    const contrib = byId.get("CONTRIBUTOR") ?? byId.get("CONTRIBUTION");
    if (contrib) out.push(contrib);
  }
  if (templateId === "group.living" && signals.rentOverdue) {
    const rent = byId.get("RENT");
    if (rent) out.push(rent);
  }
  return out;
}

/** Derive signals from loose pulse/moments payloads already on the client. */
export function deriveSuggestionSignals(
  templateId: string,
  pulseLike: Record<string, unknown> | null | undefined,
): SuggestionSignals {
  if (!pulseLike) return {};
  const stats = (pulseLike.stats ?? pulseLike.pulse_data ?? {}) as Record<string, unknown>;
  if (templateId === "group.trip") {
    const bookings = Number(stats.confirmed_bookings ?? stats.confirmedBookings ?? 0);
    return { missingBookings: bookings <= 0 };
  }
  if (templateId === "group.purchase") {
    const pct = Number(
      stats.funding_percent ?? stats.completion_percentage ?? pulseLike.completion_percentage ?? 0,
    );
    return { fundedPercent: pct };
  }
  if (templateId === "group.living") {
    const overdue = Boolean(stats.rent_overdue ?? stats.rentOverdue ?? false);
    return { rentOverdue: overdue };
  }
  return {};
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";
import { FB_PULSE_SUMMARY_IDS } from "@/lib/personal/future_building/pulse/fbPulseUtils";

type Signal = { signal_id: string; label: string; trend: string };

const FALLBACK_LABELS: Record<string, string> = {
  learning: "Learning",
  execution: "Execution",
  momentum: "Momentum",
  confidence: "Confidence",
};

type Props = { signals: Signal[] };

export function FbPulseSummaryBar({ signals }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const byId = Object.fromEntries(signals.map((s) => [s.signal_id.toLowerCase(), s]));

  return (
    <div
      className="flex items-center justify-between px-4 py-3"
      style={{ ...personalGlassCardStyle(tokens), borderRadius: 20 }}
    >
      {FB_PULSE_SUMMARY_IDS.map((id) => {
        const signal = byId[id];
        // Chrome-only label fallback; never invent KPI trend arrows without API signal.
        const label = signal?.label ?? FALLBACK_LABELS[id];
        if (!signal?.trend) {
          return (
            <div key={id} className="flex items-center gap-1.5">
              <span style={{ fontSize: 10, fontWeight: 700, opacity: 0.8 }}>{label}</span>
            </div>
          );
        }
        const tint =
          id === "execution"
            ? colors.brandSecondary
            : id === "momentum"
              ? colors.brandTertiary
              : colors.brandPrimary;
        return (
          <div key={id} className="flex items-center gap-1.5">
            <span style={{ fontSize: 10, fontWeight: 700, opacity: 0.8 }}>{label}</span>
            <span style={{ fontSize: 10, fontWeight: 900, color: tint }}>{fbPulseCopy.trendArrow(signal.trend)}</span>
          </div>
        );
      })}
    </div>
  );
}

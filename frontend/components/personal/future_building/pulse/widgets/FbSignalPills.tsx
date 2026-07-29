"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";

type Signal = { signal_id: string; label: string; trend: string };

type Props = { signals: Signal[] };

function pillStyle(signalId: string, colors: ReturnType<typeof useThemeTokens>["colors"]) {
  const id = signalId.toLowerCase();
  if (id.includes("momentum") || id.includes("accelerat")) {
    return { bg: `${colors.primaryContainer}4d`, color: colors.brandPrimary, border: `${colors.brandPrimary}33` };
  }
  if (id.includes("opportunity") || id.includes("emerging")) {
    return { bg: `${colors.brandSecondary}33`, color: colors.brandSecondary, border: `${colors.brandSecondary}33` };
  }
  if (id.includes("learning")) {
    return { bg: `${colors.brandTertiary}33`, color: colors.brandTertiary, border: `${colors.brandTertiary}33` };
  }
  return { bg: `${colors.brandPrimary}33`, color: colors.brandPrimary, border: `${colors.brandPrimary}33` };
}

export function FbSignalPills({ signals }: Props) {
  const { colors } = useThemeTokens();

  if (signals.length === 0) return null;

  return (
    <section className="flex flex-wrap gap-2">
      {signals.map((signal) => {
        const style = pillStyle(signal.signal_id, colors);
        const arrow = signal.trend === "STRONG_UP" ? "↑↑" : fbPulseCopy.trendArrow(signal.trend);
        return (
          <span
            key={signal.signal_id}
            className="flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[10px] font-bold"
            style={{ background: style.bg, color: style.color, borderColor: style.border }}
          >
            {signal.label} <span style={{ opacity: 0.6 }}>{arrow}</span>
          </span>
        );
      })}
    </section>
  );
}

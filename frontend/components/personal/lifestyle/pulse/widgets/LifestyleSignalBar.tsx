"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifestylePulseMetrics } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";

type Signal = PersonalLifestylePulseMetrics["signals"][number];
type Props = { signals: Signal[] };

export function LifestyleSignalBar({ signals }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section
      className="flex items-center justify-between overflow-x-auto whitespace-nowrap"
      style={{
        ...personalGlassCardStyle(tokens),
        borderRadius: 999,
        padding: "10px 14px",
        background: `${colors.surfaceContainer}80`,
      }}
    >
      {signals.map((signal, i) => (
        <div
          key={signal.signal_id}
          className="flex items-center gap-1.5 px-2"
          style={{
            borderRight: i < signals.length - 1 ? "1px solid rgba(255,255,255,0.05)" : undefined,
          }}
        >
          <span style={{ ...personalTypography.labelSm, fontWeight: 700, color: colors.textSecondary }}>
            {lifestylePulseCopy.signalLabels[signal.signal_id] ?? signal.signal_id}
          </span>
          <span style={{ ...personalTypography.labelSm, fontWeight: 700, color: colors.tertiary }}>
            {lifestylePulseCopy.trendArrow(signal.trend)}
          </span>
        </div>
      ))}
    </section>
  );
}

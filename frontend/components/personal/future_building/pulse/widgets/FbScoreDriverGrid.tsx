"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";
import { FB_SEGMENT_COLORS } from "@/lib/personal/future_building/pulse/fbPulseUtils";
import { Brain, Flag, Zap } from "lucide-react";

const MOMENT_TYPE = "FUTURE_BUILDING";

type Driver = { driver_id: string; label: string; impact: number; fill_percent: number };

const DRIVER_ICONS: Record<string, typeof Brain> = {
  learning: Brain,
  execution: Zap,
  milestones: Flag,
};

type Props = { drivers: Driver[] };

export function FbScoreDriverGrid({ drivers }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 20, padding: 16 }}>
      <PersonalWidgetSectionHeader title={fbPulseCopy.scoreDriversTitle} explainerId="PULSE-002" momentTypeCode={MOMENT_TYPE} className="mb-3" />
      <div className="grid grid-cols-3 gap-3">
        {drivers.map((driver, i) => {
          const Icon = DRIVER_ICONS[driver.driver_id] ?? Zap;
          const accent = FB_SEGMENT_COLORS[i % FB_SEGMENT_COLORS.length];
          return (
            <div
              key={driver.driver_id}
              className="flex flex-col items-center rounded-2xl border p-3"
              style={{ background: "rgba(255,255,255,0.04)", borderColor: "rgba(255,255,255,0.06)" }}
            >
              <Icon size={20} color={accent} />
              <span style={{ fontSize: 10, fontWeight: 700, marginTop: 4 }}>{driver.label}</span>
              <span style={{ fontSize: 12, fontWeight: 900, color: colors.brandTertiary }}>+{driver.impact}</span>
              <div className="mt-2 h-1 w-full overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.08)" }}>
                <div className="h-full rounded-full" style={{ width: `${driver.fill_percent}%`, background: accent }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

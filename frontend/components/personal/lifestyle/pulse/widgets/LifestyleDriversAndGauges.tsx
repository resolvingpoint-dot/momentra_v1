"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import type { PersonalLifestylePulseMetrics } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";
import { LIFESTYLE_GAUGE_COLORS, resolveLifestyleActivityIcon } from "@/lib/personal/lifestyle/pulse/lifestylePulseIcons";

const MOMENT_TYPE = "LIFESTYLE";

type Props = {
  drivers: PersonalLifestylePulseMetrics["score_drivers"];
  gauges: PersonalLifestylePulseMetrics["gauges"];
};

function MiniRing({ percent, color, label }: { percent: number; color: string; label: string }) {
  const r = 20;
  const c = 2 * Math.PI * r;
  const offset = c - (percent / 100) * c;

  return (
    <div className="flex flex-col items-center">
      <div className="relative size-12">
        <svg className="-rotate-90" viewBox="0 0 48 48" width={48} height={48}>
          <circle cx="24" cy="24" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="3" />
          <circle cx="24" cy="24" r={r} fill="none" stroke={color} strokeWidth="3" strokeDasharray={c} strokeDashoffset={offset} />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center text-[11px] font-bold">{percent}</div>
      </div>
      <span className="mt-1 text-[8px] font-bold uppercase opacity-60">{label}</span>
    </div>
  );
}

export function LifestyleDriversAndGauges({ drivers, gauges }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
        <div className="mb-3 flex items-center gap-0.5">
          <h3 className="text-[10px] font-bold uppercase tracking-wider opacity-60">{lifestylePulseCopy.scoreDriversTitle}</h3>
          <WidgetInfoButton explainerId="PULSE-002" momentTypeCode={MOMENT_TYPE} />
        </div>
        <div className="space-y-2">
          {drivers.map((driver) => {
            const Icon = resolveLifestyleActivityIcon(driver.driver_id, driver.driver_id);
            const negative = driver.impact < 0;
            return (
              <div
                key={driver.driver_id}
                className="flex items-center justify-between rounded-lg p-2"
                style={{
                  background: colors.surfaceContainer,
                  border: negative ? `1px solid ${colors.error}33` : undefined,
                }}
              >
                <div className="flex items-center gap-2">
                  <Icon size={16} color={negative ? colors.error : colors.tertiary} />
                  <span className="text-[10px] font-semibold">
                    {lifestylePulseCopy.driverLabels[driver.driver_id] ?? driver.driver_id}
                  </span>
                </div>
                <span className="text-[10px] font-extrabold" style={{ color: negative ? colors.error : colors.tertiary }}>
                  {driver.impact >= 0 ? `+${driver.impact}` : driver.impact}
                </span>
              </div>
            );
          })}
        </div>
      </div>
      <div style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
        <div className="mb-3 flex items-center gap-0.5">
          <h3 className="text-[10px] font-bold uppercase tracking-wider opacity-60">{lifestylePulseCopy.stateGaugesTitle}</h3>
          <WidgetInfoButton explainerId="PULSE-008" momentTypeCode={MOMENT_TYPE} />
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {gauges.map((gauge) => (
            <MiniRing
              key={gauge.gauge_id}
              percent={gauge.percent}
              color={LIFESTYLE_GAUGE_COLORS[gauge.gauge_id] ?? colors.brandPrimary}
              label={gauge.label ?? lifestylePulseCopy.gaugeLabels[gauge.gauge_id] ?? gauge.gauge_id}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

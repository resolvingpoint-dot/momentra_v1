"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsDriver } from "@/lib/api/personal";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type Props = {
  bestDrivers: PersonalLifeOpsDriver[];
  lowestDrivers: PersonalLifeOpsDriver[];
};

export function FbDriversGrid({ bestDrivers, lowestDrivers }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
        <div className="mb-4 flex items-center gap-0.5">
          <p style={{ ...personalTypography.labelSm, fontSize: 11, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", opacity: 0.7 }}>
            {fbMemoryCopy.sections.bestDrivers}
          </p>
          <WidgetInfoButton explainerId="MEMORY-003" momentTypeCode="FUTURE_BUILDING" />
        </div>
        <div className="space-y-3">
          {bestDrivers.map((driver) => (
            <div key={driver.rank}>
              <div className="mb-1 flex justify-between text-xs">
                <span style={{ fontWeight: 500, color: colors.textPrimary }}>#{driver.rank} {driver.label}</span>
                <span style={{ fontWeight: 700, color: colors.brandPrimary }}>{driver.impact_percent}%</span>
              </div>
              {driver.impact_description ? (
                <p style={{ fontSize: 10, color: `${colors.brandPrimary}99`, marginBottom: 4 }}>{driver.impact_description}</p>
              ) : null}
              <div className="h-1.5 overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.05)" }}>
                <div className="h-full rounded-full" style={{ width: `${driver.impact_percent}%`, background: colors.brandPrimary, opacity: 1 - (driver.rank - 1) * 0.15 }} />
              </div>
            </div>
          ))}
        </div>
      </section>
      <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
        <div className="mb-4 flex items-center gap-0.5">
          <p style={{ ...personalTypography.labelSm, fontSize: 11, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", opacity: 0.7 }}>
            {fbMemoryCopy.sections.lowestDrivers}
          </p>
          <WidgetInfoButton explainerId="MEMORY-004" momentTypeCode="FUTURE_BUILDING" />
        </div>
        <div className="space-y-2">
          {lowestDrivers.map((driver) => (
            <div
              key={driver.rank}
              className="rounded-xl border p-2"
              style={{ background: `${colors.error ?? "#ffb4ab"}1a`, borderColor: `${colors.error ?? "#ffb4ab"}33` }}
            >
              <div className="mb-1 flex items-center justify-between">
                <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: colors.error }}>{driver.label}</span>
                <span style={{ fontSize: 12, color: colors.textPrimary }}>{driver.impact_percent}%</span>
              </div>
              <p style={{ fontSize: 10, color: colors.textSecondary, lineHeight: 1.3 }}>{driver.impact_description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

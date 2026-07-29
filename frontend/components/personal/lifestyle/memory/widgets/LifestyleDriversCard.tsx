"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifeOpsDriver } from "@/lib/api/personal";

type Props = {
  drivers: PersonalLifeOpsDriver[];
  variant: "best" | "lowest";
};

export function LifestyleDriversCard({ drivers, variant }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const isBest = variant === "best";

  return (
    <div
      style={{
        ...personalGlassCardStyle(tokens),
        borderRadius: 16,
        padding: 16,
        borderColor: isBest ? undefined : `${colors.error}33`,
      }}
    >
      <LifestyleSectionBadge index={isBest ? 3 : 4} label={isBest ? "Best Drivers" : "Lowest Drivers"} accent={isBest} explainerId={isBest ? "MEMORY-003" : "MEMORY-004"} />
      <div className="space-y-3">
        {drivers.map((driver) =>
          isBest ? (
            <div key={`${driver.rank}-${driver.label}`}>
              <div className="mb-1 flex justify-between text-[11px] font-bold">
                <span>{driver.label}</span>
                <span style={{ color: colors.brandPrimary }}>{driver.impact_percent}%</span>
              </div>
              <div className="mb-1 h-1 overflow-hidden rounded-full" style={{ background: colors.surfaceContainer }}>
                <div className="h-full rounded-full" style={{ width: `${driver.impact_percent}%`, background: colors.brandPrimary }} />
              </div>
              {driver.impact_description ? (
                <p className="text-[9px] leading-tight opacity-60">{driver.impact_description}</p>
              ) : null}
            </div>
          ) : (
            <div key={`${driver.rank}-${driver.label}`} className="rounded-lg border p-2" style={{ background: `${colors.error}0d`, borderColor: `${colors.error}1a` }}>
              <span className="block text-[10px] opacity-60">{driver.label}</span>
              <span className="text-sm font-bold" style={{ color: colors.error }}>
                {driver.impact_percent}% Impact
              </span>
              {driver.impact_description ? (
                <p className="mt-1 text-[9px] opacity-60">{driver.impact_description}</p>
              ) : null}
            </div>
          ),
        )}
      </div>
    </div>
  );
}

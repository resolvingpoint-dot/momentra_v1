"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsDriver } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";

type Props = {copy?: PersonalMemoryCopy;  drivers: PersonalLifeOpsDriver[]; variant: "best" | "lowest"; momentTypeCode?: string | null };

export function DriversSection({ drivers, variant, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;
  const isLowest = variant === "lowest";
  const label = isLowest ? memoryCopy.sectionLabels.lowestDrivers : memoryCopy.sectionLabels.bestDrivers;
  const accent = isLowest ? colors.error ?? "#ffb4ab" : colors.brandPrimary;

  return (
    <PersonalGlassGlowSection tokens={tokens} cornerRadius={16} innerStyle={{ padding: tokens.spacing.md }}>
      <div className="flex items-center gap-0.5">
        <p style={memoryMicroLabelStyle(tokens, accent)}>{label}</p>
        <WidgetInfoButton explainerId={isLowest ? "MEMORY-004" : "MEMORY-003"} momentTypeCode={momentTypeCode} />
      </div>
      <div className="mt-3 space-y-3">
        {drivers.map((driver, index) => {
          const key = `${variant}-${driver.label}-${driver.rank}-${index}`;
          return isLowest ? (
            <div
              key={key}
              className="flex items-center gap-2 rounded-xl p-2"
              style={{
                background: driver.rank === 1 ? `${accent}1a` : `${colors.textSecondary}14`,
                border: driver.rank === 1 ? `1px solid ${accent}33` : "none",
              }}
            >
              <span
                className="flex h-5 w-5 items-center justify-center rounded-md"
                style={{
                  ...personalTypography.microLabel,
                  background: `${accent}33`,
                  color: accent,
                }}
              >
                {driver.rank}
              </span>
              <div>
                <p style={{ ...personalTypography.labelSm, fontWeight: 700, color: colors.textPrimary }}>
                  {driver.label}
                </p>
                <p style={{ ...personalTypography.microLabel, opacity: 0.6, color: accent }}>
                  {driver.impact_percent}% Impact
                  {driver.impact_description ? `: ${driver.impact_description}` : ""}
                </p>
              </div>
            </div>
          ) : (
            <div key={key}>
              <div className="mb-1 flex justify-between" style={personalTypography.labelSm}>
                <span style={{ fontWeight: 700, color: colors.textPrimary }}>
                  {driver.rank} {driver.label}
                </span>
                <span style={{ color: colors.brandPrimary }}>{driver.impact_percent}%</span>
              </div>
              {driver.impact_description ? (
                <p style={{ ...personalTypography.microLabel, opacity: 0.7, color: colors.textSecondary }}>
                  {driver.impact_description}
                </p>
              ) : null}
              <div className="h-1 overflow-hidden rounded-full" style={{ background: `${colors.textSecondary}14` }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${driver.impact_percent}%`,
                    background: colors.brandPrimary,
                    opacity: driver.rank === 1 ? 1 : 0.5,
                    boxShadow: driver.rank === 1 ? `0 0 8px ${colors.brandPrimary}80` : undefined,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </PersonalGlassGlowSection>
  );
}


"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { Heart } from "lucide-react";
import { LifeCard } from "./LifeCard";
import { LifeHappinessBar } from "./LifeHappinessBar";
import { LifeSectionLabel } from "./LifeSectionLabel";

type HappinessDriversCardProps = {
  happiness: PersonalLifeMetrics["happiness"];
};

export function HappinessDriversCard({ happiness }: HappinessDriversCardProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard>
      <LifeSectionLabel explainerId="LIFE-009">{personalLifeCopy.sections.happiness}</LifeSectionLabel>
      <div className="mt-4 grid gap-6 md:grid-cols-2">
        <div>
          <span style={{ ...personalTypography.microLabel, fontWeight: 700, color: colors.success }}>
            {personalLifeCopy.sections.topDrivers}
          </span>
          <ul className="mt-3 space-y-3">
            {happiness.top_drivers.map((driver) => (
              <li key={driver} className="flex items-center gap-2" style={{ ...personalTypography.labelSm }}>
                <Heart className="size-3" style={{ color: colors.success }} />
                {driver}
              </li>
            ))}
          </ul>
        </div>
        <div className="space-y-4">
          <div>
            <span style={{ ...personalTypography.microLabel, fontWeight: 700, color: colors.brandTertiary }}>
              {personalLifeCopy.sections.highestReturn}
            </span>
            {happiness.highest_return.map((bar) => (
              <LifeHappinessBar key={bar.label} label={bar.label} fraction={bar.height_fraction} variant="high" />
            ))}
          </div>
          <div>
            <span style={{ ...personalTypography.microLabel, fontWeight: 700, color: colors.error }}>
              {personalLifeCopy.sections.lowestReturn}
            </span>
            {happiness.lowest_return.map((bar) => (
              <LifeHappinessBar key={bar.label} label={bar.label} fraction={bar.height_fraction} variant="low" />
            ))}
          </div>
        </div>
      </div>
      <p
        className="mt-4 border-t pt-4 italic"
        style={{
          ...personalTypography.microLabel,
          opacity: 0.6,
          color: colors.textSecondary,
          borderColor: colors.border,
        }}
      >
        {happiness.footer_text}
      </p>
    </LifeCard>
  );
}

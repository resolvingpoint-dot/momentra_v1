"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { LifeGraphVisual } from "@/components/personal/shared/LifeGraphVisual";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeHealthHero } from "@/lib/api/personal";
import { ArrowUp } from "lucide-react";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type LifeHealthHeroProps = {
  lifeHealth: PersonalLifeHealthHero;
};

export function LifeHealthHero({ lifeHealth }: LifeHealthHeroProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <LifeCard className="relative overflow-hidden p-6 md:p-8" glow>
      <div className="flex flex-col items-center gap-8 md:flex-row md:justify-between">
        <div className="order-2 w-full md:order-1 md:max-w-xs">
          <LifeSectionLabel explainerId="LIFE-001">{personalLifeCopy.sections.personalLifeHealth}</LifeSectionLabel>
          <div className="mt-4 flex items-baseline gap-2">
            <span style={{ ...personalTypography.heroTitle, fontSize: 48, color: colors.textPrimary }}>
              {lifeHealth.life_score}
            </span>
            <span style={{ ...personalTypography.bodyMd, opacity: 0.5, color: colors.textSecondary }}>
              {personalLifeCopy.scoreSuffix}
            </span>
          </div>
          <p className="mt-2 font-medium" style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
            {lifeHealth.status_label}
          </p>
          {lifeHealth.delta_month != null ? (
            <p
              className="mt-1 flex items-center gap-1"
              style={{ ...personalTypography.labelSm, color: colors.success }}
            >
              <ArrowUp className="size-3" />
              {personalLifeCopy.deltaMonthLabel(lifeHealth.delta_month)}
            </p>
          ) : null}
          <p
            className="mt-4 italic leading-relaxed"
            style={{ ...personalTypography.microLabel, opacity: 0.7, color: colors.textSecondary }}
          >
            &ldquo;{lifeHealth.insight_quote}&rdquo;
          </p>
        </div>
        <div className="order-1 w-full md:order-2 md:flex-1">
          <LifeGraphVisual
            tokens={tokens}
            centerScore={lifeHealth.life_score}
            satelliteScores={lifeHealth.satellite_scores}
          />
        </div>
      </div>
    </LifeCard>
  );
}

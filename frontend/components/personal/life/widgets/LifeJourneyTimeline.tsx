"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type LifeJourneyTimelineProps = {
  journey: PersonalLifeMetrics["journey"];
};

export function LifeJourneyTimeline({ journey }: LifeJourneyTimelineProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard>
      <LifeSectionLabel explainerId="LIFE-003">{personalLifeCopy.sections.journey}</LifeSectionLabel>
      <div className="relative mt-4 space-y-4 pl-6">
        <div
          className="absolute bottom-0 left-1 top-0 w-px"
          style={{ background: `color-mix(in srgb, ${colors.textPrimary} 10%, transparent)` }}
        />
        {journey.map((item, index) => (
          <div key={`journey-${index}-${item.period_label}`} className="relative flex items-center gap-6">
            <div
              className="absolute -left-6 size-2.5 rounded-full"
              style={{ background: colors.brandPrimary }}
            />
            <span
              className="w-10 uppercase"
              style={{ ...personalTypography.labelSm, fontWeight: 700, color: colors.textPrimary }}
            >
              {item.period_label}
            </span>
            <span style={{ ...personalTypography.labelSm, opacity: 0.7, color: colors.textSecondary }}>
              {item.summary}
            </span>
          </div>
        ))}
      </div>
    </LifeCard>
  );
}

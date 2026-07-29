"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { badgeStyle, personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type LifeBalanceModelProps = {
  balance: PersonalLifeMetrics["balance_model"];
};

export function LifeBalanceModel({ balance }: LifeBalanceModelProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <LifeSectionLabel explainerId="LIFE-002">{personalLifeCopy.sections.lifeBalance}</LifeSectionLabel>
        <span
          className="uppercase tracking-wide"
          style={{ ...personalTypography.microLabel, opacity: 0.5, color: colors.textSecondary }}
        >
          {balance.subtitle}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {balance.dimensions.map((dim) => (
          <div
            key={dim.dimension_code}
            className="rounded-xl border p-3"
            style={{ borderColor: colors.border, background: colors.surfaceContainer }}
          >
            <span style={{ ...personalTypography.microLabel, opacity: 0.6, color: colors.textSecondary }}>
              {dim.label}
            </span>
            <p style={{ ...personalTypography.heroTitle, fontSize: 28, marginTop: 4 }}>{dim.score}</p>
            <span
              className="mt-1 inline-block rounded px-2 py-0.5 uppercase"
              style={{ ...personalTypography.microLabel, fontWeight: 700, ...badgeStyle(dim.badge_color_token, colors) }}
            >
              {dim.badge_label.toUpperCase()}
            </span>
            <p
              className="mt-2 leading-tight"
              style={{ ...personalTypography.microLabel, opacity: 0.6, color: colors.textSecondary }}
            >
              {dim.driver_text}
            </p>
          </div>
        ))}
      </div>
    </LifeCard>
  );
}

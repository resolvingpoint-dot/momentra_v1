"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { TrendingUp } from "lucide-react";
import { LifeCard } from "./LifeCard";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type LifeLeverageCardProps = {
  leverage: NonNullable<PersonalLifeMetrics["leverage"]>;
  onQuickAdd?: (eventType: string) => void;
};

export function LifeLeverageCard({ leverage, onQuickAdd }: LifeLeverageCardProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard
      style={{
        borderColor: `color-mix(in srgb, ${colors.success} 30%, transparent)`,
        background: `color-mix(in srgb, ${colors.success} 6%, transparent)`,
      }}
    >
      <div className="mb-3 flex items-center gap-2" style={{ color: colors.success }}>
        <TrendingUp className="size-4" />
        <span style={{ ...personalTypography.labelSm, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          {personalLifeCopy.sections.leverage}
        </span>
        <WidgetInfoButton explainerId="LIFE-008" />
      </div>
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h4 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>{leverage.title}</h4>
          <p className="mt-1" style={{ ...personalTypography.labelSm, opacity: 0.85, color: colors.textSecondary }}>
            {leverage.body}
          </p>
        </div>
        <button
          type="button"
          onClick={() => onQuickAdd?.(leverage.action_code)}
          className="shrink-0 rounded-xl border px-4 py-2"
          style={{
            ...personalTypography.labelSm,
            fontWeight: 700,
            borderColor: `color-mix(in srgb, ${colors.success} 40%, transparent)`,
            color: colors.success,
          }}
        >
          {leverage.cta_label}
        </button>
      </div>
      <div
        className="mt-4 grid grid-cols-4 gap-3 border-t pt-4"
        style={{ borderColor: `color-mix(in srgb, ${colors.success} 20%, transparent)` }}
      >
        {leverage.expected_impact.map((imp) => (
          <div key={imp.dimension_code}>
            <span style={{ ...personalTypography.labelSm, opacity: 0.6, color: colors.textSecondary }}>
              {imp.label}
            </span>
            <p
              style={{
                ...personalTypography.labelSm,
                fontWeight: 700,
                color: imp.delta >= 0 ? colors.success : colors.error,
              }}
            >
              {imp.delta >= 0 ? "+" : ""}
              {imp.delta}
            </p>
          </div>
        ))}
      </div>
    </LifeCard>
  );
}

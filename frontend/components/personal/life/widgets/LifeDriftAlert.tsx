"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { AlertTriangle } from "lucide-react";
import { LifeCard } from "./LifeCard";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type LifeDriftAlertProps = {
  alert: NonNullable<PersonalLifeMetrics["drift_alert"]>;
  onQuickAdd?: (eventType: string) => void;
};

export function LifeDriftAlert({ alert, onQuickAdd }: LifeDriftAlertProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard
      style={{
        borderColor: `color-mix(in srgb, ${colors.error} 40%, transparent)`,
        background: `color-mix(in srgb, ${colors.error} 8%, transparent)`,
      }}
    >
      <div className="mb-3 flex items-center gap-2" style={{ color: colors.error }}>
        <AlertTriangle className="size-4" />
        <span style={{ ...personalTypography.labelSm, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          {personalLifeCopy.sections.driftAlert}
        </span>
        <WidgetInfoButton explainerId="LIFE-007" />
      </div>
      <h4 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>{alert.title}</h4>
      <p className="mt-2" style={{ ...personalTypography.labelSm, opacity: 0.85, color: colors.textSecondary }}>
        {alert.body}
      </p>
      <button
        type="button"
        className="mt-4 w-full rounded-xl border py-2"
        onClick={() => onQuickAdd?.("CUSTOM_ACTIVITY")}
        style={{
          ...personalTypography.labelSm,
          fontWeight: 700,
          borderColor: `color-mix(in srgb, ${colors.error} 40%, transparent)`,
          color: colors.error,
        }}
      >
        {alert.cta_label}
      </button>
    </LifeCard>
  );
}

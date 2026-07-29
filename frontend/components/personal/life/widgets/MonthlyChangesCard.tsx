"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { ArrowDown, ArrowUp } from "lucide-react";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type MonthlyChangesCardProps = {
  changes: PersonalLifeMetrics["monthly_changes"];
};

export function MonthlyChangesCard({ changes }: MonthlyChangesCardProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard>
      <LifeSectionLabel explainerId="LIFE-011">{personalLifeCopy.sections.monthlyChanges}</LifeSectionLabel>
      <div className="mt-4 space-y-3">
        {changes.map((ch) => {
          const positive =
            ch.direction === "UP"
              ? ch.change_code !== "MONEY_PRESSURE"
              : ch.change_code === "MONEY_PRESSURE";
          return (
            <div key={ch.change_code} className="flex items-center justify-between">
              <div>
                <p style={{ ...personalTypography.labelSm, fontWeight: 600, color: colors.textPrimary }}>
                  {ch.label}
                </p>
                <p style={{ ...personalTypography.microLabel, opacity: 0.5, color: colors.textSecondary }}>
                  {ch.sublabel}
                </p>
              </div>
              <span
                className="flex items-center gap-1"
                style={{
                  ...personalTypography.labelSm,
                  fontWeight: 700,
                  color: positive ? colors.success : colors.error,
                }}
              >
                {ch.delta_percent}%
                {ch.direction === "UP" ? <ArrowUp className="size-3" /> : <ArrowDown className="size-3" />}
              </span>
            </div>
          );
        })}
      </div>
    </LifeCard>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsTurningPoint } from "@/lib/api/personal";
import { lifeOpsMomentsCopy } from "@/lib/personal/life_operations/moments/lifeOpsMomentsCopy";
import { Flag } from "lucide-react";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";

type TurningPointsListProps = {
  points: PersonalLifeOpsTurningPoint[];
};

export function TurningPointsList({ points }: TurningPointsListProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section>
      <PersonalWidgetSectionHeader title={lifeOpsMomentsCopy.turningPointsTitle} explainerId="MOMENT-TP" momentTypeCode="LIFE_OPERATIONS" className="mb-3" />
      {points.length === 0 ? (
        <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
          {lifeOpsMomentsCopy.turningPointsEmpty}
        </p>
      ) : (
        <div className="space-y-2">
          {points.map((point) => (
            <PersonalGlassGlowSection
              key={point.turning_point_id}
              tokens={tokens}
              cornerRadius={16}
              className="flex cursor-pointer items-center gap-3 transition-transform hover:scale-[1.02] active:scale-95"
              innerClassName="flex items-center gap-3"
              innerStyle={{ padding: 12 }}
            >
              <div
                className="flex size-9 shrink-0 items-center justify-center rounded-xl"
                style={{ background: `${colors.brandPrimary}22` }}
              >
                <Flag className="size-4" style={{ color: colors.brandPrimary }} />
              </div>
              <div>
                <p className="font-semibold" style={{ color: colors.textPrimary }}>
                  {point.title}
                </p>
                <p className="text-xs" style={{ color: colors.textSecondary }}>
                  {point.subtitle}
                </p>
              </div>
            </PersonalGlassGlowSection>
          ))}
        </div>
      )}
    </section>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { ArcGauge } from "@/components/personal/life_operations/pulse/widgets/ArcGauge";
import { emotionColor, personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type DominantEmotionCardProps = {
  dominant: PersonalLifeMetrics["dominant_emotion"];
  onQuickAdd?: (eventType: string) => void;
};

export function DominantEmotionCard({ dominant, onQuickAdd }: DominantEmotionCardProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard>
      <LifeSectionLabel explainerId="LIFE-005">{personalLifeCopy.sections.dominantEmotion}</LifeSectionLabel>
      {dominant.is_sparse ? (
        <div className="mt-4 space-y-3">
          <p style={{ ...personalTypography.labelSm, opacity: 0.85, color: colors.textSecondary }}>
            {personalLifeCopy.dominantEmotionSparseBody}
          </p>
          <button
            type="button"
            onClick={() => onQuickAdd?.("REFLECTION")}
            className="rounded-xl border px-4 py-2"
            style={{
              ...personalTypography.labelSm,
              fontWeight: 700,
              borderColor: colors.brandPrimary,
              color: colors.brandPrimary,
            }}
          >
            {personalLifeCopy.sparseCta}
          </button>
        </div>
      ) : (
        <>
          <div className="mt-4 flex items-center gap-6">
            <ArcGauge
              gaugeId="life_dominant_emotion"
              percent={dominant.dominant_percent}
              label={dominant.dominant_label}
              size={72}
            />
            <div className="flex-1 space-y-2">
              {dominant.breakdown.map((row) => (
                <div key={row.emotion_code} className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2" style={{ ...personalTypography.labelSm, opacity: 0.85 }}>
                    <span
                      className="size-2 shrink-0 rounded-full"
                      style={{ background: emotionColor(row.color_token, colors) }}
                    />
                    {row.label}
                  </span>
                  <span style={{ ...personalTypography.labelSm, fontWeight: 600 }}>{row.percent}%</span>
                </div>
              ))}
            </div>
          </div>
          <p
            className="mt-4 text-center italic"
            style={{ ...personalTypography.microLabel, opacity: 0.6, color: colors.textSecondary }}
          >
            {dominant.footer_text}
          </p>
        </>
      )}
    </LifeCard>
  );
}

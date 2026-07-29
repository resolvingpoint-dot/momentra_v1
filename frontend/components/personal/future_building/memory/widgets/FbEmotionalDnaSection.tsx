"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsEmotionalDna } from "@/lib/api/personal";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type Props = { dna: PersonalLifeOpsEmotionalDna };

export function FbEmotionalDnaSection({ dna }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const segmentColors = [colors.brandPrimary, colors.brandSecondary, colors.brandTertiary];

  return (
    <section className="flex-1" style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="mb-4 flex items-center gap-0.5">
        <span style={{ ...personalTypography.labelSm, fontSize: 11, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", opacity: 0.7 }}>
          {fbMemoryCopy.sections.emotionalDna}
        </span>
        <WidgetInfoButton explainerId="MEMORY-007" momentTypeCode="FUTURE_BUILDING" />
      </div>
      <div className="flex flex-col items-center">
        <div
          className="relative flex size-24 items-center justify-center rounded-full border-8"
          style={{ borderColor: colors.surfaceContainer }}
        >
          <div className="flex flex-col items-center">
            <span style={{ fontSize: 12, fontWeight: 700, lineHeight: 1, color: colors.textPrimary }}>{dna.dominant_label.slice(0, 7).toUpperCase()}</span>
            <span style={{ fontSize: 8, color: colors.textSecondary, textTransform: "uppercase" }}>DNA</span>
          </div>
        </div>
        <div className="mt-3 w-full space-y-1">
          {dna.segments.map((seg, i) => (
            <div key={seg.segment_id} className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <div className="size-1.5 rounded-full" style={{ background: segmentColors[i % segmentColors.length] }} />
                <span style={{ fontSize: 10, color: colors.textSecondary }}>{seg.label}</span>
              </div>
              <span style={{ fontSize: 10, fontWeight: 700, color: colors.textPrimary }}>{seg.percent}%</span>
            </div>
          ))}
        </div>
      </div>
      <p className="mt-3 border-t pt-2 text-[10px] italic" style={{ borderColor: "rgba(255,255,255,0.06)", color: colors.textSecondary }}>
        {dna.insight_body}
      </p>
    </section>
  );
}

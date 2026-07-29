"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsTurningPoint } from "@/lib/api/personal";
import { fbMomentsCopy } from "@/lib/personal/future_building/moments/fbMomentsCopy";
import { FbSectionBadge } from "@/components/personal/future_building/moments/widgets/FbSectionBadge";
import { Award, BookOpen, Flag } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

const BORDER_COLORS = ["#a855f7", "#22d3ee"];
const ICONS = [BookOpen, Award, Flag];

type Props = { points: PersonalLifeOpsTurningPoint[] };

export function FbTurningPointsList({ points }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FbSectionBadge number={5} />
          <h2 style={{ ...personalTypography.labelSm, textTransform: "uppercase", letterSpacing: "0.12em", opacity: 0.6 }}>
            {fbMomentsCopy.turningPointsTitle}
          </h2>
          <WidgetInfoButton explainerId="MOMENT-TP" momentTypeCode="FUTURE_BUILDING" />
        </div>
        <button type="button" style={{ fontSize: 12, color: colors.brandPrimary, background: "none", border: "none" }}>
          {fbMomentsCopy.viewAll}
        </button>
      </div>
      {points.length === 0 ? (
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Turning points appear as your story develops.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {points.map((point, i) => {
            const border = BORDER_COLORS[i % BORDER_COLORS.length];
            const Icon = ICONS[i % ICONS.length];
            return (
              <div
                key={point.turning_point_id}
                className="flex cursor-pointer items-center gap-3 rounded-2xl border p-3 transition-transform hover:scale-[1.02] active:scale-95"
                style={{ ...personalGlassCardStyle(tokens), borderColor: `${border}4d` }}
              >
                <div
                  className="flex size-14 shrink-0 items-center justify-center rounded-xl border"
                  style={{ background: `${border}33`, borderColor: `${border}80` }}
                >
                  <Icon size={28} color={border} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h4 style={{ fontSize: 14, fontWeight: 700, color: colors.textPrimary }}>{point.title}</h4>
                  </div>
                  <p style={{ fontSize: 12, marginTop: 2, color: colors.textSecondary }}>{point.subtitle}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

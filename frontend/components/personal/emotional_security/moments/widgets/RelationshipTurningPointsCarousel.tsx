"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { PersonalEmotionalSecurityTurningPoint } from "@/lib/api/personalDomainTypes";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  relationshipsMomentsAccent,
  relationshipsMomentsCopy,
} from "@/lib/personal/emotional_security/moments/relationshipsMomentsCopy";
import { Flag, Plus, Shield } from "lucide-react";

type RelationshipTurningPointsCarouselProps = {
  points: PersonalEmotionalSecurityTurningPoint[];
};

function accentFor(color: string | null | undefined) {
  if (color === "blue") return "#4cd6ff";
  return relationshipsMomentsAccent.pink;
}

function IconFor({ icon }: { icon: string }) {
  if (icon === "shield") return <Shield className="size-5 text-white" />;
  if (icon === "add") return <Plus className="size-5 text-white" />;
  return <Flag className="size-5 text-white" />;
}

export function RelationshipTurningPointsCarousel({ points }: RelationshipTurningPointsCarouselProps) {
  const { colors } = useThemeTokens();
  if (points.length === 0) return null;

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-0.5">
          <h3 className="text-[10px] font-bold uppercase tracking-widest opacity-50">
            {relationshipsMomentsCopy.turningPointsTitle}
          </h3>
          <WidgetInfoButton explainerId="MOMENT-TP" momentTypeCode="RELATIONSHIPS" />
        </div>
        <button type="button" className="text-[10px] font-bold" style={{ color: "#818cf8" }}>
          {relationshipsMomentsCopy.viewAll}
        </button>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {points.map((point) => {
          const accent = accentFor(point.accent_color);
          return (
            <article
              key={point.turning_point_id}
              className="w-64 shrink-0 rounded-2xl p-3 transition-transform hover:scale-[1.02] active:scale-95"
              style={{ background: relationshipsMomentsAccent.cardBg, border: "1px solid rgba(255,255,255,0.08)" }}
            >
              <div
                className="mb-2 flex size-10 items-center justify-center rounded-xl"
                style={{ background: accent }}
              >
                <IconFor icon={point.icon} />
              </div>
              <h4 className="text-sm font-semibold" style={{ color: colors.textPrimary }}>
                {point.title}
              </h4>
              {point.date_label ? (
                <p className="mt-0.5 text-xs font-bold" style={{ color: accent }}>
                  {point.date_label}
                </p>
              ) : null}
              <p className="mt-1 text-xs opacity-75" style={{ color: colors.textSecondary }}>
                {point.subtitle}
              </p>
            </article>
          );
        })}
      </div>
    </section>
  );
}

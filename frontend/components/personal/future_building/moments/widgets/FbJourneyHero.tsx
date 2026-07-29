"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalFutureBuildingJourneyHero } from "@/lib/api/personalDomainTypes";
import { fbMomentsCopy } from "@/lib/personal/future_building/moments/fbMomentsCopy";
import { FbSectionBadge } from "@/components/personal/future_building/moments/widgets/FbSectionBadge";
import { TrendingUp } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type FbJourneyHeroProps = {
  hero: PersonalFutureBuildingJourneyHero;
};

export function FbJourneyHero({ hero }: FbJourneyHeroProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section
      className="overflow-hidden rounded-3xl"
      style={{
        ...personalGlassCardStyle(tokens),
        background: `linear-gradient(180deg, ${colors.primaryContainer}66 0%, rgba(13,17,45,1) 100%)`,
        borderRadius: 24,
      }}
    >
      <div style={{ padding: 16 }}>
        <div className="mb-4 flex items-center gap-2">
          <FbSectionBadge number={1} />
          <p style={{ ...personalTypography.labelSm, textTransform: "uppercase", letterSpacing: "0.12em", opacity: 0.6 }}>
            {fbMomentsCopy.journeyHeroSection}
          </p>
        </div>
        <div className="flex items-center gap-0.5">
          <h2 style={{ fontSize: 30, fontWeight: 800, color: colors.textPrimary, letterSpacing: "-0.02em" }}>
            {fbMomentsCopy.journeyHeroTitle}
          </h2>
          <WidgetInfoButton explainerId="MOMENT-001" momentTypeCode="FUTURE_BUILDING" />
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span style={{ fontSize: 60, fontWeight: 900, lineHeight: 1, color: colors.textPrimary }}>{hero.journey_score}</span>
          <span className="flex items-center gap-1 text-lg font-bold" style={{ color: "#4ade80" }}>
            <TrendingUp size={20} />
            {fbMomentsCopy.statusBandLabel(hero.status_band, hero.status_label)}
          </span>
        </div>
        <div className="mt-2 flex items-center gap-2 py-1.5 text-[10px] font-bold uppercase tracking-tighter">
          {hero.phases.map((phase, i) => (
            <span key={phase.phase_id} className="flex items-center gap-2">
              {i > 0 ? <span style={{ opacity: 0.4 }}>→</span> : null}
              <span
                style={{
                  color: phase.is_active ? colors.brandPrimary : colors.textSecondary,
                  opacity: phase.is_active ? 1 : 0.4,
                  borderBottom: phase.is_active ? `1px solid ${colors.brandPrimary}` : "none",
                  paddingBottom: 2,
                }}
              >
                {phase.label}
              </span>
            </span>
          ))}
        </div>
        <p className="mt-4 text-sm italic leading-relaxed" style={{ color: colors.textSecondary }}>
          &ldquo;{hero.insight_body}&rdquo;
        </p>
        <div className="mt-6 grid grid-cols-2 gap-2">
          {[
            { label: "Milestones", value: `${hero.milestones}` },
            { label: "Learning Sessions", value: `${hero.learning_events}` },
            { label: "Invested", value: fbMomentsCopy.formatInrMinor(hero.invested_minor) },
            { label: "Captured", value: `${hero.opportunities}` },
          ].map((tile) => (
            <div
              key={tile.label}
              className="rounded-xl border p-3"
              style={{ background: "rgba(255,255,255,0.05)", borderColor: "rgba(255,255,255,0.1)", backdropFilter: "blur(8px)" }}
            >
              <p style={{ fontSize: 22, fontWeight: 700, color: colors.textPrimary }}>{tile.value}</p>
              <p style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", color: colors.textSecondary }}>{tile.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalEmotionalSecurityJourneyHero } from "@/lib/api/personalDomainTypes";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  relationshipsMomentsAccent,
  relationshipsMomentsCopy,
} from "@/lib/personal/emotional_security/moments/relationshipsMomentsCopy";

type RelationshipJourneyHeroProps = {
  hero: PersonalEmotionalSecurityJourneyHero;
};

export function RelationshipJourneyHero({ hero }: RelationshipJourneyHeroProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const statusLabel = relationshipsMomentsCopy.statusBandLabel(hero.status_band);
  const activeIdx = hero.phases.findIndex((p) => p.is_active);

  return (
    <section
      style={{
        ...personalGlassCardStyle(tokens),
        borderRadius: 24,
        padding: 16,
        background: relationshipsMomentsAccent.cardBg,
        border: "1px solid rgba(255,255,255,0.1)",
      }}
    >
      <p className="text-[10px] font-bold uppercase tracking-widest opacity-50">
        {relationshipsMomentsCopy.journeyHeroSection}
      </p>
      <div className="mt-2 flex items-center gap-0.5">
        <h2 className="text-lg font-bold" style={{ color: colors.textPrimary }}>
          {relationshipsMomentsCopy.journeyHeroTitle}
        </h2>
        <WidgetInfoButton explainerId="MOMENT-001" momentTypeCode="RELATIONSHIPS" />
      </div>
      <div className="mt-3 flex flex-wrap items-end gap-2">
        <span className="text-6xl font-extrabold leading-none" style={{ color: colors.textPrimary }}>
          {hero.journey_score}
        </span>
        <span className="mb-2 text-lg font-bold text-emerald-400">{statusLabel}</span>
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-[9px] font-bold uppercase tracking-widest opacity-60">
        {hero.phases.map((phase, i) => (
          <span key={phase.phase_id} className="flex items-center gap-2">
            {i > 0 ? <span style={{ color: relationshipsMomentsAccent.pink }}>→</span> : null}
            <span style={{ color: phase.is_active ? colors.textPrimary : undefined, opacity: phase.is_active ? 1 : 0.4 }}>
              {phase.label}
            </span>
          </span>
        ))}
      </div>
      <div className="relative mt-4 h-24">
        <svg viewBox="0 0 400 120" className="h-full w-full" aria-hidden>
          <defs>
            <linearGradient id="rsJourneyGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={relationshipsMomentsAccent.purple} />
              <stop offset="100%" stopColor={relationshipsMomentsAccent.pink} />
            </linearGradient>
          </defs>
          <path
            d="M0,100 C50,90 100,110 150,70 C200,30 250,50 300,20 C350,-10 400,10 400,10"
            fill="none"
            stroke="url(#rsJourneyGradient)"
            strokeWidth={3}
          />
          <circle cx={150} cy={70} r={4} fill={relationshipsMomentsAccent.pink} />
          <circle cx={300} cy={20} r={4} fill={relationshipsMomentsAccent.pink} />
          <circle cx={400} cy={10} r={5} fill="#fff" />
          <text x={180} y={85} fill="#fff" fontSize={8} fontWeight={700}>
            {relationshipsMomentsCopy.pathMilestoneLabel}
          </text>
        </svg>
        <p className="mt-2 text-[11px] leading-tight opacity-70" style={{ color: colors.textSecondary }}>
          {hero.insight_body}
        </p>
      </div>
      <div
        className="mt-4 grid grid-cols-2 gap-2 border-t pt-4 text-center sm:grid-cols-4"
        style={{ borderColor: "rgba(255,255,255,0.05)" }}
      >
        {[
          { value: hero.connections, label: relationshipsMomentsCopy.statConnections },
          { value: hero.support, label: relationshipsMomentsCopy.statSupport },
          { value: hero.experiences, label: relationshipsMomentsCopy.statExperiences },
          { value: relationshipsMomentsCopy.formatInrMinor(hero.spend_minor), label: relationshipsMomentsCopy.statSpend },
        ].map((stat) => (
          <div key={stat.label}>
            <p className="text-xl font-bold sm:text-2xl">{stat.value}</p>
            <p className="text-[9px] font-semibold uppercase opacity-60 sm:text-[10px]">{stat.label}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalGlowWrapperStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifestyleJourneyHero } from "@/lib/api/personal";
import { lifestyleMomentsCopy } from "@/lib/personal/lifestyle/moments/lifestyleMomentsCopy";

type Props = { hero: PersonalLifestyleJourneyHero };

function phaseProgress(hero: PersonalLifestyleJourneyHero): number {
  const activeIdx = hero.phases.findIndex((p) => p.is_active);
  if (activeIdx <= 0) return 33;
  if (activeIdx === 1) return 66;
  return 100;
}

export function LifestyleJourneyHero({ hero }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const progress = phaseProgress(hero);
  const statusLabel = lifestyleMomentsCopy.statusBandLabel(hero.status_band);
  const flourishing = hero.status_band === "FLOURISHING";

  return (
    <section style={personalGlowWrapperStyle(tokens)}>
      <div style={{ ...personalGlassCardStyle(tokens), borderRadius: 24, padding: 16 }}>
        <LifestyleSectionBadge index={1} label="Journey Hero" accent explainerId="MOMENT-001" />

        <div className="mb-6 flex flex-col items-center text-center">
          <span className="mb-2 text-xs uppercase tracking-widest opacity-60">{lifestyleMomentsCopy.journeyHeroTitle}</span>
          <h2 className="mb-1 text-5xl font-bold">{hero.journey_score}</h2>
          <span className="text-lg font-semibold tracking-wide" style={{ color: flourishing ? "#10b981" : colors.brandPrimary }}>
            {statusLabel}
          </span>
          <div className="mt-4 w-full max-w-[240px] space-y-1.5">
            <div className="flex justify-between text-[8px] uppercase tracking-tighter opacity-60">
              {hero.phases.map((phase) => (
                <span key={phase.phase_id} style={{ color: phase.is_active ? "#10b981" : undefined, opacity: phase.is_active ? 1 : 0.6 }}>
                  {phase.label}
                </span>
              ))}
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.1)" }}>
              <div
                className="h-full rounded-full"
                style={{
                  width: `${progress}%`,
                  background: flourishing ? "#10b981" : colors.brandPrimary,
                  boxShadow: flourishing ? "0 0 8px rgba(16,185,129,0.5)" : undefined,
                }}
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-center sm:grid-cols-4">
          {[
            { value: hero.experience_count, label: lifestyleMomentsCopy.statExperiences },
            { value: hero.discovery_count, label: lifestyleMomentsCopy.statDiscoveries },
            { value: hero.creative_session_count, label: lifestyleMomentsCopy.statCreative },
            { value: lifestyleMomentsCopy.formatInrMinor(hero.lifestyle_spend_minor), label: lifestyleMomentsCopy.statSpend },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-lg font-bold sm:text-xl">{stat.value}</div>
              <div className="text-[8px] uppercase tracking-tighter opacity-60 sm:text-[10px]">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

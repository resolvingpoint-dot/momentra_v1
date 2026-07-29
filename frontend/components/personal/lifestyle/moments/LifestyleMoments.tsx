"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalPulseContainerStyle, personalTypography, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleBestMomentsCarousel } from "@/components/personal/lifestyle/moments/widgets/LifestyleBestMomentsCarousel";
import { LifestyleJourneyHero } from "@/components/personal/lifestyle/moments/widgets/LifestyleJourneyHero";
import { LifestyleJourneyTimeline } from "@/components/personal/lifestyle/moments/widgets/LifestyleJourneyTimeline";
import { LifestyleSpendJourney } from "@/components/personal/lifestyle/moments/widgets/LifestyleSpendJourney";
import { LifestyleTurningPointsList } from "@/components/personal/lifestyle/moments/widgets/LifestyleTurningPointsList";
import type { PersonalLifestyleMomentDetail } from "@/lib/api/personalDomainTypes";
import { lifestyleMomentsCopy } from "@/lib/personal/lifestyle/moments/lifestyleMomentsCopy";

type LifestyleMomentsProps = {
  detail: PersonalLifestyleMomentDetail;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

export function LifestyleMoments({ detail, bottomPadding = 0, hideScreenHeader = false }: LifestyleMomentsProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = detail.metrics;

  if (!metrics?.journey_hero || !metrics.money_journey) {
    return <LifestyleMomentsSkeleton bottomPadding={bottomPadding} />;
  }

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <div style={personalPulseContainerStyle(tokens)}>
        {!hideScreenHeader ? (
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            {lifestyleMomentsCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>
            {lifestyleMomentsCopy.screenTitle}
          </h1>
        </header>
        ) : null}

        <LifestyleJourneyHero hero={metrics.journey_hero} />
        <LifestyleJourneyTimeline items={metrics.journey_timeline} />
        <LifestyleSpendJourney money={metrics.money_journey} />
        <LifestyleBestMomentsCarousel cards={metrics.best_moments} />
        <LifestyleTurningPointsList points={metrics.turning_points} />
      </div>
    </div>
  );
}

export function LifestyleMomentsSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="relative min-h-0 flex-1 overflow-y-auto bg-[#14121b]" style={{ paddingBottom: bottomPadding || 16 }}>
      <div className="flex min-h-0 flex-1 items-center justify-center px-6 py-8">
        <div className="w-full max-w-[1080px] space-y-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="mb-2 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-7 w-44 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-6">
            <div className="mb-4 h-10 w-24 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-4 h-20 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
            <div className="flex gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex flex-col items-center gap-1">
                  <div className="h-5 w-14 animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-3 w-10 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex gap-4 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="h-12 w-12 animate-pulse rounded-xl bg-[#2a2a2a]" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-40 animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-3 w-56 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              </div>
            ))}
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-4 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-3 h-40 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
            <div className="flex gap-4">
              <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="flex gap-4 overflow-hidden">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 w-60 shrink-0 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="mb-2 h-4 w-32 animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-3 w-20 animate-pulse rounded bg-[#2a2a2a]" />
              </div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="mb-2 h-4 w-44 animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-3 w-64 animate-pulse rounded bg-[#2a2a2a]" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

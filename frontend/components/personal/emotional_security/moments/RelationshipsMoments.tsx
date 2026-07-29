"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalPulseContainerStyle, personalTypography, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import { RelationshipBestMomentsCarousel } from "@/components/personal/emotional_security/moments/widgets/RelationshipBestMomentsCarousel";
import { RelationshipJourneyHero } from "@/components/personal/emotional_security/moments/widgets/RelationshipJourneyHero";
import { RelationshipJourneyTimeline } from "@/components/personal/emotional_security/moments/widgets/RelationshipJourneyTimeline";
import { RelationshipMoneyJourneyChart } from "@/components/personal/emotional_security/moments/widgets/RelationshipMoneyJourneyChart";
import { RelationshipTurningPointsCarousel } from "@/components/personal/emotional_security/moments/widgets/RelationshipTurningPointsCarousel";
import type { PersonalEmotionalSecurityMomentDetail } from "@/lib/api/personalDomainTypes";
import { relationshipsMomentsCopy } from "@/lib/personal/emotional_security/moments/relationshipsMomentsCopy";

type RelationshipsMomentsProps = {
  detail: PersonalEmotionalSecurityMomentDetail;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

export function RelationshipsMoments({ detail, bottomPadding = 0, hideScreenHeader = false }: RelationshipsMomentsProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = detail.metrics;

  if (!metrics) {
    return (
      <div className="relative flex min-h-0 flex-1 items-center justify-center" style={scrollShellStyle(tokens, bottomPadding)}>
        <PersonalAtmosphericOrbs />
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Loading your moments…</p>
      </div>
    );
  }

  return (
    <div data-momentra-context="personal" className="relative min-h-0 flex-1 overflow-y-auto" style={scrollShellStyle(tokens, bottomPadding)}>
      <PersonalAtmosphericOrbs />
      <div style={{ ...personalPulseContainerStyle(tokens), gap: 24 }}>
        {!hideScreenHeader ? (
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            {relationshipsMomentsCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>
            {relationshipsMomentsCopy.screenTitle}
          </h1>
        </header>
        ) : null}
        <RelationshipJourneyHero hero={metrics.journey_hero} />
        <RelationshipJourneyTimeline items={metrics.journey_timeline} />
        <RelationshipMoneyJourneyChart money={metrics.money_journey} />
        <RelationshipBestMomentsCarousel cards={metrics.best_moments} />
        <RelationshipTurningPointsCarousel points={metrics.turning_points} />
      </div>
    </div>
  );
}

export function RelationshipsMomentsSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="relative min-h-0 flex-1 overflow-y-auto bg-[#0a0b1e]" style={{ paddingBottom: bottomPadding || 16 }}>
      <div className="flex min-h-0 flex-1 items-center justify-center px-6 py-8">
        <div className="w-full max-w-[1080px] space-y-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="mb-2 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-7 w-44 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-6">
            <div className="mb-4 h-12 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-24 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
          </div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex gap-4 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="h-10 w-10 animate-pulse rounded-full bg-[#2a2a2a]" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-32 animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-3 w-24 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              </div>
            ))}
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-4 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-32 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
                <div className="mb-3 h-4 w-24 animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-20 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
                <div className="h-16 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

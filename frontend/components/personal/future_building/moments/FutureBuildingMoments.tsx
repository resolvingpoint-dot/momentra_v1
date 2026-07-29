"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import {
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { FbBestMomentsCarousel } from "@/components/personal/future_building/moments/widgets/FbBestMomentsCarousel";
import { FbJourneyHero } from "@/components/personal/future_building/moments/widgets/FbJourneyHero";
import { FbJourneyTimeline } from "@/components/personal/future_building/moments/widgets/FbJourneyTimeline";
import { FbMoneyJourneyChart } from "@/components/personal/future_building/moments/widgets/FbMoneyJourneyChart";
import { FbTurningPointsList } from "@/components/personal/future_building/moments/widgets/FbTurningPointsList";
import type { PersonalFutureBuildingMomentDetail } from "@/lib/api/personalDomainTypes";
import { fbMomentsCopy } from "@/lib/personal/future_building/moments/fbMomentsCopy";

type FutureBuildingMomentsProps = {
  detail: PersonalFutureBuildingMomentDetail;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

export function FutureBuildingMoments({ detail, bottomPadding = 0, hideScreenHeader = false }: FutureBuildingMomentsProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = detail.metrics;

  if (!metrics?.journey_hero || !metrics.money_journey) {
    return <FutureBuildingMomentsSkeleton bottomPadding={bottomPadding} />;
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
            {fbMomentsCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>{fbMomentsCopy.screenTitle}</h1>
        </header>
        ) : null}

        <FbJourneyHero hero={metrics.journey_hero} />
        <FbJourneyTimeline items={metrics.journey_timeline} />
        <FbMoneyJourneyChart money={metrics.money_journey} />
        <FbBestMomentsCarousel cards={metrics.best_moments} />
        <FbTurningPointsList points={metrics.turning_points} />
      </div>
    </div>
  );
}

export function FutureBuildingMomentsSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="relative min-h-0 flex-1 overflow-y-auto bg-[#05071a]" style={{ paddingBottom: bottomPadding || 16 }}>
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

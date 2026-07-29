"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import {
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { FbAiInsightSection } from "@/components/personal/future_building/pulse/widgets/FbAiInsightSection";
import { FbFinancialMomentum } from "@/components/personal/future_building/pulse/widgets/FbFinancialMomentum";
import { FbOpportunityCard } from "@/components/personal/future_building/pulse/widgets/FbOpportunityCard";
import { FbPulseHero } from "@/components/personal/future_building/pulse/widgets/FbPulseHero";
import { FbPulseSummaryBar } from "@/components/personal/future_building/pulse/widgets/FbPulseSummaryBar";
import { FbQuickAddGrid } from "@/components/personal/future_building/pulse/widgets/FbQuickAddGrid";
import { FbRecentActivityFeed } from "@/components/personal/future_building/pulse/widgets/FbRecentActivityFeed";
import { FbScoreDriverGrid } from "@/components/personal/future_building/pulse/widgets/FbScoreDriverGrid";
import { FbSignalPills } from "@/components/personal/future_building/pulse/widgets/FbSignalPills";
import { FbStateSnapshot } from "@/components/personal/future_building/pulse/widgets/FbStateSnapshot";
import { FbTrendLineChart } from "@/components/personal/future_building/pulse/widgets/FbTrendLineChart";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";
import type { PersonalFutureBuildingPulse } from "@/lib/api/personalDomainTypes";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";

const MOMENT_TYPE = "FUTURE_BUILDING";

type FutureBuildingPulseProps = {
  pulse: PersonalFutureBuildingPulse;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
  onQuickAdd?: (action: string) => void;
  onViewAllActivity?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
};

export function FutureBuildingPulse({ pulse, bottomPadding = 0, hideScreenHeader = false, onQuickAdd, onViewAllActivity, onEditActivity }: FutureBuildingPulseProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = pulse.metrics;

  if (!metrics) {
    return <FutureBuildingPulseSkeleton bottomPadding={bottomPadding} />;
  }

  const totalMinor =
    (metrics.financial_segments ?? []).reduce((s, seg) => s + seg.amount_minor, 0) ||
    metrics.capacity_stats?.investments_minor ||
    0;

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
            {fbPulseCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>{fbPulseCopy.screenTitle}</h1>
        </header>
        ) : null}

        <FbPulseHero metrics={metrics} />
        <FbPulseSummaryBar signals={metrics.signals} />
        <FbRecentActivityFeed items={metrics.recent_activity} onViewAll={onViewAllActivity} onEditActivity={onEditActivity} />
        <FbFinancialMomentum segments={metrics.financial_segments} fallbackTotalMinor={totalMinor} />
        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 24, padding: 20 }}>
          <PersonalWidgetSectionHeader
            title={fbPulseCopy.trendsTitle}
            explainerId="PULSE-007"
            momentTypeCode={MOMENT_TYPE}
            className="mb-4"
          />
          <FbTrendLineChart
            learning={metrics.trends_30d?.learning}
            execution={metrics.trends_30d?.execution}
            progress={metrics.trends_30d?.progress}
          />
        </section>
        <FbScoreDriverGrid drivers={metrics.score_drivers} />
        <FbStateSnapshot gauges={metrics.gauges} />
        <FbOpportunityCard opportunity={metrics.opportunity} onQuickAdd={onQuickAdd} />
        <FbSignalPills signals={metrics.signals} />
        <FbAiInsightSection insightText={metrics.intelligence.insight_text} confidencePercent={metrics.intelligence.confidence_percent} />
        <FbQuickAddGrid onQuickAdd={onQuickAdd} />
      </div>
    </div>
  );
}

export function FutureBuildingPulseSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
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
            <div className="mb-4 h-20 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
            <div className="grid grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex flex-col items-center gap-1">
                  <div className="h-8 w-16 animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-3 w-12 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="flex gap-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-5 flex-1 animate-pulse rounded-full bg-[#2a2a2a]" />
            ))}
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
            <div className="mb-3 h-32 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
            <div className="flex gap-4">
              <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-4 h-5 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-3 h-24 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
            <div className="flex gap-4">
              <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
              <div className="mb-2 h-3 w-20 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="space-y-2">
                {[...Array(3)].map((_, j) => (
                  <div key={j} className="flex items-center gap-2">
                    <div className="h-4 flex-1 animate-pulse rounded bg-[#2a2a2a]" />
                    <div className="h-4 w-12 animate-pulse rounded bg-[#2a2a2a]" />
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
              <div className="mb-2 h-3 w-20 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="flex justify-between">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="flex flex-col items-center gap-1">
                    <div className="h-12 w-12 animate-pulse rounded-full bg-[#2a2a2a]" />
                    <div className="h-3 w-10 animate-pulse rounded bg-[#2a2a2a]" />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-3 w-28 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-2 h-6 w-48 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-4 h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-12 w-32 animate-pulse rounded-2xl bg-[#2a2a2a]" />
          </div>
          <div className="flex gap-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-5 flex-1 animate-pulse rounded-full bg-[#2a2a2a]" />
            ))}
          </div>
          <div className="flex gap-4 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="h-7 w-7 animate-pulse rounded-full bg-[#2a2a2a]" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-36 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-12 animate-pulse rounded-full bg-[#2a2a2a]" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

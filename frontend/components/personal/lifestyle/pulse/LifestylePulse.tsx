"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalPulseContainerStyle, personalTypography, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleActivityFeedGrid } from "@/components/personal/lifestyle/pulse/widgets/LifestyleActivityFeedGrid";
import { LifestyleDriversAndGauges } from "@/components/personal/lifestyle/pulse/widgets/LifestyleDriversAndGauges";
import { LifestyleFinancialPulse } from "@/components/personal/lifestyle/pulse/widgets/LifestyleFinancialPulse";
import { LifestyleIntelligenceCard } from "@/components/personal/lifestyle/pulse/widgets/LifestyleIntelligenceCard";
import { LifestyleOpportunityCard } from "@/components/personal/lifestyle/pulse/widgets/LifestyleOpportunityCard";
import { LifestyleQuickLauncher } from "@/components/personal/lifestyle/pulse/widgets/LifestyleQuickLauncher";
import { LifestyleSignalBar } from "@/components/personal/lifestyle/pulse/widgets/LifestyleSignalBar";
import { LifestyleSignalPills } from "@/components/personal/lifestyle/pulse/widgets/LifestyleSignalPills";
import { LifestyleTrendsChart } from "@/components/personal/lifestyle/pulse/widgets/LifestyleTrendsChart";
import { LifestyleVitalityHero } from "@/components/personal/lifestyle/pulse/widgets/LifestyleVitalityHero";
import type { PersonalLifestylePulse } from "@/lib/api/personalDomainTypes";

type LifestylePulseProps = {
  pulse: PersonalLifestylePulse;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
  onQuickAdd?: (action: string) => void;
  onViewAllActivity?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
};

export function LifestylePulse({ pulse, bottomPadding = 0, hideScreenHeader = false, onQuickAdd, onViewAllActivity, onEditActivity }: LifestylePulseProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = pulse.metrics;

  if (!metrics) {
    return <LifestylePulseSkeleton bottomPadding={bottomPadding} />;
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
            Personal / Pulse
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>Lifestyle</h1>
        </header>
        ) : null}

        <LifestyleVitalityHero metrics={metrics} />
        <LifestyleSignalBar signals={metrics.signals} />
        <LifestyleActivityFeedGrid
          items={pulse.dashboard_card?.recent_items ?? []}
          emptyMessage={pulse.dashboard_card?.empty_recent_message}
          onViewAll={onViewAllActivity}
          onEditActivity={onEditActivity}
        />
        <LifestyleFinancialPulse segments={metrics.financial_segments} totalSpendMinor={metrics.capacity.lifestyle_spend_minor} />
        <LifestyleTrendsChart trends={metrics.trends_30d} />
        <LifestyleDriversAndGauges drivers={metrics.score_drivers} gauges={metrics.gauges} />
        <LifestyleOpportunityCard opportunity={metrics.opportunity} onCta={() => onQuickAdd?.("LIFESTYLE_EXPENSE")} />
        <LifestyleSignalPills metrics={metrics} />
        <LifestyleIntelligenceCard intelligence={metrics.intelligence} />
        <LifestyleQuickLauncher onQuickAdd={onQuickAdd} />
      </div>
    </div>
  );
}

export function LifestylePulseSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="relative min-h-0 flex-1 overflow-y-auto bg-[#14121b]" style={{ paddingBottom: bottomPadding || 16 }}>
      <div className="flex min-h-0 flex-1 items-center justify-center px-6 py-8">
        <div className="w-full max-w-[1080px] space-y-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="mb-2 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-7 w-44 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
            <div className="flex items-center gap-3">
              <div className="h-8 w-20 animate-pulse rounded-full bg-[#2a2a2a]" />
              <div className="h-8 w-8 animate-pulse rounded-full bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-6">
            <div className="mb-4 h-12 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-4 h-24 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
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
              <div key={i} className="h-6 flex-1 animate-pulse rounded-full bg-[#2a2a2a]" />
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
            <div className="h-28 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
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
              <div key={i} className="h-6 flex-1 animate-pulse rounded-full bg-[#2a2a2a]" />
            ))}
          </div>
          <div className="flex gap-4 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="h-7 w-7 animate-pulse rounded-full bg-[#2a2a2a]" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-28 animate-pulse rounded bg-[#2a2a2a]" />
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

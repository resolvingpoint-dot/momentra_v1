"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import {
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { FbAiInterpretationSection } from "@/components/personal/future_building/memory/widgets/FbAiInterpretationSection";
import { FbBehavioralPatternsSection } from "@/components/personal/future_building/memory/widgets/FbBehavioralPatternsSection";
import { FbCorePatternSection } from "@/components/personal/future_building/memory/widgets/FbCorePatternSection";
import { FbDriversGrid } from "@/components/personal/future_building/memory/widgets/FbDriversGrid";
import { FbEmotionalDnaSection } from "@/components/personal/future_building/memory/widgets/FbEmotionalDnaSection";
import { FbEvolutionTimelineSection } from "@/components/personal/future_building/memory/widgets/FbEvolutionTimelineSection";
import { FbGrowthEdgeSection } from "@/components/personal/future_building/memory/widgets/FbGrowthEdgeSection";
import { FbIdentitySnapshotSection } from "@/components/personal/future_building/memory/widgets/FbIdentitySnapshotSection";
import { FbReturnBehaviorsSection } from "@/components/personal/future_building/memory/widgets/FbReturnBehaviorsSection";
import type { PersonalFutureBuildingMemory } from "@/lib/api/personalDomainTypes";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";

type FutureBuildingMemoryProps = {
  memory: PersonalFutureBuildingMemory;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

export function FutureBuildingMemory({ memory, bottomPadding = 0, hideScreenHeader = false }: FutureBuildingMemoryProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = memory.metrics;

  if (!metrics) {
    return <FutureBuildingMemorySkeleton bottomPadding={bottomPadding} />;
  }

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <div style={{ ...personalPulseContainerStyle(tokens), gap: tokens.spacing.gutter }}>
        {!hideScreenHeader ? (
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            {fbMemoryCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>{fbMemoryCopy.screenTitle}</h1>
        </header>
        ) : null}

        <FbIdentitySnapshotSection snapshot={metrics.identity_snapshot} />
        <FbCorePatternSection pattern={metrics.core_pattern} />
        <FbDriversGrid bestDrivers={metrics.best_drivers} lowestDrivers={metrics.lowest_drivers} />
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <FbReturnBehaviorsSection behaviors={metrics.highest_return_behaviors} />
          </div>
          <div className="lg:col-span-2">
            {metrics.emotional_dna ? <FbEmotionalDnaSection dna={metrics.emotional_dna} /> : null}
          </div>
        </div>
        <FbBehavioralPatternsSection patterns={metrics.behavioral_patterns} />
        <FbEvolutionTimelineSection phases={metrics.evolution_timeline} />
        {metrics.ai_interpretation?.quote ? (
          <FbAiInterpretationSection quote={metrics.ai_interpretation.quote} />
        ) : null}
        {metrics.next_growth_edge ? <FbGrowthEdgeSection edge={metrics.next_growth_edge} /> : null}
      </div>
    </div>
  );
}

export function FutureBuildingMemorySkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
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
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-3 w-20 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-5 w-40 animate-pulse rounded bg-[#2a2a2a]" />
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-5 w-28 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-16 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
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
            ))}
          </div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
            <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5 lg:col-span-3">
              <div className="mb-2 h-3 w-24 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="space-y-2">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5 lg:col-span-2">
              <div className="mb-2 h-3 w-20 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="flex justify-between">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="flex flex-col items-center gap-1">
                    <div className="h-10 w-10 animate-pulse rounded-full bg-[#2a2a2a]" />
                    <div className="h-3 w-8 animate-pulse rounded bg-[#2a2a2a]" />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-2">
              {[...Array(3)].map((_, j) => (
                <div key={j} className="h-12 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-5 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-3">
              {[...Array(3)].map((_, j) => (
                <div key={j} className="flex items-start gap-3">
                  <div className="mt-1 h-3 w-3 animate-pulse rounded-full bg-[#2a2a2a]" />
                  <div className="h-10 flex-1 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="flex gap-4 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="h-7 w-7 animate-pulse rounded-full bg-[#2a2a2a]" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-28 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-5 w-24 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalPulseContainerStyle, personalTypography, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleAiInterpretation } from "@/components/personal/lifestyle/memory/widgets/LifestyleAiInterpretation";
import { LifestyleBehavioralPatterns } from "@/components/personal/lifestyle/memory/widgets/LifestyleBehavioralPatterns";
import { LifestyleCorePattern } from "@/components/personal/lifestyle/memory/widgets/LifestyleCorePattern";
import { LifestyleDriversCard } from "@/components/personal/lifestyle/memory/widgets/LifestyleDriversCard";
import { LifestyleEmotionalDna } from "@/components/personal/lifestyle/memory/widgets/LifestyleEmotionalDna";
import { LifestyleEvolutionTimeline } from "@/components/personal/lifestyle/memory/widgets/LifestyleEvolutionTimeline";
import { LifestyleGrowthEdge } from "@/components/personal/lifestyle/memory/widgets/LifestyleGrowthEdge";
import { LifestyleIdentitySnapshot } from "@/components/personal/lifestyle/memory/widgets/LifestyleIdentitySnapshot";
import { RoiAnalysisSection } from "@/components/personal/lifestyle/memory/widgets/RoiAnalysisSection";
import type { PersonalLifestyleMemoryMetrics } from "@/lib/api/personal";
import { lifestyleMemoryCopy } from "@/lib/personal/lifestyle/memory/lifestyleMemoryCopy";

type LifestyleMemoryProps = {
  metrics: PersonalLifestyleMemoryMetrics;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

export function LifestyleMemory({ metrics, bottomPadding = 0, hideScreenHeader = false }: LifestyleMemoryProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;

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
            {lifestyleMemoryCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>
            {lifestyleMemoryCopy.screenTitle}
          </h1>
        </header>
        ) : null}

        <LifestyleIdentitySnapshot snapshot={metrics.identity_snapshot} />
        <LifestyleCorePattern pattern={metrics.core_pattern} />
        <div className="grid grid-cols-1 sm:grid-cols-2" style={{ gap: tokens.spacing.gutter }}>
          <LifestyleDriversCard drivers={metrics.best_drivers} variant="best" />
          <LifestyleDriversCard drivers={metrics.lowest_drivers} variant="lowest" />
        </div>
        <div className="grid grid-cols-1 gap-4">
          {metrics.roi_analysis ? <RoiAnalysisSection roi={metrics.roi_analysis} /> : null}
          <LifestyleEmotionalDna dna={metrics.emotional_dna} />
        </div>
        <LifestyleBehavioralPatterns patterns={metrics.behavioral_patterns} />
        <LifestyleEvolutionTimeline phases={metrics.evolution_timeline} />
        <LifestyleAiInterpretation interpretation={metrics.ai_interpretation} />
        <LifestyleGrowthEdge edge={metrics.next_growth_edge} />
      </div>
    </div>
  );
}

export function LifestyleMemorySkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="relative min-h-0 flex-1 overflow-y-auto bg-[#14121b]" style={{ paddingBottom: bottomPadding || 16 }}>
      <div className="flex min-h-0 flex-1 items-center justify-center px-6 py-8">
        <div className="w-full max-w-[1080px] space-y-5">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="mb-2 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-7 w-44 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-3 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-2 h-5 w-48 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-4 w-64 animate-pulse rounded bg-[#2a2a2a]" />
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-3 w-28 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-12 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
          </div>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
                <div className="mb-2 h-3 w-24 animate-pulse rounded bg-[#2a2a2a]" />
                <div className="space-y-2">
                  <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-4 w-3/4 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              </div>
            ))}
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-3 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="flex gap-4">
              <div className="h-20 w-20 animate-pulse rounded-xl bg-[#2a2a2a]" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-4 w-3/4 animate-pulse rounded bg-[#2a2a2a]" />
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-3 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-2">
              {[...Array(2)].map((_, j) => (
                <div key={j} className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-3 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-3">
              {[...Array(2)].map((_, j) => (
                <div key={j} className="flex gap-3">
                  <div className="h-12 w-1 animate-pulse rounded-full bg-[#2a2a2a]" />
                  <div className="flex-1 space-y-1">
                    <div className="h-4 w-32 animate-pulse rounded bg-[#2a2a2a]" />
                    <div className="h-3 w-48 animate-pulse rounded bg-[#2a2a2a]" />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="flex gap-4">
              <div className="h-8 w-8 animate-pulse rounded-full bg-[#2a2a2a]" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-3 w-3/4 animate-pulse rounded bg-[#2a2a2a]" />
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-3 w-28 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalPulseContainerStyle, personalTypography, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import { AiInterpretationSection } from "@/components/personal/life_operations/memory/widgets/AiInterpretationSection";
import { BehavioralPatternsSection } from "@/components/personal/life_operations/memory/widgets/BehavioralPatternsSection";
import { CorePatternSection } from "@/components/personal/life_operations/memory/widgets/CorePatternSection";
import { DriversSection } from "@/components/personal/life_operations/memory/widgets/DriversSection";
import { EmotionalDnaSection } from "@/components/personal/life_operations/memory/widgets/EmotionalDnaSection";
import { EvolutionTimelineSection } from "@/components/personal/life_operations/memory/widgets/EvolutionTimelineSection";
import { GrowthEdgeSection } from "@/components/personal/life_operations/memory/widgets/GrowthEdgeSection";
import { IdentitySnapshotSection } from "@/components/personal/life_operations/memory/widgets/IdentitySnapshotSection";
import { RoiAnalysisSection } from "@/components/personal/lifestyle/memory/widgets/RoiAnalysisSection";
import type { PersonalEmotionalSecurityMemory } from "@/lib/api/personalDomainTypes";
import { relationshipsMemoryCopy } from "@/lib/personal/emotional_security/memory/relationshipsMemoryCopy";
import { resolvedMemoryRoiAnalysis } from "@/lib/personal/shared/memoryMetrics";

type RelationshipsMemoryProps = {
  memory: PersonalEmotionalSecurityMemory;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

export function RelationshipsMemory({ memory, bottomPadding = 0, hideScreenHeader = false }: RelationshipsMemoryProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = memory.metrics;
  const copy = relationshipsMemoryCopy;
  const roiAnalysis = resolvedMemoryRoiAnalysis(metrics);

  if (!metrics) {
    return (
      <div className="relative flex min-h-0 flex-1 items-center justify-center" style={scrollShellStyle(tokens, bottomPadding)}>
        <PersonalAtmosphericOrbs />
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Loading your memory…</p>
      </div>
    );
  }

  return (
    <div data-momentra-context="personal" className="relative min-h-0 flex-1 overflow-y-auto" style={scrollShellStyle(tokens, bottomPadding)}>
      <PersonalAtmosphericOrbs />
      <div style={{ ...personalPulseContainerStyle(tokens), gap: tokens.spacing.gutter }}>
        {!hideScreenHeader ? (
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>{copy.screenBreadcrumb}</p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>{copy.screenTitle}</h1>
        </header>
        ) : null}
        <IdentitySnapshotSection snapshot={metrics.identity_snapshot} copy={copy} momentTypeCode="RELATIONSHIPS" />
        <CorePatternSection pattern={metrics.core_pattern} copy={copy} momentTypeCode="RELATIONSHIPS" />
        <div className="grid grid-cols-1 sm:grid-cols-2" style={{ gap: tokens.spacing.gutter }}>
          <DriversSection drivers={metrics.best_drivers} variant="best" copy={copy} momentTypeCode="RELATIONSHIPS" />
          <DriversSection drivers={metrics.lowest_drivers} variant="lowest" copy={copy} momentTypeCode="RELATIONSHIPS" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-5" style={{ gap: tokens.spacing.gutter }}>
          <div className="sm:col-span-3">
            <RoiAnalysisSection roi={roiAnalysis} momentTypeCode="RELATIONSHIPS" />
          </div>
          <div className="sm:col-span-2">
            <EmotionalDnaSection dna={metrics.emotional_dna} copy={copy} momentTypeCode="RELATIONSHIPS" />
          </div>
        </div>
        <BehavioralPatternsSection patterns={metrics.behavioral_patterns} copy={copy} momentTypeCode="RELATIONSHIPS" />
        <EvolutionTimelineSection phases={metrics.evolution_timeline} copy={copy} momentTypeCode="RELATIONSHIPS" />
        <AiInterpretationSection interpretation={metrics.ai_interpretation} copy={copy} momentTypeCode="RELATIONSHIPS" />
        <GrowthEdgeSection edge={metrics.next_growth_edge} copy={copy} momentTypeCode="RELATIONSHIPS" />
      </div>
    </div>
  );
}

export function RelationshipsMemorySkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
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
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-5">
            <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5 sm:col-span-3">
              <div className="mb-2 h-3 w-24 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="space-y-2">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5 sm:col-span-2">
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

"use client";

import { useState } from "react";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import {
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { AiInterpretationSection } from "@/components/personal/life_operations/memory/widgets/AiInterpretationSection";
import { BehavioralPatternsSection } from "@/components/personal/life_operations/memory/widgets/BehavioralPatternsSection";
import { CorePatternSection } from "@/components/personal/life_operations/memory/widgets/CorePatternSection";
import { DriversSection } from "@/components/personal/life_operations/memory/widgets/DriversSection";
import { EmotionalDnaSection } from "@/components/personal/life_operations/memory/widgets/EmotionalDnaSection";
import { EvolutionTimelineSection } from "@/components/personal/life_operations/memory/widgets/EvolutionTimelineSection";
import { GrowthEdgeSection } from "@/components/personal/life_operations/memory/widgets/GrowthEdgeSection";
import { MotionStaggerRoot, MotionSection } from "@/components/shared/MotionStagger";
import { FloatingParticles } from "@/lib/motion/FloatingParticles";
import { IdentitySnapshotSection } from "@/components/personal/life_operations/memory/widgets/IdentitySnapshotSection";
import { ReturnBehaviorsSection } from "@/components/personal/life_operations/memory/widgets/ReturnBehaviorsSection";
import type { TemplateMemoryResponse } from "@/lib/api/personal";
import { lifeOpsMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";

type LifeOperationsMemoryProps = {
  data: TemplateMemoryResponse;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

export function LifeOperationsMemory({ data, bottomPadding = 0, hideScreenHeader = false }: LifeOperationsMemoryProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = data.memory_projection;
  const [search, setSearch] = useState("");

  if (!metrics) {
    return (
      <div
        className="flex min-h-0 flex-1 items-center justify-center px-6 text-center"
        style={{ paddingBottom: bottomPadding }}
      >
        <p className="text-sm opacity-70">Personal Intelligence is forming as you capture moments.</p>
      </div>
    );
  }

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <FloatingParticles density={1.2} className="-z-[5]" color={`${colors.brandPrimary}66`} />
      <div style={{ ...personalPulseContainerStyle(tokens), gap: tokens.spacing.gutter }}>
        <MotionStaggerRoot>
        <MotionSection>
        {!hideScreenHeader ? (
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            {lifeOpsMemoryCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>
            {lifeOpsMemoryCopy.screenTitle}
          </h1>
        </header>
        ) : null}
        </MotionSection>

        <MotionSection>
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search patterns and insights…"
          aria-label="Search memory"
          className="w-full rounded-xl border bg-transparent px-4 py-2.5 text-sm outline-none"
          style={{ borderColor: colors.border, color: colors.textPrimary }}
        />
        </MotionSection>

        {(!search || metrics.identity_snapshot.title.toLowerCase().includes(search.toLowerCase())) ? (
        <MotionSection><IdentitySnapshotSection snapshot={metrics.identity_snapshot} /></MotionSection>
        ) : null}
        <MotionSection><CorePatternSection pattern={metrics.core_pattern} /></MotionSection>
        <MotionSection>
        <div className="grid grid-cols-1 sm:grid-cols-2" style={{ gap: tokens.spacing.gutter }}>
          <DriversSection drivers={metrics.best_drivers} variant="best" />
          <DriversSection drivers={metrics.lowest_drivers} variant="lowest" />
        </div>
        </MotionSection>
        <MotionSection>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <ReturnBehaviorsSection behaviors={metrics.highest_return_behaviors} />
          <EmotionalDnaSection dna={metrics.emotional_dna} />
        </div>
        </MotionSection>
        {metrics.behavioral_patterns.length > 0 &&
        (!search ||
          metrics.behavioral_patterns.some((p) => p.title.toLowerCase().includes(search.toLowerCase()))) ? (
          <MotionSection><BehavioralPatternsSection patterns={metrics.behavioral_patterns} /></MotionSection>
        ) : null}
        <MotionSection><EvolutionTimelineSection phases={metrics.evolution_timeline} /></MotionSection>
        <MotionSection><AiInterpretationSection interpretation={metrics.ai_interpretation} /></MotionSection>
        <MotionSection><GrowthEdgeSection edge={metrics.next_growth_edge} /></MotionSection>
        </MotionStaggerRoot>
      </div>
    </div>
  );
}

export function LifeOperationsMemorySkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="min-h-0 flex-1 p-6" style={{ paddingBottom: bottomPadding }}>
      <div className="mx-auto max-w-[1080px] space-y-4">
        <div className="h-7 w-44 animate-pulse rounded bg-[#2a2a2a]" />
        <div className="h-28 animate-pulse rounded-2xl bg-[#2a2a2a]" />
        <div className="h-28 animate-pulse rounded-2xl bg-[#2a2a2a]" />
      </div>
    </div>
  );
}

export function LifeOperationsMemoryEmpty({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div
      className="flex min-h-0 flex-1 items-center justify-center px-6 text-center"
      style={{ paddingBottom: bottomPadding }}
    >
      <p className="text-sm opacity-70">Not enough data for memories yet.</p>
    </div>
  );
}

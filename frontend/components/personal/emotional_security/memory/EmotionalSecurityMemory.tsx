"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  DomainGlassSection,
  DomainMemoryConfidence,
  DomainMemoryEvolution,
  DomainMemoryHeader,
  DomainMemoryPatterns,
  DomainMemoryShell,
  DomainMemorySynthesis,
  DomainProgressGlow,
  DomainSectionHeader,
} from "@/components/personal/shared/domain/DomainScreens";
import type { PersonalEmotionalSecurityMemory } from "@/lib/api/personalDomainTypes";

export function EmotionalSecurityMemory({
  memory,
  bottomPadding = 0,
}: {
  memory: PersonalEmotionalSecurityMemory;
  bottomPadding?: number;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <DomainMemoryShell bottomPadding={bottomPadding}>
      <DomainMemoryHeader sectionLabel={memory.section_label} statusLabel={memory.status_label} />
      <DomainMemorySynthesis
        synthesisTitle={memory.synthesis_title}
        synthesisBody={memory.synthesis_body}
        systemState={memory.system_state}
        daysAnalyzed={memory.days_analyzed}
      />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <DomainGlassSection>
          <p className="text-xs uppercase opacity-70" style={{ color: colors.textSecondary }}>
            Identity
          </p>
          <p className="mt-2 text-sm font-medium">{memory.identity_label}</p>
        </DomainGlassSection>
        <DomainGlassSection>
          <p className="text-xs uppercase opacity-70" style={{ color: colors.textSecondary }}>
            Focus
          </p>
          <p className="mt-2 text-sm font-medium">{memory.focus_label}</p>
        </DomainGlassSection>
      </div>
      <DomainMemoryConfidence
        confidenceTitle={memory.confidence_title}
        confidencePercent={memory.confidence_percent}
        confidenceBody={memory.confidence_body}
      />
      <DomainGlassSection>
        <div className="flex justify-between">
          <h4 className="text-base font-semibold">{memory.focus_title}</h4>
          <span className="text-2xl font-bold" style={{ color: colors.brandTertiary }}>
            {memory.focus_percent}%
          </span>
        </div>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          {memory.focus_body}
        </p>
      </DomainGlassSection>
      <DomainGlassSection>
        <h4 className="text-base font-semibold">{memory.breakthrough_title}</h4>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          {memory.breakthrough_body}
        </p>
        {memory.breakthrough_active ? (
          <p className="mt-2 text-sm font-medium" style={{ color: colors.brandPrimary }}>
            Active
          </p>
        ) : null}
      </DomainGlassSection>
      <DomainGlassSection>
        <h4 className="text-base font-semibold">{memory.neural_growth_title}</h4>
        <p className="mt-1 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          {memory.neural_growth_subtitle}
        </p>
      </DomainGlassSection>
      <DomainMemoryPatterns patterns={memory.identified_patterns} />
      <DomainMemoryEvolution points={memory.confidence_evolution} />
      {memory.focus_optimization_percent != null ? (
        <DomainGlassSection>
          <DomainSectionHeader title="Focus Optimization" />
          <p className="mt-2 text-2xl font-bold" style={{ color: colors.brandTertiary }}>
            {memory.focus_optimization_percent}%
          </p>
          <DomainProgressGlow percent={memory.focus_optimization_percent} />
        </DomainGlassSection>
      ) : null}
    </DomainMemoryShell>
  );
}

export function EmotionalSecurityMemorySkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
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
            <div className="mb-2 h-5 w-40 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-12 w-full animate-pulse rounded bg-[#2a2a2a]" />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="mb-2 h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-5 w-32 animate-pulse rounded bg-[#2a2a2a]" />
              </div>
            ))}
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-3 h-12 w-full animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-4 w-48 animate-pulse rounded bg-[#2a2a2a]" />
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 flex items-center justify-between">
              <div className="h-5 w-32 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-8 w-16 animate-pulse rounded bg-[#2a2a2a]" />
            </div>
            <div className="h-8 w-full animate-pulse rounded bg-[#2a2a2a]" />
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-12 w-full animate-pulse rounded bg-[#2a2a2a]" />
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-5 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-6 w-full animate-pulse rounded bg-[#2a2a2a]" />
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-2">
              {[...Array(4)].map((_, j) => (
                <div key={j} className="flex items-center gap-2">
                  <div className="h-3 w-3 animate-pulse rounded-full bg-[#2a2a2a]" />
                  <div className="h-4 flex-1 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-5 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-3">
              {[...Array(4)].map((_, j) => (
                <div key={j} className="flex items-start gap-3">
                  <div className="mt-1 h-3 w-3 animate-pulse rounded-full bg-[#2a2a2a]" />
                  <div className="h-8 flex-1 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-2 h-5 w-36 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-2 h-8 w-16 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
          </div>
        </div>
      </div>
    </div>
  );
}

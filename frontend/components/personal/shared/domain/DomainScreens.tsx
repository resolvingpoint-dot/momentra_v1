"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import {
  DomainGlassSection,
  DomainInsightCard,
  DomainKvRow,
  DomainProgressGlow,
  DomainSectionHeader,
} from "@/components/personal/shared/domain/DomainWidgets";
import type { PersonalDomainActivityTimeline, PersonalDomainRuntimeTile } from "@/lib/api/personalDomainTypes";

export function DomainMemoryShell({
  children,
  bottomPadding,
}: {
  children: ReactNode;
  bottomPadding: number;
}) {
  const tokens = useThemeTokens();
  return (
    <div
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <div className="relative mx-auto w-full max-w-[1080px] space-y-5 px-5 py-6 md:px-20">
        {children}
      </div>
    </div>
  );
}

export function DomainMemoryHeader({
  sectionLabel,
  statusLabel,
}: {
  sectionLabel: string;
  statusLabel: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs font-bold uppercase tracking-widest" style={{ color: colors.brandTertiary }}>
        {sectionLabel}
      </span>
      <span
        className="rounded-full px-2.5 py-1 text-[10px] font-bold"
        style={{
          color: colors.brandPrimary,
          background: `color-mix(in srgb, ${colors.brandPrimary} 12%, transparent)`,
        }}
      >
        {statusLabel}
      </span>
    </div>
  );
}

export function DomainMemorySynthesis({
  synthesisTitle,
  synthesisBody,
  systemState,
  daysAnalyzed,
}: {
  synthesisTitle: string;
  synthesisBody: string;
  systemState: string;
  daysAnalyzed: number;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <DomainGlassSection>
      <h3 className="text-lg font-semibold">{synthesisTitle}</h3>
      <p className="mt-2 text-sm leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
        {synthesisBody}
      </p>
      <div className="mt-4 flex justify-between text-sm">
        <span style={{ color: colors.brandPrimary }}>{systemState}</span>
        <span className="opacity-70" style={{ color: colors.textSecondary }}>
          {daysAnalyzed} days analyzed
        </span>
      </div>
    </DomainGlassSection>
  );
}

export function DomainMemoryConfidence({
  confidenceTitle,
  confidencePercent,
  confidenceBody,
}: {
  confidenceTitle: string;
  confidencePercent: number;
  confidenceBody: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <DomainGlassSection>
      <div className="flex items-center justify-between">
        <h4 className="text-base font-semibold">{confidenceTitle}</h4>
        <span className="text-2xl font-bold" style={{ color: colors.brandPrimary }}>
          {confidencePercent}%
        </span>
      </div>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full" style={{ background: colors.surfaceContainer }}>
        <div
          className="h-full rounded-full"
          style={{ width: `${confidencePercent}%`, background: colors.brandPrimary }}
        />
      </div>
      <p className="mt-3 text-sm opacity-80" style={{ color: colors.textSecondary }}>
        {confidenceBody}
      </p>
    </DomainGlassSection>
  );
}

export function DomainMemoryPatterns({
  patterns,
}: {
  patterns: Array<{ name: string; confidence_percent: number }>;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  if (patterns.length === 0) return null;
  return (
    <DomainGlassSection>
      <DomainSectionHeader title="Identified Patterns" />
      <div className="mt-3 space-y-2">
        {patterns.map((pattern) => (
          <div key={pattern.name} className="flex justify-between text-sm">
            <span>{pattern.name}</span>
            <span style={{ color: colors.brandPrimary }}>{pattern.confidence_percent}%</span>
          </div>
        ))}
      </div>
    </DomainGlassSection>
  );
}

export function DomainMemoryEvolution({
  points,
}: {
  points: Array<{ month: string; value: number }>;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  if (points.length === 0) return null;
  return (
    <DomainGlassSection>
      <DomainSectionHeader title="Confidence Evolution" />
      <div className="mt-4 flex items-end justify-evenly gap-2">
        {points.map((point) => (
          <div key={point.month} className="flex flex-col items-center">
            <div
              className="w-6 rounded-t"
              style={{
                height: Math.max(4, point.value * 0.8),
                background: `color-mix(in srgb, ${colors.brandPrimary} 70%, transparent)`,
              }}
            />
            <span className="mt-1 text-[10px] opacity-70">{point.month}</span>
          </div>
        ))}
      </div>
    </DomainGlassSection>
  );
}

export function DomainRuntimeTiles({ tiles }: { tiles: PersonalDomainRuntimeTile[] }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const rows: PersonalDomainRuntimeTile[][] = [];
  for (let i = 0; i < tiles.length; i += 2) {
    rows.push(tiles.slice(i, i + 2));
  }
  return (
    <>
      {rows.map((row) => (
        <div key={row.map((t) => t.label).join("-")} className="grid grid-cols-2 gap-3">
          {row.map((tile) => (
            <DomainGlassSection key={tile.label}>
              <p className="text-[10px] font-bold uppercase tracking-widest opacity-70" style={{ color: colors.textSecondary }}>
                {tile.label}
              </p>
              <p className="mt-2 text-sm font-medium">{tile.value}</p>
            </DomainGlassSection>
          ))}
        </div>
      ))}
    </>
  );
}

export function DomainActivityTimeline({ timeline }: { timeline: PersonalDomainActivityTimeline }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return timeline.items.filter((item) => {
      const matchesFilter = filter === "ALL" || item.event_type === filter;
      const matchesSearch =
        query.length === 0 ||
        item.detail_line.toLowerCase().includes(query) ||
        item.category_label.toLowerCase().includes(query);
      return matchesFilter && matchesSearch;
    });
  }, [filter, search, timeline.items]);

  return (
    <DomainGlassSection>
      <h4 className="text-base font-semibold">{timeline.section_title}</h4>
      <div className="mt-3 flex flex-wrap gap-2">
        {timeline.filter_chips.map((chip) => (
          <button
            key={chip.id}
            type="button"
            onClick={() => setFilter(chip.id)}
            className="rounded-full px-3 py-1.5 text-xs font-medium"
            style={{
              color: filter === chip.id ? colors.brandOnPrimary : colors.textSecondary,
              background: filter === chip.id ? colors.brandPrimary : colors.surfaceHigh,
            }}
          >
            {chip.label}
          </button>
        ))}
      </div>
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder={timeline.search_placeholder}
        className="mt-3 w-full rounded-xl border px-3 py-2 text-sm"
        style={{
          borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
          background: colors.surfaceContainer,
          color: colors.textPrimary,
        }}
      />
      <div className="mt-4 space-y-3">
        {filtered.length === 0 ? (
          <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
            {timeline.empty_message ?? "No activities match your filters."}
          </p>
        ) : (
          filtered.map((item) => (
            <div
              key={item.id}
              className="rounded-xl p-3"
              style={{ background: `color-mix(in srgb, ${colors.surfaceContainer} 60%, transparent)` }}
            >
              <div className="flex justify-between gap-2 text-xs opacity-70">
                <span>{item.category_label}</span>
                <span>{item.relative_time}</span>
              </div>
              <p className="mt-1 text-sm">{item.detail_line}</p>
            </div>
          ))
        )}
      </div>
    </DomainGlassSection>
  );
}

export function DomainProfileHero({
  identityLabel,
  percent,
  percentLabel,
  leftLabel,
  rightLabel,
  footerLabel,
}: {
  identityLabel: string;
  percent: number;
  percentLabel?: string;
  leftLabel: string;
  rightLabel: string;
  footerLabel: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <DomainGlassSection>
      <div className="text-center">
        <h3 className="text-xl font-bold">{identityLabel}</h3>
        <DomainProgressGlow percent={percent} />
        {percentLabel ? (
          <p className="text-xs opacity-70" style={{ color: colors.textSecondary }}>
            {percentLabel}
          </p>
        ) : null}
        <div className="mt-3 flex justify-between text-sm">
          <span style={{ color: colors.textSecondary }}>{leftLabel}</span>
          <span style={{ color: colors.brandPrimary }}>{rightLabel}</span>
        </div>
        <p className="mt-2 text-xs opacity-70" style={{ color: colors.textSecondary }}>
          {footerLabel}
        </p>
      </div>
    </DomainGlassSection>
  );
}

export { DomainInsightCard, DomainKvRow, DomainProgressGlow, DomainSectionHeader };
export { DomainGlassSection } from "@/components/personal/shared/domain/DomainWidgets";

"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import {
  neuralLineBackground,
  personalGlassCardStyle,
  personalGlowWrapperStyle,
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { PersonalPremiumGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { ArcGauge } from "@/components/personal/life_operations/pulse/widgets/ArcGauge";
import { DonutChart } from "@/components/personal/life_operations/pulse/widgets/DonutChart";
import { SegmentShareBar } from "@/components/personal/life_operations/pulse/widgets/SegmentShareBar";
import {
  PersonalWidgetSectionHeader,
  WidgetInfoButton,
} from "@/components/personal/shared/WidgetInfoButton";
import { RelationshipRadarChart } from "@/components/personal/emotional_security/pulse/widgets/RelationshipRadarChart";
import { RelationshipsRecentActivityList } from "@/components/personal/emotional_security/pulse/widgets/RelationshipsRecentActivityList";
import { RelationshipsTrendLineChart } from "@/components/personal/emotional_security/pulse/widgets/RelationshipsTrendLineChart";
import type { PersonalEmotionalSecurityPulse } from "@/lib/api/personalDomainTypes";
import { relationshipsPulseCopy } from "@/lib/personal/emotional_security/pulse/relationshipsPulseCopy";
import { SEGMENT_COLORS } from "@/lib/personal/life_operations/pulse/pulseIcons";
import { Brain, Link2, TrendingUp } from "lucide-react";

const MOMENT_TYPE = "RELATIONSHIPS";

type RelationshipsPulseProps = {
  pulse: PersonalEmotionalSecurityPulse;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
  onQuickAdd?: (action: string) => void;
  onViewAllActivity?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
};

function segmentLabel(seg: { category_id: string; category_name?: string | null }) {
  return seg.category_name?.trim() || seg.category_id.slice(0, 8);
}

export function RelationshipsPulse({ pulse, bottomPadding = 0, hideScreenHeader = false, onQuickAdd, onViewAllActivity, onEditActivity }: RelationshipsPulseProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const metrics = pulse.metrics;

  if (!metrics) {
    return (
      <div
        data-momentra-context="personal"
        className="relative flex min-h-0 flex-1 items-center justify-center"
        style={scrollShellStyle(tokens, bottomPadding)}
      >
        <PersonalAtmosphericOrbs />
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Loading your pulse…</p>
      </div>
    );
  }

  const heroInnerStyle = {
    ...personalGlassCardStyle(tokens),
    ...neuralLineBackground(),
    borderRadius: 24,
    padding: 16,
  };

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <div style={personalPulseContainerStyle(tokens)}>
        {!hideScreenHeader ? (
        <header className="mb-2">
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            {relationshipsPulseCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            {relationshipsPulseCopy.screenTitle}
          </h1>
        </header>
        ) : null}
        <section style={personalGlowWrapperStyle(tokens)}>
          <div style={heroInnerStyle}>
            <div className="mb-4 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-0.5">
                  <p style={{ fontSize: 48, fontWeight: 800, lineHeight: 1, color: colors.textPrimary }}>
                    {metrics.bond_index}
                    <span style={{ fontSize: 20, fontWeight: 500, opacity: 0.4 }}>
                      {relationshipsPulseCopy.bondIndexSuffix}
                    </span>
                  </p>
                  <WidgetInfoButton explainerId="PULSE-001" momentTypeCode={MOMENT_TYPE} />
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <span
                    className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase"
                    style={{ borderColor: `${colors.brandTertiary}44`, color: colors.brandTertiary, background: `${colors.brandTertiary}18` }}
                  >
                    <TrendingUp size={12} />
                    {relationshipsPulseCopy.statusBands[metrics.status_band] ?? metrics.status_band}
                  </span>
                  {metrics.bond_index_delta_month != null && metrics.bond_index_delta_month !== 0 ? (
                    <span className="text-[10px] font-bold uppercase tracking-widest opacity-60">
                      +{metrics.bond_index_delta_month} This Month
                    </span>
                  ) : null}
                </div>
              </div>
              <div className="text-right">
                <p className="text-[10px] font-bold uppercase tracking-widest opacity-40">
                  {relationshipsPulseCopy.networkStability}
                </p>
                <p className="flex items-center justify-end gap-1 text-sm font-bold" style={{ color: colors.brandPrimary }}>
                  <span className="size-1.5 animate-pulse rounded-full" style={{ background: colors.brandPrimary }} />
                  {metrics.network_stability_label}
                </p>
              </div>
            </div>
            <div className="mb-1 flex justify-end">
              <WidgetInfoButton explainerId="PULSE-002" momentTypeCode={MOMENT_TYPE} />
            </div>
            <RelationshipRadarChart bondIndex={metrics.bond_index} axes={metrics.radar_axes} />
            <div className="mt-4 grid grid-cols-2 gap-2 border-t pt-4 sm:grid-cols-4" style={{ borderColor: "rgba(255,255,255,0.05)" }}>
              <div className="col-span-2 flex items-center justify-center gap-0.5 sm:col-span-4">
                <p className="text-[8px] uppercase tracking-tighter opacity-50 sm:text-[10px]">Capacity</p>
                <WidgetInfoButton explainerId="PULSE-003" momentTypeCode={MOMENT_TYPE} />
              </div>
              {[
                { v: metrics.hero_stats.connections, l: relationshipsPulseCopy.statConnections },
                { v: metrics.hero_stats.support, l: relationshipsPulseCopy.statSupport },
                { v: metrics.hero_stats.experiences, l: relationshipsPulseCopy.statExperiences },
                { v: relationshipsPulseCopy.formatInrMinor(metrics.hero_stats.spend_minor), l: relationshipsPulseCopy.statSpend, accent: true },
              ].map((s) => (
                <div key={s.l} className="text-center">
                  <p className="text-sm font-bold sm:text-base" style={{ color: s.accent ? colors.brandPrimary : colors.textPrimary }}>{s.v}</p>
                  <p className="text-[8px] uppercase tracking-tighter opacity-50 sm:text-[10px]">{s.l}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="flex justify-between rounded-xl border px-3 py-2" style={{ ...personalGlassCardStyle(tokens), borderColor: "rgba(255,255,255,0.05)" }}>
          {metrics.signal_chips.map((chip, i) => (
            <span key={chip.signal_id} className="flex items-center gap-1 text-[10px] font-bold uppercase" style={{ color: chip.trend === "FLAT" ? colors.textSecondary : colors.brandTertiary }}>
              {chip.label} {relationshipsPulseCopy.trendArrow(chip.trend)}
              {i < metrics.signal_chips.length - 1 ? null : null}
            </span>
          ))}
        </section>

        <div className="grid grid-cols-2 gap-3">
          {[
            { label: relationshipsPulseCopy.summaryConnections, value: metrics.connection_count, icon: "groups" },
            { label: relationshipsPulseCopy.summarySpend, value: relationshipsPulseCopy.formatInrMinor(metrics.spend_minor), icon: "wallet" },
          ].map((tile) => (
            <div key={tile.label} style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }} className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest opacity-60">{tile.label}</p>
                <p className="text-2xl font-bold">{tile.value}</p>
              </div>
            </div>
          ))}
        </div>

        <RelationshipsRecentActivityList items={metrics.recent_activity} emptyMessage={relationshipsPulseCopy.recentActivityEmpty} onViewAll={onViewAllActivity} onEditActivity={onEditActivity} />

        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
          <PersonalWidgetSectionHeader title={relationshipsPulseCopy.financialTitle} explainerId="PULSE-006" momentTypeCode={MOMENT_TYPE} />
          <div className="mt-3 flex flex-col gap-3 sm:flex-row">
            <div className="mx-auto sm:mx-0">
              <DonutChart segments={metrics.financial_segments} fallbackTotalMinor={metrics.spend_minor} />
            </div>
            <div className="min-w-0 flex-1">
              {metrics.financial_segments.length > 0 ? (
                metrics.financial_segments.map((seg, i) => (
                  <div key={seg.category_id} className="mb-3">
                    <div className="flex items-center gap-2 text-xs">
                      <span className="size-2 rounded-full" style={{ background: SEGMENT_COLORS[i % SEGMENT_COLORS.length] }} />
                      <span className="flex-1 truncate uppercase">{segmentLabel(seg)}</span>
                      <span className="font-bold">{seg.share_percent}%</span>
                    </div>
                    <SegmentShareBar percent={seg.share_percent} color={SEGMENT_COLORS[i % SEGMENT_COLORS.length]} />
                  </div>
                ))
              ) : (
                <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>{relationshipsPulseCopy.financialEmptyHint}</p>
              )}
            </div>
          </div>
        </section>

        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
          <PersonalWidgetSectionHeader title={relationshipsPulseCopy.trendsTitle} explainerId="PULSE-007" momentTypeCode={MOMENT_TYPE} />
          <RelationshipsTrendLineChart
            trust={metrics.trends_30d?.trust ?? []}
            connection={metrics.trends_30d?.connection ?? []}
          />
        </section>

        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
          <PersonalWidgetSectionHeader title={relationshipsPulseCopy.gaugesTitle} explainerId="PULSE-008" momentTypeCode={MOMENT_TYPE} className="mb-3" />
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {metrics.gauges.map((g) => (
              <ArcGauge
                key={g.gauge_id}
                gaugeId={g.gauge_id}
                percent={g.percent}
                label={relationshipsPulseCopy.gaugeLabels[g.gauge_id] ?? g.gauge_id}
              />
            ))}
          </div>
        </section>

        <PersonalPremiumGlowSection
          tokens={tokens}
          cornerRadius={16}
          className="transition-transform hover:scale-[1.02] active:scale-95"
          innerStyle={{ borderColor: "rgba(108, 78, 242, 0.4)" }}
        >
          <div className="mb-2 flex items-center gap-0.5">
            <p className="text-[10px] font-bold uppercase tracking-widest opacity-70">{relationshipsPulseCopy.recommendationBadge}</p>
            <WidgetInfoButton explainerId="PULSE-009" momentTypeCode={MOMENT_TYPE} />
          </div>
          <h3 style={{ ...personalTypography.sectionHeader, fontSize: 20 }}>{metrics.opportunity.title}</h3>
          <p style={{ ...personalTypography.bodyMd, opacity: 0.8, marginTop: 8 }}>{metrics.opportunity.body}</p>
          <div className="mt-3 flex gap-2">
            {metrics.opportunity.impact_chips.map((chip) => (
              <span key={chip} className="text-xs font-bold opacity-70">{chip}</span>
            ))}
          </div>
          {onQuickAdd ? (
            <button
              type="button"
              className="mt-4 rounded-2xl px-6 py-3 text-[11px] font-black uppercase tracking-widest"
              style={{ background: colors.primaryContainer ?? colors.brandPrimary, color: colors.onPrimaryContainer ?? "#fff" }}
              onClick={() => onQuickAdd("CONNECTION")}
            >
              {metrics.opportunity.cta_label}
            </button>
          ) : null}
        </PersonalPremiumGlowSection>

        {metrics.analysis_signals.length > 0 ? (
          <section>
            <p className="mb-2 text-[10px] font-bold uppercase tracking-widest opacity-60">{relationshipsPulseCopy.signalsTitle}</p>
            <div className="flex flex-wrap gap-2">
            {metrics.analysis_signals.map((sig) => (
              <span
                key={sig.signal_id}
                className="inline-flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs font-semibold"
                style={{ borderColor: `${colors.brandPrimary}33`, background: `${colors.brandPrimary}11` }}
              >
                <TrendingUp size={14} /> {sig.label}
              </span>
            ))}
            </div>
          </section>
        ) : null}

        <PersonalPremiumGlowSection tokens={tokens} cornerRadius={16}>
          <div className="flex gap-4 p-5">
            <Brain size={28} style={{ color: colors.brandPrimary }} />
            <div className="min-w-0 flex-1">
              <div className="mb-1 flex items-center gap-0.5">
                <span className="font-bold uppercase tracking-wider opacity-70">{relationshipsPulseCopy.intelligenceTitle}</span>
                <WidgetInfoButton explainerId="PULSE-011" momentTypeCode={MOMENT_TYPE} />
              </div>
              <p style={{ ...personalTypography.bodyMd, lineHeight: 1.5 }}>
                {metrics.intelligence.body}
              </p>
            </div>
          </div>
        </PersonalPremiumGlowSection>

        <section>
          <div className="mb-3 flex items-center justify-center gap-0.5">
            <p className="text-center text-[10px] font-bold uppercase tracking-widest opacity-60">
              {relationshipsPulseCopy.quickCaptureTitle}
            </p>
            <WidgetInfoButton explainerId="PULSE-010" momentTypeCode={MOMENT_TYPE} />
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:justify-between sm:gap-2">
            {metrics.quick_capture_actions.map((action) => (
              <button
                key={action.action_code}
                type="button"
                className="flex flex-col items-center gap-1 rounded-full border py-3 text-[9px] font-bold uppercase sm:flex-1"
                style={{ borderColor: "rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.04)" }}
                onClick={() => onQuickAdd?.(action.action_code)}
              >
                <Link2 size={18} style={{ color: colors.brandPrimary }} />
                {action.label}
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export function RelationshipsPulseSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
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
          <div className="grid grid-cols-2 gap-3">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="mb-2 h-3 w-20 animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-8 w-16 animate-pulse rounded bg-[#2a2a2a]" />
              </div>
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
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex flex-col items-center gap-2 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="h-12 w-12 animate-pulse rounded-full bg-[#2a2a2a]" />
                <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
              </div>
            ))}
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-3 w-28 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-2 h-6 w-48 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-4 h-4 w-full animate-pulse rounded bg-[#2a2a2a]" />
            <div className="h-12 w-32 animate-pulse rounded-2xl bg-[#2a2a2a]" />
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

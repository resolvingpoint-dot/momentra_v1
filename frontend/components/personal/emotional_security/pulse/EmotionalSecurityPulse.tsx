"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import {
  personalPulseContainerStyle,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import {
  DomainGlassSection,
  DomainKvRow,
  DomainMetricTile,
  DomainSectionHeader,
} from "@/components/personal/shared/domain/DomainWidgets";
import { PulseDashboardCardView } from "@/components/personal/shared/domain/PulseDashboardCardView";
import type { PersonalEmotionalSecurityPulse } from "@/lib/api/personalDomainTypes";

type EmotionalSecurityPulseProps = {
  pulse: PersonalEmotionalSecurityPulse;
  bottomPadding?: number;
};

export function EmotionalSecurityPulse({ pulse, bottomPadding = 0 }: EmotionalSecurityPulseProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <div style={personalPulseContainerStyle(tokens)} className="relative space-y-5">
        {pulse.dashboard_card ? <PulseDashboardCardView card={pulse.dashboard_card} /> : null}

        <section className="space-y-3 py-2 text-center">
          <h2 className="text-2xl font-bold">{pulse.hero_title}</h2>
          <p className="text-sm opacity-80" style={{ color: colors.textSecondary }}>
            {pulse.hero_subtitle}
          </p>
        </section>

        <div className="grid grid-cols-2 gap-3">
          <DomainMetricTile
            sectionLabel={pulse.vitality_section_label}
            value={pulse.vitality_label}
            trend={pulse.vitality_trend}
            accent={colors.brandPrimary}
          />
          <DomainMetricTile
            sectionLabel={pulse.bond_rate_section_label}
            value={`${pulse.bond_rate_percent}${pulse.bond_rate_suffix}`}
            trend={pulse.focus_label}
            accent={colors.brandTertiary}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <DomainGlassSection>
            <p className="text-xs uppercase tracking-wide opacity-70" style={{ color: colors.textSecondary }}>
              Identity
            </p>
            <p className="mt-2 text-sm font-medium">{pulse.identity_label}</p>
          </DomainGlassSection>
          <DomainGlassSection>
            <p className="text-xs uppercase tracking-wide opacity-70" style={{ color: colors.textSecondary }}>
              Focus
            </p>
            <p className="mt-2 text-sm font-medium">{pulse.focus_label}</p>
          </DomainGlassSection>
        </div>

        <DomainGlassSection>
          <p className="text-xs font-bold uppercase tracking-widest" style={{ color: colors.brandTertiary }}>
            {pulse.connection_signals_title}
          </p>
          {pulse.connection_signals ? (
            <div className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <span style={{ color: colors.textSecondary }}>Captured</span>
                <span>{pulse.connection_signals.captured_count}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: colors.textSecondary }}>High bond</span>
                <span style={{ color: colors.brandTertiary }}>
                  {pulse.connection_signals.high_bond_count}
                </span>
              </div>
            </div>
          ) : null}
          <h3 className="mt-4 text-base font-semibold">{pulse.pattern_insight_title}</h3>
          <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
            {pulse.pattern_insight_body}
          </p>
        </DomainGlassSection>

        {pulse.breakthrough ? (
          <DomainGlassSection>
            <p className="text-base font-semibold" style={{ color: colors.brandPrimary }}>
              {pulse.breakthrough.label}
            </p>
            <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
              {pulse.breakthrough.body}
            </p>
          </DomainGlassSection>
        ) : null}

        {pulse.spend_effectiveness ? (
          <DomainGlassSection>
            <DomainSectionHeader title="Spend Effectiveness" />
            <div className="mt-3">
              <DomainKvRow label="Spend" value={pulse.spend_effectiveness.spend_inr} />
              <DomainKvRow label="Connections" value={pulse.spend_effectiveness.connection_count} />
              <DomainKvRow
                label="Return"
                value={pulse.spend_effectiveness.return_label}
                accent={colors.brandTertiary}
              />
            </div>
          </DomainGlassSection>
        ) : null}

        {pulse.horizon_trajectory || pulse.horizon_opportunity ? (
          <DomainGlassSection>
            <DomainSectionHeader title="Relationship Horizon" />
            <div className="mt-3">
              {pulse.horizon_trajectory ? (
                <DomainKvRow label="Trajectory" value={pulse.horizon_trajectory} />
              ) : null}
              {pulse.horizon_opportunity ? (
                <DomainKvRow
                  label="Opportunity"
                  value={pulse.horizon_opportunity}
                  accent={colors.brandTertiary}
                />
              ) : null}
            </div>
          </DomainGlassSection>
        ) : null}
      </div>
    </div>
  );
}

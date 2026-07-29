"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import {
  DomainActivityTimeline,
  DomainGlassSection,
  DomainInsightCard,
  DomainKvRow,
  DomainProfileHero,
  DomainRuntimeTiles,
  DomainSectionHeader,
} from "@/components/personal/shared/domain/DomainScreens";
import type { PersonalEmotionalSecurityMomentDetail } from "@/lib/api/personalDomainTypes";

export function EmotionalSecurityMoments({
  detail,
  bottomPadding = 0,
}: {
  detail: PersonalEmotionalSecurityMomentDetail;
  bottomPadding?: number;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <div className="relative mx-auto w-full max-w-[1080px] space-y-5 px-5 py-6 pb-24 md:px-20">
        <header>
          <h2 className="text-2xl font-bold">{detail.screen_title}</h2>
          <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
            {detail.section_label}
          </p>
        </header>

        {detail.bond_profile ? (
          <DomainProfileHero
            identityLabel={detail.bond_profile.identity_label}
            percent={detail.bond_profile.bond_percent}
            leftLabel={detail.bond_profile.focus_label}
            rightLabel={detail.bond_profile.energy_label}
            footerLabel={detail.bond_profile.want_more_label}
          />
        ) : null}

        {detail.spend_summary ? (
          <DomainGlassSection>
            <DomainSectionHeader title="Spend" />
            <div className="mt-3">
              <DomainKvRow label="Spend" value={detail.spend_summary.spend_inr} />
              <DomainKvRow label="Connections" value={`${detail.spend_summary.connection_count}`} />
              <DomainKvRow label="Return" value={detail.spend_summary.return_label} />
            </div>
          </DomainGlassSection>
        ) : null}

        {detail.returns_summary ? (
          <DomainGlassSection>
            <DomainSectionHeader title="Returns" />
            <div className="mt-3">
              <DomainKvRow
                label="Bond score"
                value={detail.returns_summary.bond_score_inr}
                accent={colors.brandTertiary}
              />
              <DomainKvRow label="Connections" value={`${detail.returns_summary.connections}`} />
              <DomainKvRow label="Support entries" value={`${detail.returns_summary.support_entries}`} />
              <DomainKvRow label="Shared experiences" value={`${detail.returns_summary.shared_experiences}`} />
              <DomainKvRow label="Investments" value={`${detail.returns_summary.investments}`} />
            </div>
          </DomainGlassSection>
        ) : null}

        {detail.relationship_insight ? (
          <DomainInsightCard title="Relationship Insight" body={detail.relationship_insight} />
        ) : null}

        <DomainGlassSection>
          <div className="text-center">
            <h3 className="text-xl font-bold">{detail.rhythm_label}</h3>
            <span
              className="mt-3 inline-block rounded-full px-3 py-1 text-xs font-semibold"
              style={{
                color: colors.brandPrimary,
                background: `color-mix(in srgb, ${colors.brandPrimary} 12%, transparent)`,
              }}
            >
              {detail.active_session_label}
            </span>
          </div>
        </DomainGlassSection>

        <DomainRuntimeTiles
          tiles={[
            detail.runtime_profile,
            detail.runtime_focus,
            detail.runtime_energy,
            detail.runtime_want_more,
          ]}
        />

        <DomainActivityTimeline timeline={detail.activity_timeline.timeline} />

        <div
          className="fixed bottom-0 left-0 right-0 flex gap-2 border-t px-5 py-3"
          style={{
            borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
            background: `color-mix(in srgb, ${colors.surfaceContainer} 85%, transparent)`,
            paddingBottom: bottomPadding + 12,
          }}
        >
          {[detail.bottom_actions.edit_label, detail.bottom_actions.export_label, detail.bottom_actions.archive_label].map(
            (label) => (
              <button
                key={label}
                type="button"
                className="flex-1 rounded-lg py-2 text-sm font-medium"
                style={{ color: colors.textPrimary }}
              >
                {label}
              </button>
            ),
          )}
        </div>
      </div>
    </div>
  );
}

export function EmotionalSecurityMomentsSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
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
            <div className="mb-3 h-12 w-32 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mb-4 h-20 w-full animate-pulse rounded-xl bg-[#2a2a2a]" />
            <div className="grid grid-cols-4 gap-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex flex-col items-center gap-1">
                  <div className="h-6 w-12 animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-5 w-28 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-2">
              {[...Array(3)].map((_, j) => (
                <div key={j} className="flex items-center justify-between">
                  <div className="h-4 w-24 animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-4 w-16 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mb-3 h-5 w-28 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="space-y-2">
              {[...Array(5)].map((_, j) => (
                <div key={j} className="flex items-center justify-between">
                  <div className="h-4 w-28 animate-pulse rounded bg-[#2a2a2a]" />
                  <div className="h-4 w-16 animate-pulse rounded bg-[#2a2a2a]" />
                </div>
              ))}
            </div>
          </div>
          <div className="flex gap-4 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="h-3 w-3 animate-pulse rounded-full bg-[#2a2a2a]" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-32 animate-pulse rounded bg-[#2a2a2a]" />
              <div className="h-3 w-full animate-pulse rounded bg-[#2a2a2a]" />
            </div>
          </div>
          <div className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-5">
            <div className="mx-auto mb-3 h-6 w-40 animate-pulse rounded bg-[#2a2a2a]" />
            <div className="mx-auto h-6 w-24 animate-pulse rounded-full bg-[#2a2a2a]" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <div className="mb-1 h-3 w-16 animate-pulse rounded bg-[#2a2a2a]" />
                <div className="h-6 w-12 animate-pulse rounded bg-[#2a2a2a]" />
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
        </div>
      </div>
    </div>
  );
}

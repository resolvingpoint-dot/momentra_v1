"use client";

import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import {
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { BestMomentsCarousel } from "@/components/personal/life_operations/moments/widgets/BestMomentsCarousel";
import { JourneyHero } from "@/components/personal/life_operations/moments/widgets/JourneyHero";
import { MotionStaggerRoot, MotionSection } from "@/components/shared/MotionStagger";
import { JourneyTimeline } from "@/components/personal/life_operations/moments/widgets/JourneyTimeline";
import { MoneyJourneyChart } from "@/components/personal/life_operations/moments/widgets/MoneyJourneyChart";
import { TurningPointsList } from "@/components/personal/life_operations/moments/widgets/TurningPointsList";
import { lifeOpsMomentsCopy } from "@/lib/personal/life_operations/moments/lifeOpsMomentsCopy";
import type { TemplateMomentsResponse } from "@/lib/api/personal";

type LifeOperationsMomentsProps = {
  data: TemplateMomentsResponse;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
  onManage?: () => void;
  onComplete?: () => void;
  onArchive?: () => void;
};

export function LifeOperationsMoments({
  data,
  bottomPadding = 0,
  hideScreenHeader = false,
  onManage,
  onComplete,
  onArchive,
}: LifeOperationsMomentsProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const moment = data.moment;
  const projection = data.moment_projection;

  if (projection) {
    return (
      <div
        data-momentra-context="personal"
        className="relative min-h-0 flex-1 overflow-y-auto"
        style={scrollShellStyle(tokens, bottomPadding)}
      >
        <PersonalAtmosphericOrbs />
        <div style={personalPulseContainerStyle(tokens)}>
          <MotionStaggerRoot>
            <MotionSection>
              <header className="flex flex-wrap items-start justify-between gap-3">
            {!hideScreenHeader ? (
            <div>
              <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
                {lifeOpsMomentsCopy.screenBreadcrumb}
              </p>
              <h1 style={{ ...personalTypography.screenTitle, color: colors.brandPrimary }}>
                {lifeOpsMomentsCopy.screenTitle}
              </h1>
            </div>
            ) : (
              <div />
            )}
            {moment && (onManage || onComplete || onArchive) ? (
              <div className="flex flex-wrap items-center gap-2">
                {onManage ? (
                  <button type="button" onClick={onManage} className="text-sm underline opacity-80">
                    Manage
                  </button>
                ) : null}
                {onComplete ? (
                  <button
                    type="button"
                    onClick={onComplete}
                    className="rounded-lg px-3 py-1.5 text-sm font-medium"
                    style={{ background: colors.primaryContainer, color: colors.onPrimaryContainer }}
                  >
                    Complete
                  </button>
                ) : null}
                {onArchive ? (
                  <button
                    type="button"
                    onClick={onArchive}
                    className="rounded-lg border px-3 py-1.5 text-sm"
                    style={{ borderColor: colors.border }}
                  >
                    Archive
                  </button>
                ) : null}
              </div>
            ) : null}
          </header>
            </MotionSection>
            <MotionSection><JourneyHero hero={projection.journey_hero} /></MotionSection>
            <MotionSection><JourneyTimeline items={projection.journey_timeline} /></MotionSection>
            <MotionSection><MoneyJourneyChart money={projection.money_journey} /></MotionSection>
            <MotionSection><BestMomentsCarousel cards={projection.best_moments} /></MotionSection>
            <MotionSection><TurningPointsList points={projection.turning_points} /></MotionSection>
          </MotionStaggerRoot>
        </div>
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
      <div style={personalPulseContainerStyle(tokens)}>
        <MotionStaggerRoot>
        {!hideScreenHeader ? (
        <MotionSection>
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            Personal · Moments
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            Life Operations
          </h1>
        </header>
        </MotionSection>
        ) : null}

        {moment ? (
          <MotionSection>
          <section
            className="rounded-2xl border p-5"
            style={{ borderColor: colors.border, background: colors.surfaceContainer }}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-wide opacity-60">{data.status}</p>
                <h2 className="text-lg font-semibold">{moment.moment_name}</h2>
                {moment.moment_description ? (
                  <p className="mt-1 text-sm opacity-80">{moment.moment_description}</p>
                ) : null}
              </div>
              {onManage ? (
                <button type="button" onClick={onManage} className="text-sm underline opacity-80">
                  Manage
                </button>
              ) : null}
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {onComplete ? (
                <button
                  type="button"
                  onClick={onComplete}
                  className="rounded-lg px-3 py-1.5 text-sm font-medium"
                  style={{ background: colors.primaryContainer, color: colors.onPrimaryContainer }}
                >
                  Complete
                </button>
              ) : null}
              {onArchive ? (
                <button
                  type="button"
                  onClick={onArchive}
                  className="rounded-lg border px-3 py-1.5 text-sm"
                  style={{ borderColor: colors.border }}
                >
                  Archive
                </button>
              ) : null}
            </div>
          </section>
          </MotionSection>
        ) : null}

        <MotionSection>
        <section className="mt-6">
          <h3 className="text-sm font-semibold opacity-80">{data.progress.label}</h3>
          <p className="text-sm opacity-60">{data.progress.subtitle}</p>
        </section>
        </MotionSection>
        </MotionStaggerRoot>
      </div>
    </div>
  );
}

export function LifeOperationsMomentsSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="relative min-h-0 flex-1 overflow-y-auto bg-[#14121b]" style={{ paddingBottom: bottomPadding || 16 }}>
      <div className="mx-auto max-w-[1080px] space-y-4 p-6">
        <div className="h-7 w-48 animate-pulse rounded bg-[#2a2a2a]" />
        <div className="h-32 animate-pulse rounded-2xl bg-[#2a2a2a]" />
        <div className="h-24 animate-pulse rounded-2xl bg-[#2a2a2a]" />
      </div>
    </div>
  );
}

export function LifeOperationsMomentsEmpty({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div
      className="flex min-h-0 flex-1 flex-col items-center justify-center px-6 text-center"
      style={{ paddingBottom: bottomPadding }}
    >
      <p className="text-sm opacity-70">No Life Operations moment yet.</p>
    </div>
  );
}

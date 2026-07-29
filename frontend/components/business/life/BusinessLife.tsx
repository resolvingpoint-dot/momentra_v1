"use client";

import {
  OPS_LIFE_SLICE_KEYS,
  RUNWAY_LIFE_SLICE_KEYS,
  TEAM_OPS_LIFE_SLICE_KEYS,
  type BusinessLifeResponse,
} from "@/lib/api/businessActive";
import {
  TeamOpsEmptyLine,
  TeamOpsScrollShell,
  TeamOpsStatusBanner,
} from "@/components/business/active/team-operations/shared/shared";
import {
  LmBandHero,
  LmConnectionsSection,
  LmContributionDetails,
  LmDriftAlertSection,
  LmDrivesGrowthSection,
  LmJourneySection,
  LmLeverageSection,
  LmMonthlyChangesSection,
  LmQuickActions,
  LmSliceCard,
  LmTrendsSection,
} from "@/components/business/life-memory/LifeMemoryStitchComponents";

type Props = {
  data: BusinessLifeResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
  onCreateMoment?: () => void;
};

const LIFE_SLICE_KEYS = [
  ...TEAM_OPS_LIFE_SLICE_KEYS,
  ...RUNWAY_LIFE_SLICE_KEYS,
  ...OPS_LIFE_SLICE_KEYS,
] as const;

/**
 * Shared Business Life — stitch layout (life_business docs).
 * Real bands/signals/dimensions/journey only; no composite score or invented narrative.
 */
export function TeamOperationsLifeContribution({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  onRetry,
  onQuickAdd,
  onCreateMoment,
}: Props) {
  if (loading && !data) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsStatusBanner loading refreshing={false} error={null} onRetry={onRetry} />
      </TeamOpsScrollShell>
    );
  }
  if (error && !data) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsStatusBanner loading={false} error={error} onRetry={onRetry} />
      </TeamOpsScrollShell>
    );
  }
  if (!data) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsEmptyLine label="No data" />
      </TeamOpsScrollShell>
    );
  }

  const signals = Array.isArray(data.signals) ? data.signals : [];
  const dimensions = Array.isArray(data.dimensions) ? data.dimensions : [];
  const journey = Array.isArray(data.journey) ? data.journey : [];
  const uniqueSliceKeys = Array.from(new Set(LIFE_SLICE_KEYS));
  const slicesWithData = uniqueSliceKeys.filter((key) => data.slices[key]);

  // Fixed stitch section numbering (docs): 1 Health … 8 Journey … QA last
  const nConnections = 2;
  const nDrift = 3;
  const nLeverage = 4;
  const nTrends = 5;
  const nGrowth = 6;
  const nMonthly = 7;
  const nJourney = 8;
  const nActions = onQuickAdd || onCreateMoment ? 9 : 0;

  return (
    <TeamOpsScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <TeamOpsStatusBanner loading={false} refreshing error={null} onRetry={onRetry} />
      ) : null}

      <LmBandHero health={data.health} activeMomentCount={data.active_moment_count} />

      <LmConnectionsSection sectionIndex={nConnections} />

      <LmDriftAlertSection signals={signals} sectionIndex={nDrift} />

      <LmLeverageSection dimensions={dimensions} sectionIndex={nLeverage} />

      <div className="grid grid-cols-2 gap-4">
        <LmTrendsSection dimensions={dimensions} sectionIndex={nTrends} />
        <LmDrivesGrowthSection sectionIndex={nGrowth} />
      </div>

      <LmMonthlyChangesSection sectionIndex={nMonthly} />

      <LmJourneySection items={journey} sectionIndex={nJourney} title="Business Journey" />

      {nActions ? (
        <LmQuickActions
          sectionIndex={nActions}
          onQuickAdd={onQuickAdd}
          onCreateMoment={onCreateMoment}
        />
      ) : null}

      {slicesWithData.length > 0 ? (
        <LmContributionDetails>
          {slicesWithData.map((key, i) => {
            const slice = data.slices[key]!;
            return (
              <LmSliceCard
                key={key}
                index={i + 1}
                title={slice.label || key}
                band={slice.band}
                count={slice.count}
                state={slice.state}
                items={slice.items ?? []}
              />
            );
          })}
        </LmContributionDetails>
      ) : null}
    </TeamOpsScrollShell>
  );
}

export function BusinessLife(props: Props) {
  return <TeamOperationsLifeContribution {...props} />;
}

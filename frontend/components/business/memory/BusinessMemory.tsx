"use client";

import { useMemo, useState } from "react";
import type { BusinessMemoryEvent, BusinessMemoryResponse } from "@/lib/api/businessActive";
import { MEMORY_BUCKET_LABELS, MEMORY_BUCKET_ORDER } from "@/lib/business/teamOpsApiMappers";
import {
  TeamOpsEmptyLine,
  TeamOpsScrollShell,
  TeamOpsStatusBanner,
} from "@/components/business/active/team-operations/shared/shared";
import {
  LmBiggestLearningSection,
  LmBucketSection,
  LmContributionDetails,
  LmFilterChips,
  LmJourneySection,
  LmMemoryStrengthHero,
  LmPatternNetworkSection,
  LmPlaybookSection,
  LmQuickActions,
  LmRiskMemorySection,
  LmSuccessMemorySection,
  LmWisdomSection,
} from "@/components/business/life-memory/LifeMemoryStitchComponents";

type Props = {
  data: BusinessMemoryResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
  onCreateMoment?: () => void;
};

function matchesFilter(
  event: BusinessMemoryEvent,
  filterKey: string,
  momentTypes: string[],
): boolean {
  if (filterKey === "all" || momentTypes.length === 0) return true;
  const t = (event.source_moment_type || "").toUpperCase().replace(/ /g, "_");
  return momentTypes.includes(t);
}

/**
 * Shared Business Memory — stitch layout (memory_business docs).
 * Factual summary + allowlisted evidence only; no strength score / AI narrative.
 */
export function TeamOperationsMemoryContribution({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  onRetry,
  onQuickAdd,
  onCreateMoment,
}: Props) {
  const [filterKey, setFilterKey] = useState("all");

  const filters = data?.source_filters?.length
    ? data.source_filters
    : [{ key: "all", label: "All", moment_types: [] as string[] }];

  const activeFilter = filters.find((f) => f.key === filterKey) ?? filters[0];
  const momentTypes = activeFilter?.moment_types ?? [];

  const filteredEvents = useMemo(() => {
    const events = data?.events ?? [];
    return events.filter((e) => matchesFilter(e, activeFilter?.key ?? "all", momentTypes));
  }, [data?.events, activeFilter?.key, momentTypes]);

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

  const patterns = Array.isArray(data.patterns) ? data.patterns : [];
  const success = data.success_memory ?? [];
  const risk = data.risk_memory ?? [];
  const journey = data.journey ?? [];
  const playbooks = data.playbooks ?? [];
  const biggestLearning = success[0] ?? null;
  const bucketKeys = MEMORY_BUCKET_ORDER.filter((key) => key in (data.buckets ?? {}));
  const satellites = patterns
    .filter((p) => typeof p !== "string" && (p.pattern_type || "").toLowerCase() === "dimension_active")
    .map((p) => (typeof p === "string" ? p : p.label || p.dimension || ""))
    .filter(Boolean)
    .map((s) =>
      s
        .replace(/is actively being tracked/gi, "")
        .replace(/BUSINESS_/gi, "")
        .replace(/_/g, " ")
        .trim(),
    )
    .slice(0, 4);

  // Fixed stitch numbering from memory_business docs
  const nLearning = 2;
  const nPatterns = 3;
  const nPlaybook = 4;
  const nSuccess = 5;
  const nRisk = 6;
  const nWisdom = 7;
  const nJourney = 8;
  const nActions = onQuickAdd || onCreateMoment ? 9 : 0;

  return (
    <TeamOpsScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <TeamOpsStatusBanner loading={false} refreshing error={null} onRetry={onRetry} />
      ) : null}

      <LmFilterChips
        filters={filters}
        activeKey={activeFilter?.key ?? "all"}
        onChange={setFilterKey}
      />

      <LmMemoryStrengthHero
        summary={data.summary}
        activeMomentCount={data.active_moment_count}
        eventCount={data.summary?.event_count ?? filteredEvents.length}
        satellites={satellites}
      />

      <LmBiggestLearningSection item={biggestLearning} sectionIndex={nLearning} />

      <LmPatternNetworkSection patterns={patterns} sectionIndex={nPatterns} />

      <LmPlaybookSection playbooks={playbooks} sectionIndex={nPlaybook} />

      <LmSuccessMemorySection items={success} sectionIndex={nSuccess} />

      <LmRiskMemorySection items={risk} sectionIndex={nRisk} />

      <LmWisdomSection sectionIndex={nWisdom} />

      <LmJourneySection
        items={journey}
        sectionIndex={nJourney}
        title="Knowledge Journey"
      />

      {nActions ? (
        <LmQuickActions
          sectionIndex={nActions}
          onQuickAdd={onQuickAdd}
          onCreateMoment={onCreateMoment}
        />
      ) : null}

      {bucketKeys.length > 0 || filteredEvents.length > 0 ? (
        <LmContributionDetails>
          {filteredEvents.length > 0 ? (
            <LmBucketSection
              index={1}
              title="Timeline"
              items={filteredEvents.slice(0, 40)}
            />
          ) : null}
          {bucketKeys.map((key, i) => {
            const items = (data.buckets?.[key]?.items ?? []).filter((e) =>
              matchesFilter(e, activeFilter?.key ?? "all", momentTypes),
            );
            const label = MEMORY_BUCKET_LABELS[key] ?? key;
            return (
              <LmBucketSection
                key={key}
                index={i + 2}
                title={label}
                items={items}
              />
            );
          })}
        </LmContributionDetails>
      ) : null}
    </TeamOpsScrollShell>
  );
}

export function BusinessMemory(props: Props) {
  return <TeamOperationsMemoryContribution {...props} />;
}

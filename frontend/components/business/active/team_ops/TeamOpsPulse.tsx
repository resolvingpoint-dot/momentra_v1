"use client";

/**
 * Presentational Team Operations Pulse — data already mapped by ViewModel.
 */
import type { TeamOpsEventItem, TeamOpsPulseResponse } from "@/lib/api/businessActive";
import { TeamOpsEmptyLine, TeamOpsScrollShell, TeamOpsStatusBanner } from "./shared";
import {
  PulseApprovals,
  PulseAttention,
  PulseHero,
  PulseIssues,
  PulseKpis,
  PulseNextAction,
  PulseParticipation,
  PulseRecentActivity,
  PulseRecognition,
  PulseSignals,
} from "./widgets/PulseWidgets";

type Props = {
  data: TeamOpsPulseResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
  onViewActivity?: () => void;
  onSelectActivity?: (item: TeamOpsEventItem) => void;
};

export function TeamOperationsPulse({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  onRetry,
  onQuickAdd,
  onViewActivity,
  onSelectActivity,
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

  return (
    <TeamOpsScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <TeamOpsStatusBanner loading={false} refreshing error={null} onRetry={onRetry} />
      ) : null}
      <PulseHero data={data} />
      <PulseKpis data={data} />
      <PulseParticipation data={data} />
      <PulseApprovals data={data} />
      <PulseIssues data={data} />
      <PulseRecognition data={data} />
      <PulseSignals data={data} />
      <PulseAttention data={data} />
      <PulseRecentActivity
        data={data}
        onViewActivity={onViewActivity}
        onSelectActivity={onSelectActivity}
      />
      <PulseNextAction data={data} onQuickAdd={onQuickAdd} />
    </TeamOpsScrollShell>
  );
}

/** @deprecated use TeamOperationsPulse */
export const TeamOpsPulse = TeamOperationsPulse;

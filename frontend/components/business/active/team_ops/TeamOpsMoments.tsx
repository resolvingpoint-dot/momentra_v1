"use client";

import type { TeamOpsMomentsResponse } from "@/lib/api/businessActive";
import { TEAM_OPS } from "./teamOpsTheme";
import {
  TeamOpsEmptyLine,
  TeamOpsScrollShell,
  TeamOpsSectionCard,
  TeamOpsStatusBanner,
} from "./shared";
import {
  MomentsApprovals,
  MomentsHero,
  MomentsIssues,
  MomentsMeetings,
  MomentsMilestones,
  MomentsRecentActivity,
  MomentsRecognition,
  MomentsTeamChanges,
  MomentsTimeline,
} from "./widgets/MomentsWidgets";

type Props = {
  data: TeamOpsMomentsResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
};

export function TeamOperationsMoments({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  onRetry,
  onQuickAdd,
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
      <MomentsHero data={data} />
      <MomentsMilestones data={data} />
      <MomentsMeetings data={data} />
      <MomentsTimeline data={data} />
      <MomentsRecognition data={data} />
      <MomentsIssues data={data} />
      <MomentsApprovals data={data} />
      <MomentsTeamChanges data={data} />
      <MomentsRecentActivity data={data} />
      {onQuickAdd ? (
        <TeamOpsSectionCard>
          <p className="mb-3 text-sm" style={{ color: TEAM_OPS.onVariant }}>
            Capture the next team moment.
          </p>
          <button
            type="button"
            className="w-full rounded-xl py-3 text-sm font-semibold"
            style={{ background: TEAM_OPS.primaryContainer, color: "#0d0096" }}
            onClick={onQuickAdd}
          >
            Open Action Center
          </button>
        </TeamOpsSectionCard>
      ) : null}
    </TeamOpsScrollShell>
  );
}

/** @deprecated use TeamOperationsMoments */
export const TeamOpsMoments = TeamOperationsMoments;

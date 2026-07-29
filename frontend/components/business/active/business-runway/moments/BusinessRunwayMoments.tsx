"use client";

import type { RunwayMomentsResponse } from "@/lib/api/businessActive";
import {
  RunwayHighlights,
  RunwayManageBar,
  RunwayMomentsHero,
  RunwayProgressSnapshot,
  RunwayScrollShell,
  RunwayTimelineSection,
} from "../shared/RunwayStitchComponents";
import { RUNWAY } from "../shared/runwayTheme";

type Props = {
  data: RunwayMomentsResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
};

export function BusinessRunwayMoments({
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
      <RunwayScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          Loading journey…
        </p>
      </RunwayScrollShell>
    );
  }
  if (error && !data) {
    const denied =
      /403|401|permission|forbidden|not a member|invalid_member|membership/i.test(error);
    return (
      <RunwayScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: denied ? RUNWAY.onVariant : RUNWAY.error }}>
          {denied ? "This moment is no longer available." : error}
        </p>
        {!denied ? (
          <button type="button" className="mt-2 text-sm underline" onClick={onRetry}>
            Retry
          </button>
        ) : null}
      </RunwayScrollShell>
    );
  }
  if (!data) return null;

  const highlights = (data.recent_activity.items.length > 0
    ? data.recent_activity.items
    : data.milestones.items);

  return (
    <RunwayScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <p className="mb-2 text-xs" style={{ color: RUNWAY.onVariant }}>
          Updating…
        </p>
      ) : null}
      <div className="flex flex-col gap-5">
        <RunwayMomentsHero data={data} onQuickAdd={onQuickAdd} />
        <RunwayTimelineSection items={data.timeline.items} />
        <RunwayProgressSnapshot data={data} />
        <RunwayHighlights items={highlights} />
        <RunwayManageBar onQuickAdd={onQuickAdd} />
      </div>
    </RunwayScrollShell>
  );
}

"use client";

import type { RunwayPulseResponse, TeamOpsEventItem } from "@/lib/api/businessActive";
import {
  RunwayActivityFeed,
  RunwayAttentionCards,
  RunwayHealthHero,
  RunwayKpiGrid,
  RunwayNextAction,
  RunwayScrollShell,
  RunwaySignalsGrid,
} from "../shared/RunwayStitchComponents";
import { RUNWAY } from "../shared/runwayTheme";

type Props = {
  data: RunwayPulseResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
  onViewActivity?: () => void;
};

export function BusinessRunwayPulse({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  onRetry,
  onQuickAdd,
  onViewActivity,
}: Props) {
  if (loading && !data) {
    return (
      <RunwayScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          Loading runway…
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
  if (!data) {
    return (
      <RunwayScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          No data
        </p>
      </RunwayScrollShell>
    );
  }

  return (
    <RunwayScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <p className="mb-2 text-xs" style={{ color: RUNWAY.onVariant }}>
          Updating…
        </p>
      ) : null}
      <div className="flex flex-col gap-4">
        <RunwayHealthHero data={data} />
        <RunwayKpiGrid data={data} />
        <RunwayAttentionCards items={data.attention_items.items} onViewAll={onViewActivity} />
        <RunwaySignalsGrid items={data.signals.items} />
        <RunwayActivityFeed items={data.recent_activity.items} onViewAll={onViewActivity} />
        <RunwayNextAction item={data.next_best_action.item} onQuickAdd={onQuickAdd} />
      </div>
    </RunwayScrollShell>
  );
}

"use client";

import type { OpsMomentsResponse } from "@/lib/api/businessActive";
import {
  OpsManageBar,
  OpsMilestonesSection,
  OpsMomentsHero,
  OpsScrollShell,
  OpsTimelineSection,
} from "../shared/OpsStitchComponents";
import { OPS } from "../shared/opsTheme";

type Props = {
  data: OpsMomentsResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
};

export function BusinessOperationsMoments({
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
      <OpsScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: OPS.onVariant }}>
          Loading journey…
        </p>
      </OpsScrollShell>
    );
  }
  if (error && !data) {
    const denied =
      /403|401|permission|forbidden|not a member|invalid_member|membership/i.test(error);
    return (
      <OpsScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: denied ? OPS.onVariant : OPS.error }}>
          {denied ? "This moment is no longer available." : error}
        </p>
        {!denied ? (
          <button type="button" className="mt-2 text-sm underline" onClick={onRetry}>
            Retry
          </button>
        ) : null}
      </OpsScrollShell>
    );
  }
  if (!data) return null;

  return (
    <OpsScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <p className="mb-2 text-xs" style={{ color: OPS.onVariant }}>
          Updating…
        </p>
      ) : null}
      <div className="flex flex-col gap-4">
        <OpsMomentsHero data={data} onQuickAdd={onQuickAdd} />
        <OpsTimelineSection title="Spend timeline" items={data.spend_timeline.items} emptyLabel="No spend yet" />
        <OpsTimelineSection title="Approvals" items={data.approval_timeline.items} emptyLabel="No approvals yet" />
        <OpsTimelineSection title="Issues" items={data.issue_timeline.items} emptyLabel="No issues yet" />
        <OpsTimelineSection title="Vendors" items={data.vendor_timeline.items} emptyLabel="No vendor updates yet" />
        <OpsTimelineSection
          title="Improvements"
          items={data.improvement_timeline.items}
          emptyLabel="No improvements yet"
        />
        <OpsMilestonesSection items={data.milestones.items} />
        <OpsTimelineSection title="Key decisions" items={data.key_decisions.items} emptyLabel="No decisions yet" />
        <OpsTimelineSection title="Moment Timeline" items={data.timeline.items} emptyLabel="No timeline events" />
        <OpsTimelineSection
          title="Recent Highlights"
          items={data.recent_activity.items}
          emptyLabel="No recent activity"
        />
        <OpsManageBar onQuickAdd={onQuickAdd} />
      </div>
    </OpsScrollShell>
  );
}

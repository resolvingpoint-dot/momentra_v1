"use client";

import type { OpsPulseResponse } from "@/lib/api/businessActive";
import {
  OpsActivityFeed,
  OpsApprovalsCard,
  OpsAttentionCards,
  OpsBudgetUsage,
  OpsHealthCard,
  OpsHero,
  OpsImprovementsCard,
  OpsIssuesCard,
  OpsKpiGrid,
  OpsMonitoringCard,
  OpsNextAction,
  OpsScrollShell,
  OpsSignalsGrid,
  OpsVendorsCard,
} from "../shared/OpsStitchComponents";
import { OPS } from "../shared/opsTheme";

type Props = {
  data: OpsPulseResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onQuickAdd?: () => void;
  onViewActivity?: () => void;
};

export function BusinessOperationsPulse({
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
      <OpsScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: OPS.onVariant }}>
          Loading operations…
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
  if (!data) {
    return (
      <OpsScrollShell bottomPadding={bottomPadding}>
        <p className="text-sm" style={{ color: OPS.onVariant }}>
          No data
        </p>
      </OpsScrollShell>
    );
  }

  return (
    <OpsScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <p className="mb-2 text-xs" style={{ color: OPS.onVariant }}>
          Updating…
        </p>
      ) : null}
      <div className="flex flex-col gap-4">
        <OpsHero data={data} />
        <OpsHealthCard data={data} />
        <OpsKpiGrid data={data} />
        <OpsBudgetUsage data={data} />
        <OpsApprovalsCard data={data} />
        <OpsIssuesCard data={data} />
        <OpsVendorsCard data={data} />
        <OpsImprovementsCard data={data} />
        <OpsMonitoringCard data={data} />
        <OpsAttentionCards items={data.attention_items.items} onViewAll={onViewActivity} />
        <OpsSignalsGrid items={data.signals.items} />
        <OpsActivityFeed items={data.recent_activity.items} onViewAll={onViewActivity} />
        <OpsNextAction item={data.next_best_action.item} onQuickAdd={onQuickAdd} />
      </div>
    </OpsScrollShell>
  );
}

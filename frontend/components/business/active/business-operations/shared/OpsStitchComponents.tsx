"use client";

import type {
  OpsMilestoneItem,
  OpsMomentsResponse,
  OpsPulseResponse,
  TeamOpsEventItem,
} from "@/lib/api/businessActive";
import { formatMinorCurrency } from "@/lib/business/opsApiMappers";
import { OPS, opsBandColor, formatOccurredAt } from "./opsTheme";

export function OpsScrollShell({
  children,
  bottomPadding = 0,
}: {
  children: React.ReactNode;
  bottomPadding?: number;
}) {
  return (
    <div
      className="min-h-0 flex-1 overflow-y-auto px-4 pt-4"
      style={{
        paddingBottom: bottomPadding,
        background: OPS.bg,
        color: OPS.onSurface,
        fontFamily: OPS.fontBody,
      }}
    >
      {children}
    </div>
  );
}

export function OpsCard({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl border p-4 ${className}`}
      style={{ background: OPS.surface, borderColor: `${OPS.outline}33` }}
    >
      {children}
    </div>
  );
}

function SectionHeader({
  title,
  trailing,
  onTrailing,
}: {
  title: string;
  trailing?: string;
  onTrailing?: () => void;
}) {
  return (
    <div className="mb-2 flex items-center justify-between gap-2">
      <p className="text-sm font-semibold" style={{ fontFamily: OPS.fontDisplay }}>
        {title}
      </p>
      {trailing && onTrailing ? (
        <button type="button" className="text-xs font-semibold" style={{ color: OPS.primary }} onClick={onTrailing}>
          {trailing}
        </button>
      ) : null}
    </div>
  );
}

function Badge({ text, tone }: { text: string; tone: string }) {
  return (
    <span
      className="rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide"
      style={{ color: tone, background: `${tone}2e` }}
    >
      {text}
    </span>
  );
}

export function OpsHero({ data }: { data: OpsPulseResponse }) {
  const name =
    data.hero.operations_name ||
    data.operations_name ||
    data.hero.moment_name ||
    data.moment_name ||
    "Business Operations";
  return (
    <OpsCard>
      <p className="text-[11px] font-semibold uppercase tracking-wide" style={{ color: OPS.onVariant }}>
        Operations
      </p>
      <h2 className="mt-1 text-2xl font-semibold" style={{ fontFamily: OPS.fontDisplay }}>
        {name}
      </h2>
      {data.hero.operations_scope || data.hero.operating_model || data.hero.owner ? (
        <p className="mt-2 text-sm" style={{ color: OPS.onVariant }}>
          {[data.hero.operations_scope, data.hero.operating_model, data.hero.owner]
            .filter(Boolean)
            .join(" · ")}
        </p>
      ) : null}
    </OpsCard>
  );
}

export function OpsHealthCard({ data }: { data: OpsPulseResponse }) {
  const health = data.operations_health;
  const band = health.band ?? "EMPTY";
  const tone = opsBandColor(band);
  return (
    <OpsCard className="!bg-gradient-to-b from-[#2a3344] to-[#181c23]">
      <div className="flex items-start justify-between gap-3">
        <p className="text-[11px] font-semibold uppercase tracking-wide" style={{ color: OPS.onVariant }}>
          Operations Health
        </p>
        <Badge text={health.label || "Not started"} tone={tone} />
      </div>
      <p className="mt-2 text-3xl font-bold" style={{ color: tone, fontFamily: OPS.fontDisplay }}>
        {health.label || "Not started"}
      </p>
      <p className="mt-2 text-xs" style={{ color: OPS.onVariant }}>
        Overall Business Operations health from budget control, operational stability, issue resolution, and
        process improvement.
      </p>
      <p className="mt-2 text-[10px] font-semibold uppercase tracking-wide" style={{ color: OPS.onVariant }}>
        {band}
      </p>
    </OpsCard>
  );
}

function budgetStatus(pct: number | null | undefined): string | null {
  if (pct == null || pct <= 0) return null;
  if (pct < 80) return "Good";
  if (pct < 100) return "Watch";
  return "Critical";
}

function KpiChip({
  label,
  value,
  status,
  bar,
}: {
  label: string;
  value: string;
  status?: string | null;
  bar?: number | null;
}) {
  const tone =
    status === "Good"
      ? OPS.primary
      : status === "Watch"
        ? OPS.secondary
        : status === "Critical"
          ? OPS.error
          : OPS.onVariant;
  return (
    <div
      className="min-w-[128px] shrink-0 rounded-xl border p-3"
      style={{ background: OPS.surfaceLow, borderColor: `${OPS.outline}22` }}
    >
      <p className="text-[10px]" style={{ color: OPS.onVariant }}>
        {label}
      </p>
      <p className="mt-1 text-base font-bold">{value}</p>
      {status ? (
        <p className="text-[9px]" style={{ color: tone }}>
          {status}
        </p>
      ) : null}
      {bar != null ? (
        <div className="mt-2 h-1 overflow-hidden rounded-full" style={{ background: `${OPS.onVariant}26` }}>
          <div
            className="h-full rounded-full"
            style={{ width: `${Math.max(0, Math.min(100, bar))}%`, background: tone }}
          />
        </div>
      ) : null}
    </div>
  );
}

export function OpsKpiGrid({ data }: { data: OpsPulseResponse }) {
  const k = data.kpis;
  const budgetPct = k.budget_usage_percent != null ? Math.round(k.budget_usage_percent) : null;
  return (
    <div>
      <SectionHeader title="Health Drivers" />
      <div className="flex gap-2 overflow-x-auto pb-1">
        <KpiChip
          label="Budget Usage"
          value={budgetPct != null ? `${budgetPct}%` : "—"}
          status={budgetStatus(k.budget_usage_percent)}
          bar={budgetPct}
        />
        <KpiChip
          label="Open Issues"
          value={k.open_issue_count != null ? String(k.open_issue_count) : "—"}
          status={k.open_issue_count === 0 ? "Good" : "Watch"}
        />
        <KpiChip
          label="Approval Backlog"
          value={k.pending_approval_count != null ? String(k.pending_approval_count) : "—"}
          status={k.pending_approval_count === 0 ? "Good" : "Watch"}
        />
        <KpiChip
          label="Vendors"
          value={k.active_vendor_count != null ? String(k.active_vendor_count) : "—"}
        />
        <KpiChip
          label="Improvements"
          value={
            k.completed_improvement_count != null ? String(k.completed_improvement_count) : "—"
          }
          status={(k.completed_improvement_count ?? 0) > 0 ? "Good" : null}
        />
      </div>
    </div>
  );
}

export function OpsBudgetUsage({ data }: { data: OpsPulseResponse }) {
  const currency = data.budget_usage.operating_currency ?? data.operating_currency ?? "INR";
  const b = data.budget_usage;
  const over = b.over_budget_allocations?.length ?? 0;
  return (
    <OpsCard>
      <p className="mb-2 text-sm font-semibold" style={{ fontFamily: OPS.fontDisplay }}>
        Budget usage
      </p>
      <ul className="flex flex-col gap-1 text-sm" style={{ color: OPS.onVariant }}>
        <li>Budget · {formatMinorCurrency(b.total_budget_minor, currency)}</li>
        <li>Spent · {formatMinorCurrency(b.total_spend_minor, currency)}</li>
        <li>Remaining · {formatMinorCurrency(b.remaining_minor, currency)}</li>
        {over > 0 ? <li style={{ color: OPS.error }}>Over budget · {over} allocation(s)</li> : null}
      </ul>
    </OpsCard>
  );
}

function StatGrid({
  title,
  rows,
}: {
  title: string;
  rows: Array<{ label: string; value: string | number }>;
}) {
  return (
    <OpsCard>
      <p className="mb-2 text-sm font-semibold" style={{ fontFamily: OPS.fontDisplay }}>
        {title}
      </p>
      <div className="grid grid-cols-2 gap-2">
        {rows.map((row) => (
          <div key={row.label}>
            <p className="text-xs" style={{ color: OPS.onVariant }}>
              {row.label}
            </p>
            <p className="text-sm font-medium">{row.value}</p>
          </div>
        ))}
      </div>
    </OpsCard>
  );
}

export function OpsApprovalsCard({ data }: { data: OpsPulseResponse }) {
  const a = data.approvals;
  return (
    <StatGrid
      title="Approvals"
      rows={[
        { label: "Pending", value: a.pending },
        { label: "Overdue", value: a.overdue },
        { label: "Approved", value: a.approved_recently },
        { label: "Rejected", value: a.rejected_recently },
      ]}
    />
  );
}

export function OpsIssuesCard({ data }: { data: OpsPulseResponse }) {
  const i = data.issues;
  return (
    <StatGrid
      title="Issues"
      rows={[
        { label: "Open", value: i.open },
        { label: "Critical", value: i.critical },
        { label: "Overdue", value: i.overdue },
        { label: "Unassigned", value: i.unassigned },
      ]}
    />
  );
}

export function OpsVendorsCard({ data }: { data: OpsPulseResponse }) {
  const v = data.vendors;
  return (
    <StatGrid
      title="Vendors"
      rows={[
        { label: "Active", value: v.active },
        { label: "Status changes", value: v.status_changes },
        { label: "Critical deps", value: v.critical_dependencies },
        { label: "Unresolved", value: v.unresolved_events },
      ]}
    />
  );
}

export function OpsImprovementsCard({ data }: { data: OpsPulseResponse }) {
  const i = data.improvements;
  return (
    <StatGrid
      title="Improvements"
      rows={[
        { label: "Planned", value: i.planned },
        { label: "In progress", value: i.in_progress },
        { label: "Completed", value: i.completed },
        { label: "Overdue", value: i.overdue },
      ]}
    />
  );
}

export function OpsMonitoringCard({ data }: { data: OpsPulseResponse }) {
  const m = data.monitoring;
  return (
    <OpsCard>
      <p className="mb-2 text-sm font-semibold" style={{ fontFamily: OPS.fontDisplay }}>
        Monitoring
      </p>
      <p className="text-sm" style={{ color: OPS.onVariant }}>
        {m.level ? `Level · ${m.level}` : "No monitoring configured"}
      </p>
      {(m.active_alerts?.length ?? 0) > 0 ? (
        <p className="mt-1 text-sm" style={{ color: OPS.secondary }}>
          {m.active_alerts!.length} active alert(s)
        </p>
      ) : null}
    </OpsCard>
  );
}

function attentionTone(severity?: string): string {
  const s = (severity || "").toLowerCase();
  if (s === "high") return OPS.error;
  if (s === "medium" || s === "med") return OPS.secondary;
  return OPS.primary;
}

export function OpsAttentionCards({
  items,
  onViewAll,
}: {
  items: OpsPulseResponse["attention_items"]["items"];
  onViewAll?: () => void;
}) {
  if (!items.length) return null;
  return (
    <div>
      <SectionHeader
        title="Attention Needed"
        trailing={`View All (${items.length})`}
        onTrailing={onViewAll}
      />
      <div className="flex flex-col gap-2">
        {items.map((item) => {
          const tone = attentionTone(item.severity);
          return (
            <div
              key={`${item.kind}-${item.label}`}
              className="flex items-center gap-3 rounded-xl border p-3.5"
              style={{ background: OPS.surfaceLow, borderColor: `${OPS.outline}22` }}
            >
              <div
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] text-sm font-bold"
                style={{ background: `${tone}26`, color: tone }}
              >
                !
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold">{item.label}</p>
                <div className="mt-1 flex items-center gap-2">
                  <Badge text={item.severity || "med"} tone={tone} />
                  <span className="text-[10px]" style={{ color: OPS.onVariant }}>
                    {item.description || "Needs review"}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function OpsSignalsGrid({ items }: { items: OpsPulseResponse["signals"]["items"] }) {
  if (!items.length) return null;
  return (
    <div>
      <SectionHeader title="Signals" />
      <div className="flex gap-2 overflow-x-auto pb-1">
        {items.map((item) => {
          const tone =
            item.severity?.toLowerCase() === "high" || item.severity?.toLowerCase() === "negative"
              ? OPS.error
              : OPS.primary;
          const change = item.change_percent;
          return (
            <div
              key={`${item.signal_type}-${item.label}`}
              className="min-w-[160px] shrink-0 rounded-xl border p-3"
              style={{ background: OPS.surfaceLow, borderColor: `${OPS.outline}22` }}
            >
              <p className="text-xs font-semibold">{item.title ?? item.label}</p>
              <p className="mt-1 text-[11px]" style={{ color: tone }}>
                {item.summary ||
                  (change != null ? `${change >= 0 ? "+" : ""}${Math.round(change)}%` : "Signal")}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function OpsActivityFeed({
  items,
  onViewAll,
}: {
  items: TeamOpsEventItem[];
  onViewAll?: () => void;
}) {
  return (
    <div>
      <SectionHeader
        title="Recent Activity"
        trailing={items.length ? "View All Activity" : undefined}
        onTrailing={onViewAll}
      />
      {items.length === 0 ? (
        <p className="text-sm" style={{ color: OPS.onVariant }}>
          No activity yet
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.slice(0, 5).map((item) => (
            <div
              key={item.event_id}
              className="flex items-center gap-2.5 rounded-xl p-3"
              style={{ background: OPS.surfaceLow }}
            >
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold"
                style={{ background: `${OPS.primary}26`, color: OPS.primary }}
              >
                {item.title.slice(0, 1).toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold">{item.title}</p>
                <p className="text-[11px]" style={{ color: OPS.onVariant }}>
                  {item.action_type.replace(/_/g, " ")} · {formatOccurredAt(item.occurred_at)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function OpsNextAction({
  item,
  onQuickAdd,
}: {
  item: OpsPulseResponse["next_best_action"]["item"];
  onQuickAdd?: () => void;
}) {
  if (!item) return null;
  return (
    <OpsCard>
      <p className="text-base font-bold" style={{ fontFamily: OPS.fontDisplay }}>
        {item.title || item.label}
      </p>
      {item.subtitle || item.reason ? (
        <p className="mt-1 text-xs" style={{ color: OPS.onVariant }}>
          {item.subtitle || item.reason}
        </p>
      ) : null}
      {onQuickAdd ? (
        <button
          type="button"
          className="mt-3 w-full rounded-full px-4 py-2.5 text-sm font-semibold"
          style={{ background: OPS.secondaryContainer, color: OPS.onSurface }}
          onClick={onQuickAdd}
        >
          {item.cta_label ?? "Take Action"}
        </button>
      ) : null}
    </OpsCard>
  );
}

export function OpsMomentsHero({
  data,
  onQuickAdd,
}: {
  data: OpsMomentsResponse;
  onQuickAdd?: () => void;
}) {
  const stats = data.summary_stats;
  const isActive = (data.status || "").toUpperCase() === "ACTIVE";
  return (
    <OpsCard className="!bg-gradient-to-b from-[#2a3344] to-[#181c23]">
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-xl font-bold" style={{ fontFamily: OPS.fontDisplay }}>
          {data.journey_hero.title}
        </h2>
        {isActive ? <Badge text="Active" tone={OPS.primary} /> : null}
      </div>
      <p className="mt-1 text-sm" style={{ color: OPS.onVariant }}>
        {[data.journey_hero.current_phase, data.journey_hero.progress_percent != null ? `Progress ${data.journey_hero.progress_percent}%` : null]
          .filter(Boolean)
          .join(" · ") ||
          data.journey_hero.subtitle ||
          "Operational journey"}
      </p>
      <div className="mt-4 flex justify-between gap-2">
        <div>
          <p className="text-sm font-bold">
            {stats.budget_used_percent != null ? `${Math.round(Number(stats.budget_used_percent))}%` : "—"}
          </p>
          <p className="text-[10px]" style={{ color: OPS.onVariant }}>
            Budget Used
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold">{stats.open_issues ?? "—"}</p>
          <p className="text-[10px]" style={{ color: OPS.onVariant }}>
            Open Issues
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm font-bold">{stats.approvals ?? "—"}</p>
          <p className="text-[10px]" style={{ color: OPS.onVariant }}>
            Approvals
          </p>
        </div>
      </div>
      {onQuickAdd ? (
        <button
          type="button"
          className="mt-3 text-xs font-semibold"
          style={{ color: OPS.secondary }}
          onClick={onQuickAdd}
        >
          Quick Add →
        </button>
      ) : null}
    </OpsCard>
  );
}

export function OpsTimelineSection({
  title,
  items,
  emptyLabel,
}: {
  title: string;
  items: TeamOpsEventItem[];
  emptyLabel?: string;
}) {
  return (
    <div>
      <SectionHeader title={title} />
      {items.length === 0 ? (
        <p className="text-sm" style={{ color: OPS.onVariant }}>
          {emptyLabel ?? "Nothing here yet"}
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.slice(0, 8).map((item) => (
            <div
              key={item.event_id || `${item.action_type}-${item.title}`}
              className="flex items-center gap-2.5 rounded-xl p-3"
              style={{ background: OPS.surfaceLow }}
            >
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
                style={{ background: OPS.surfaceHigh }}
              >
                <span style={{ color: OPS.secondary }}>•</span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold">{item.title}</p>
                <p className="text-[11px]" style={{ color: OPS.onVariant }}>
                  {item.action_type.replace(/_/g, " ")}
                  {item.occurred_at ? ` · ${formatOccurredAt(item.occurred_at)}` : ""}
                </p>
              </div>
              <Badge text="Done" tone={OPS.primary} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function OpsMilestonesSection({ items }: { items: OpsMilestoneItem[] }) {
  return (
    <div>
      <SectionHeader title="Progress Snapshot" />
      {items.length === 0 ? (
        <p className="text-sm" style={{ color: OPS.onVariant }}>
          No milestones yet
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          {items.slice(0, 4).map((item, idx) => (
            <OpsCard key={item.event_id || `${item.kind}-${item.title}-${idx}`}>
              <p className="text-[10px] uppercase" style={{ color: OPS.onVariant }}>
                {item.kind || "Milestone"}
              </p>
              <p className="mt-1 text-sm font-semibold">{item.title}</p>
              {item.occurred_at ? (
                <p className="mt-1 text-[11px]" style={{ color: OPS.onVariant }}>
                  {formatOccurredAt(item.occurred_at)}
                </p>
              ) : null}
            </OpsCard>
          ))}
        </div>
      )}
    </div>
  );
}

export function OpsSummaryStats({
  stats,
}: {
  stats: {
    budget_used_percent?: number | null;
    approvals?: number | null;
    open_issues?: number | null;
    vendors?: number | null;
    improvements?: number | null;
  };
}) {
  const rows = [
    {
      label: "Budget used",
      value:
        stats.budget_used_percent != null
          ? `${Math.round(Number(stats.budget_used_percent))}%`
          : "—",
    },
    { label: "Approvals", value: stats.approvals != null ? String(stats.approvals) : "—" },
    { label: "Issues", value: stats.open_issues != null ? String(stats.open_issues) : "—" },
    { label: "Vendors", value: stats.vendors != null ? String(stats.vendors) : "—" },
    {
      label: "Improvements",
      value: stats.improvements != null ? String(stats.improvements) : "—",
    },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {rows.map((row) => (
        <OpsCard key={row.label}>
          <p className="text-xs" style={{ color: OPS.onVariant }}>
            {row.label}
          </p>
          <p className="mt-1 text-sm font-medium">{row.value}</p>
        </OpsCard>
      ))}
    </div>
  );
}

export function OpsManageBar({ onQuickAdd }: { onQuickAdd?: () => void }) {
  if (!onQuickAdd) return null;
  return (
    <OpsCard>
      <p className="text-base font-bold" style={{ fontFamily: OPS.fontDisplay }}>
        Continue Managing
      </p>
      <p className="mt-1 text-xs" style={{ color: OPS.onVariant }}>
        Open your Operations workspace
      </p>
      <button
        type="button"
        className="mt-2 text-xs font-semibold"
        style={{ color: OPS.secondary }}
        onClick={onQuickAdd}
      >
        Quick Add →
      </button>
    </OpsCard>
  );
}

"use client";

import type { RunwayMomentsResponse, RunwayPulseResponse, TeamOpsEventItem } from "@/lib/api/businessActive";
import { formatMinorCurrency } from "@/lib/business/runwayApiMappers";
import { RUNWAY, runwayBandColor, formatOccurredAt, formatRunwayMonths } from "./runwayTheme";

export function RunwayScrollShell({
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
        background: RUNWAY.bg,
        color: RUNWAY.onSurface,
        fontFamily: RUNWAY.fontBody,
      }}
    >
      {children}
    </div>
  );
}

export function RunwayCard({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl border p-4 ${className}`}
      style={{ background: RUNWAY.surface, borderColor: `${RUNWAY.outline}33` }}
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
      <p className="text-sm font-semibold" style={{ fontFamily: RUNWAY.fontDisplay }}>
        {title}
      </p>
      {trailing && onTrailing ? (
        <button type="button" className="text-xs font-semibold" style={{ color: RUNWAY.primary }} onClick={onTrailing}>
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

export function RunwayHealthHero({ data }: { data: RunwayPulseResponse }) {
  const health = data.hero.runway_health ?? data.runway_health.health;
  const band = health?.band ?? "empty";
  const tone = runwayBandColor(band);
  return (
    <RunwayCard className="!bg-gradient-to-b from-[#292932] to-[#1b1b23]">
      <div className="flex items-start justify-between gap-3">
        <p className="text-[11px] font-semibold uppercase tracking-wide" style={{ color: RUNWAY.onVariant }}>
          Runway Health
        </p>
        <Badge text={health?.label ?? "Not started"} tone={tone} />
      </div>
      <p className="mt-2 text-3xl font-bold" style={{ color: tone, fontFamily: RUNWAY.fontDisplay }}>
        {health?.label ?? "Not started"}
      </p>
      <h2 className="mt-1 text-lg font-semibold" style={{ fontFamily: RUNWAY.fontDisplay }}>
        {data.hero.title}
      </h2>
      <p className="mt-2 text-xs" style={{ color: RUNWAY.onVariant }}>
        Overall Business Runway health from cash position, burn, revenue, and collections.
      </p>
      {data.runway_months.runway_months != null ? (
        <p className="mt-2 text-sm font-semibold" style={{ color: RUNWAY.primary }}>
          {formatRunwayMonths(data.runway_months.runway_months)} runway
        </p>
      ) : null}
    </RunwayCard>
  );
}

export function RunwayKpiGrid({ data }: { data: RunwayPulseResponse }) {
  const currency = data.operating_currency ?? "INR";
  const collection = data.collection_rate.collection_rate_percent;
  const kpis = [
    {
      label: "Cash Position",
      value: formatMinorCurrency(data.cash_position.cash_available_minor, currency),
      bar: null as number | null,
    },
    {
      label: "Burn Rate",
      value: formatMinorCurrency(data.monthly_burn.monthly_burn_minor, currency),
      bar: null,
    },
    {
      label: "Revenue Trend",
      value: formatMinorCurrency(data.revenue_trend.monthly_revenue_minor, currency),
      status: data.revenue_trend.revenue_status ?? undefined,
      bar: null,
    },
    {
      label: "Collection Rate",
      value: collection != null ? `${Math.round(collection)}%` : "—",
      status: collection != null && collection >= 80 ? "Excellent" : undefined,
      bar: collection != null ? Math.min(100, Math.max(0, collection)) / 100 : null,
    },
  ];
  return (
    <div>
      <SectionHeader title="Health Drivers" />
      <div className="-mx-1 flex gap-2 overflow-x-auto pb-1">
        {kpis.map((kpi) => (
          <div
            key={kpi.label}
            className="min-w-[7.5rem] flex-1 rounded-xl border p-3"
            style={{ background: RUNWAY.surfaceLow, borderColor: `${RUNWAY.outline}33` }}
          >
            <p className="text-[10px]" style={{ color: RUNWAY.onVariant }}>
              {kpi.label}
            </p>
            <p className="mt-1 truncate text-sm font-bold">{kpi.value}</p>
            {kpi.status ? (
              <p className="mt-0.5 text-[10px]" style={{ color: RUNWAY.primary }}>
                {kpi.status}
              </p>
            ) : null}
            {kpi.bar != null ? (
              <div className="mt-2 h-1 overflow-hidden rounded-full" style={{ background: `${RUNWAY.onVariant}26` }}>
                <div className="h-full rounded-full" style={{ width: `${kpi.bar * 100}%`, background: RUNWAY.primary }} />
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function attentionTone(severity?: string, kind?: string): { label: string; tone: string } {
  const sev = severity?.toLowerCase();
  if (sev === "high") return { label: "High", tone: RUNWAY.error };
  if (sev === "medium" || sev === "med") return { label: "Med", tone: RUNWAY.tertiary };
  if (sev === "low") return { label: "Low", tone: RUNWAY.primary };
  if (kind === "runway_risks" || kind === "critical") return { label: "High", tone: RUNWAY.error };
  return { label: "Med", tone: RUNWAY.tertiary };
}

export function RunwayAttentionCards({
  items,
  onViewAll,
}: {
  items: RunwayPulseResponse["attention_items"]["items"];
  onViewAll?: () => void;
}) {
  return (
    <div>
      <SectionHeader
        title="Attention Needed"
        trailing={items.length ? `View All (${items.length})` : undefined}
        onTrailing={onViewAll}
      />
      {items.length === 0 ? (
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          Nothing needs attention.
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((item) => {
            const { label, tone } = attentionTone(item.severity, item.kind);
            return (
              <div
                key={`${item.kind}-${item.label}`}
                className="flex items-center gap-3 rounded-xl border p-3"
                style={{ background: RUNWAY.surfaceLow, borderColor: `${RUNWAY.outline}33` }}
              >
                <div
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-sm font-bold"
                  style={{ background: `${tone}26`, color: tone }}
                >
                  !
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold">{item.label}</p>
                  <div className="mt-1 flex items-center gap-2">
                    <Badge text={label} tone={tone} />
                    <span className="text-[10px]" style={{ color: RUNWAY.onVariant }}>
                      {item.description?.trim() || "Needs review"}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function RunwaySignalsGrid({ items }: { items: RunwayPulseResponse["signals"]["items"] }) {
  if (!items.length) return null;
  return (
    <div>
      <SectionHeader title="Signals" />
      <div className="-mx-1 flex gap-2 overflow-x-auto pb-1">
        {items.map((item) => {
          const tone =
            item.severity?.toLowerCase() === "high" || item.severity?.toLowerCase() === "negative"
              ? RUNWAY.error
              : RUNWAY.primary;
          const change = item.change_percent;
          return (
            <div
              key={`${item.signal_type}-${item.label}-${item.title}`}
              className="min-w-[10rem] rounded-xl border p-3"
              style={{ background: RUNWAY.surfaceLow, borderColor: `${RUNWAY.outline}33` }}
            >
              <p className="text-xs font-semibold">{item.title ?? item.label ?? item.signal_type}</p>
              <p className="mt-1 text-[11px]" style={{ color: tone }}>
                {item.summary?.trim() ||
                  (change != null ? `${change >= 0 ? "+" : ""}${Math.round(change)}%` : "Signal")}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function RunwayActivityFeed({
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
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          No activity yet
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.slice(0, 5).map((item) => (
            <div
              key={item.event_id}
              className="flex items-center gap-3 rounded-xl p-3"
              style={{ background: RUNWAY.surfaceLow }}
            >
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold"
                style={{ background: `${RUNWAY.primary}26`, color: RUNWAY.primary }}
              >
                {(item.title || "?").slice(0, 1).toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{item.title}</p>
                <p className="text-[11px]" style={{ color: RUNWAY.onVariant }}>
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

export function RunwayNextAction({
  item,
  onQuickAdd,
}: {
  item: RunwayPulseResponse["next_best_action"]["item"];
  onQuickAdd?: () => void;
}) {
  if (!item) return null;
  return (
    <RunwayCard>
      <p className="text-base font-bold" style={{ fontFamily: RUNWAY.fontDisplay }}>
        {item.label}
      </p>
      {item.reason ? (
        <p className="mt-1 text-xs" style={{ color: RUNWAY.onVariant }}>
          {item.reason}
        </p>
      ) : null}
      {onQuickAdd ? (
        <button
          type="button"
          className="mt-3 w-full rounded-xl px-4 py-3 text-sm font-semibold"
          style={{ background: RUNWAY.primaryContainer, color: RUNWAY.onSurface }}
          onClick={onQuickAdd}
        >
          {item.cta_label ?? "Take Action"}
        </button>
      ) : null}
    </RunwayCard>
  );
}

export function RunwayMomentsHero({
  data,
  onQuickAdd,
}: {
  data: RunwayMomentsResponse;
  onQuickAdd?: () => void;
}) {
  const hub = data.runway_hub ?? {};
  const currency = String(hub.operating_currency ?? data.cash_available.operating_currency ?? "INR");
  const cash = Number(hub.cash_available_minor ?? data.cash_available.cash_available_minor ?? 0);
  const burn = Number(hub.monthly_burn_minor ?? 0);
  const months = (hub.runway_months as number | null | undefined) ?? data.journey_hero.runway_months ?? data.runway_months.runway_months;
  const isActive = data.journey_hero.is_active === true || data.status.toUpperCase() === "ACTIVE";

  return (
    <RunwayCard className="!bg-gradient-to-b from-[#292932] to-[#1b1b23]">
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-xl font-bold" style={{ fontFamily: RUNWAY.fontDisplay }}>
          {data.journey_hero.title}
        </h2>
        {isActive ? <Badge text="Active" tone={RUNWAY.primary} /> : null}
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
        <div>
          <p className="text-sm font-bold">{formatRunwayMonths(months)}</p>
          <p className="text-[10px]" style={{ color: RUNWAY.onVariant }}>
            Remaining
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold">{formatMinorCurrency(cash, currency)}</p>
          <p className="text-[10px]" style={{ color: RUNWAY.onVariant }}>
            Cash Available
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm font-bold">{formatMinorCurrency(burn, currency)}</p>
          <p className="text-[10px]" style={{ color: RUNWAY.onVariant }}>
            Monthly Burn
          </p>
        </div>
      </div>
      {onQuickAdd ? (
        <button
          type="button"
          className="mt-4 rounded-full px-4 py-2 text-sm font-semibold"
          style={{ background: RUNWAY.primaryContainer, color: RUNWAY.onSurface }}
          onClick={onQuickAdd}
        >
          Quick add
        </button>
      ) : null}
    </RunwayCard>
  );
}

export function RunwayTimelineSection({ items }: { items: TeamOpsEventItem[] }) {
  return (
    <div>
      <SectionHeader title="Moment Timeline" />
      {items.length === 0 ? (
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          No events yet
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.slice(0, 8).map((item) => (
            <div
              key={item.event_id}
              className="flex items-center gap-3 rounded-xl p-3"
              style={{ background: RUNWAY.surfaceLow }}
            >
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
                style={{ background: RUNWAY.surfaceHigh, color: RUNWAY.primary }}
              >
                •
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{item.title}</p>
                <p className="text-[11px]" style={{ color: RUNWAY.onVariant }}>
                  {item.subtitle ?? item.action_type.replace(/_/g, " ")} · {formatOccurredAt(item.occurred_at)}
                </p>
              </div>
              <Badge text="Done" tone={RUNWAY.primary} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function RunwayProgressSnapshot({ data }: { data: RunwayMomentsResponse }) {
  const hub = data.runway_hub ?? {};
  const currency = String(hub.operating_currency ?? "INR");
  const cash = Number(hub.cash_available_minor ?? data.cash_available.cash_available_minor ?? 0);
  const burn = Number(hub.monthly_burn_minor ?? 0);
  const months = (hub.runway_months as number | null | undefined) ?? data.runway_months.runway_months;
  const goal = data.runway_months.runway_goal_months ?? 12;
  const activity = data.journey_hero.activity_count ?? 0;
  const monthsPct = months != null && goal > 0 ? Math.min(1, Math.max(0, months / goal)) : null;

  const cards = [
    { label: "Runway months", value: formatRunwayMonths(months), bar: monthsPct },
    { label: "Cash", value: formatMinorCurrency(cash, currency), bar: null as number | null },
    { label: "Monthly burn", value: formatMinorCurrency(burn, currency), bar: null },
    { label: "Activity", value: activity > 0 ? String(activity) : "—", bar: null },
  ];

  return (
    <div>
      <SectionHeader title="Progress Snapshot" />
      <div className="grid grid-cols-2 gap-2">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border p-3"
            style={{ background: RUNWAY.surfaceLow, borderColor: `${RUNWAY.outline}33` }}
          >
            <p className="text-[10px]" style={{ color: RUNWAY.onVariant }}>
              {card.label}
            </p>
            <p className="mt-1 text-sm font-bold">{card.value}</p>
            {card.bar != null ? (
              <div className="mt-2 h-1 overflow-hidden rounded-full" style={{ background: `${RUNWAY.onVariant}26` }}>
                <div className="h-full rounded-full" style={{ width: `${card.bar * 100}%`, background: RUNWAY.primary }} />
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

export function RunwayHighlights({ items }: { items: TeamOpsEventItem[] }) {
  return (
    <div>
      <p className="text-[10px] font-bold uppercase tracking-wide" style={{ color: RUNWAY.primary }}>
        Recent Wins
      </p>
      <SectionHeader title="Recent Highlights" />
      {items.length === 0 ? (
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          No highlights yet
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {items.slice(0, 3).map((item) => (
            <div key={item.event_id} className="flex gap-3">
              <div className="w-0.5 shrink-0 rounded-full" style={{ background: RUNWAY.primary }} />
              <div>
                <p className="text-sm font-semibold">{item.title}</p>
                <p className="text-[11px]" style={{ color: RUNWAY.onVariant }}>
                  {formatOccurredAt(item.occurred_at) || item.action_type}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function RunwayManageBar({ onQuickAdd }: { onQuickAdd?: () => void }) {
  return (
    <div>
      <p className="text-base font-bold" style={{ fontFamily: RUNWAY.fontDisplay }}>
        Continue Managing
      </p>
      <p className="mt-1 text-xs" style={{ color: RUNWAY.onVariant }}>
        Open your Runway workspace to make deeper changes.
      </p>
      <div className="mt-3 flex items-center gap-3">
        <button
          type="button"
          className="flex-1 rounded-xl px-4 py-3 text-sm font-semibold"
          style={{ background: RUNWAY.primaryContainer, color: RUNWAY.onSurface }}
          onClick={onQuickAdd}
        >
          Manage Runway
        </button>
        {onQuickAdd ? (
          <button
            type="button"
            className="flex h-12 w-12 items-center justify-center rounded-full text-xl font-bold"
            style={{ background: RUNWAY.surfaceHigh, color: RUNWAY.primary }}
            onClick={onQuickAdd}
            aria-label="Quick add"
          >
            +
          </button>
        ) : null}
      </div>
    </div>
  );
}

export function RunwayLaneSection({
  title,
  items,
  emptyLabel,
}: {
  title: string;
  items: TeamOpsEventItem[];
  emptyLabel?: string;
}) {
  return (
    <RunwayCard>
      <p className="mb-2 text-sm font-medium">{title}</p>
      {items.length === 0 ? (
        <p className="text-sm" style={{ color: RUNWAY.onVariant }}>
          {emptyLabel ?? "Nothing here yet"}
        </p>
      ) : (
        <ul className="flex flex-col gap-2">
          {items.map((item) => (
            <li key={item.event_id} className="text-sm">
              {item.title}
            </li>
          ))}
        </ul>
      )}
    </RunwayCard>
  );
}

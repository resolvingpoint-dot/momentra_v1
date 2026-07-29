"use client";

import { useState, type ReactNode } from "react";
import type {
  TeamOpsEventItem,
  TeamOpsHealth,
  TeamOpsHealthDriver,
  TeamOpsProgressMetric,
  TeamOpsPulseResponse,
} from "@/lib/api/businessActive";
import { AnimatedNumber } from "@/lib/motion/AnimatedNumber";
import { TEAM_OPS, formatOccurredAt, healthBandColor } from "./teamOpsTheme";
import { TeamOpsEmptyLine, TeamOpsSectionCard } from "./shared";

export function StitchBadge({ text, tone }: { text: string; tone: string }) {
  return (
    <span
      className="rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-wider"
      style={{ background: `${tone}33`, color: tone }}
    >
      {text}
    </span>
  );
}

export function StitchSectionHeader({
  title,
  trailing,
  onTrailing,
}: {
  title: string;
  trailing?: string;
  onTrailing?: () => void;
}) {
  return (
    <div className="mb-3 flex items-center justify-between gap-2">
      <h3 className="text-sm font-semibold" style={{ color: TEAM_OPS.onSurface }}>
        {title}
      </h3>
      {trailing && onTrailing ? (
        <button
          type="button"
          className="text-[11px] font-bold"
          style={{ color: TEAM_OPS.primary }}
          onClick={onTrailing}
        >
          {trailing}
        </button>
      ) : null}
    </div>
  );
}

function sparkValues(data: TeamOpsPulseResponse): number[] {
  const k = data.kpis;
  return [
    k.participation,
    k.pending_approvals,
    k.open_issues,
    k.recognitions,
    k.meetings,
    k.escalations,
  ];
}

export function StitchHealthHero({ data }: { data: TeamOpsPulseResponse }) {
  const health = data.hero.overall_team_health ?? data.kpis.overall_team_health;
  const score = health?.score;
  const values = sparkValues(data);
  const maxV = Math.max(...values, 1);

  return (
    <TeamOpsSectionCard gradient>
      <div className="mb-2 flex items-start justify-between gap-3">
        <p className="text-sm font-medium" style={{ color: TEAM_OPS.onVariant }}>
          Team Health
        </p>
        {health ? (
          <StitchBadge text={health.label} tone={healthBandColor(health.band)} />
        ) : null}
      </div>
      <div className="mb-3 flex items-end gap-3">
        {typeof score === "number" ? (
          <div className="flex items-end gap-1">
            <span
              className="text-5xl font-bold tracking-tight"
              style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
            >
              <AnimatedNumber value={Math.round(score)} />
            </span>
            <span className="mb-2 text-sm" style={{ color: TEAM_OPS.onVariant }}>
              /{health?.max_score ?? 100}
            </span>
          </div>
        ) : (
          <span
            className="text-3xl font-bold"
            style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
          >
            {health?.label ?? "Not started"}
          </span>
        )}
        <div className="ml-auto flex h-12 items-end gap-1">
          {values.map((v, i) => (
            <div
              key={i}
              className="w-1.5 rounded-t-sm"
              style={{
                height: `${Math.max(4, (v / maxV) * 40)}px`,
                background: `${TEAM_OPS.primary}${Math.round(40 + (v / maxV) * 60).toString(16).padStart(2, "0")}`,
              }}
            />
          ))}
        </div>
      </div>
      <h2 className="mb-1 text-xl font-bold" style={{ color: TEAM_OPS.onSurface }}>
        {data.hero.title}
      </h2>
      <p className="text-[11px] leading-relaxed" style={{ color: TEAM_OPS.onVariant }}>
        Overall Team Operations health from participation, approvals, issues, and escalations.
      </p>
    </TeamOpsSectionCard>
  );
}

export function StitchHealthDrivers({ drivers }: { drivers: TeamOpsHealthDriver[] }) {
  if (!drivers.length) return <TeamOpsEmptyLine label="No health drivers yet." />;
  return (
    <section>
      <StitchSectionHeader title="Health Drivers" />
      <div className="flex gap-2 overflow-x-auto pb-1">
        {drivers.map((driver) => (
          <div
            key={driver.driver_code}
            className="min-w-[120px] flex-shrink-0 rounded-xl border p-3"
            style={{
              background: TEAM_OPS.surfaceLow,
              borderColor: `${TEAM_OPS.outline}1a`,
            }}
          >
            <p className="mb-1 truncate text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
              {driver.driver_name}
            </p>
            <p className="text-lg font-bold" style={{ color: TEAM_OPS.onSurface }}>
              <AnimatedNumber value={Math.round(driver.score)} />
            </p>
            <p className="mb-2 text-[9px] capitalize" style={{ color: TEAM_OPS.primary }}>
              {driver.status}
            </p>
            <div className="h-1 w-full rounded-full" style={{ background: `${TEAM_OPS.outline}33` }}>
              <div
                className="h-1 rounded-full"
                style={{
                  width: `${Math.min(100, driver.score)}%`,
                  background: TEAM_OPS.primary,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function StitchAttentionCards({
  items,
  onViewAll,
}: {
  items: TeamOpsPulseResponse["attention"]["items"];
  onViewAll?: () => void;
}) {
  return (
    <section>
      <StitchSectionHeader
        title="Attention Needed"
        trailing={items.length ? `View All (${items.length})` : undefined}
        onTrailing={onViewAll}
      />
      {!items.length ? (
        <TeamOpsEmptyLine label="Nothing needs attention." />
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const tone =
              item.severity === "high"
                ? TEAM_OPS.error
                : item.severity === "medium"
                  ? TEAM_OPS.warning
                  : TEAM_OPS.primary;
            return (
              <div
                key={`${item.kind}-${item.label}`}
                className="flex items-center gap-3 rounded-xl border p-4"
                style={{
                  background: TEAM_OPS.surfaceLow,
                  borderColor: `${TEAM_OPS.outline}33`,
                }}
              >
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-lg"
                  style={{ background: `${tone}22` }}
                >
                  <span style={{ color: tone }}>!</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold" style={{ color: TEAM_OPS.onSurface }}>
                    {item.label}
                  </p>
                  {item.description ? (
                    <p className="text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
                      {item.description}
                    </p>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

export function StitchSignalsGrid({
  items,
}: {
  items: TeamOpsPulseResponse["signals"]["items"];
}) {
  if (!items.length) return <TeamOpsEmptyLine label="No signals yet." />;
  return (
    <section>
      <StitchSectionHeader title="Signals" />
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {items.map((item, index) => (
          <div
            key={`${item.signal_type ?? "signal"}-${index}`}
            className="rounded-xl border p-3 text-center"
            style={{
              background: TEAM_OPS.surfaceLow,
              borderColor: `${TEAM_OPS.outline}1a`,
            }}
          >
            <p className="mb-2 text-lg" style={{ color: TEAM_OPS.primary }}>
              ~
            </p>
            <p className="text-[10px] font-medium leading-tight" style={{ color: TEAM_OPS.onSurface }}>
              {item.label ?? item.title}
            </p>
            {typeof item.change_percent === "number" ? (
              <p className="mt-1 text-[9px]" style={{ color: TEAM_OPS.primary }}>
                {item.change_percent > 0 ? "+" : ""}
                {item.change_percent}% vs last 7 days
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}

export function StitchActivityFeed({
  items,
  onViewAll,
}: {
  items: TeamOpsEventItem[];
  onViewAll?: () => void;
}) {
  return (
    <section>
      <StitchSectionHeader
        title="Recent Activity Feed"
        trailing={items.length ? "View All Activity" : undefined}
        onTrailing={onViewAll}
      />
      {!items.length ? (
        <TeamOpsEmptyLine label="No activity yet — use Action Center to record the first update." />
      ) : (
        <div className="space-y-3">
          {items.slice(0, 8).map((item) => (
            <div key={item.event_id} className="flex items-center gap-3">
              <div
                className="flex h-8 w-8 items-center justify-center rounded-full text-[11px] font-bold"
                style={{ background: `${TEAM_OPS.primary}33`, color: TEAM_OPS.primary }}
              >
                {(item.subtitle ?? item.title).slice(0, 2).toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <p className="truncate text-xs font-semibold" style={{ color: TEAM_OPS.onSurface }}>
                    {item.title || item.action_type}
                  </p>
                  <span className="text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
                    {formatOccurredAt(item.occurred_at)}
                  </span>
                </div>
                {item.subtitle ? (
                  <p className="truncate text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
                    {item.subtitle}
                  </p>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export function StitchNextAction({
  item,
  onQuickAdd,
}: {
  item: TeamOpsPulseResponse["next_action"]["item"];
  onQuickAdd?: () => void;
}) {
  return (
    <section>
      <p
        className="mb-3 text-[11px] font-semibold uppercase tracking-wider opacity-80"
        style={{ color: TEAM_OPS.onVariant }}
      >
        Recommended Next Action
      </p>
      {!item ? (
        <TeamOpsEmptyLine label="No recommended next step." />
      ) : (
        <div
          className="flex items-center justify-between gap-3 rounded-2xl border p-4"
          style={{
            background: TEAM_OPS.surfaceLow,
            borderColor: `${TEAM_OPS.primary}44`,
          }}
        >
          <div>
            <p className="text-sm font-bold" style={{ color: TEAM_OPS.onSurface }}>
              {item.label}
            </p>
            <p className="text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
              {item.reason.replace(/_/g, " ")}
            </p>
          </div>
          {onQuickAdd ? (
            <button
              type="button"
              className="rounded-lg px-3 py-2 text-[11px] font-bold"
              style={{ background: TEAM_OPS.primary, color: "#1000a9" }}
              onClick={onQuickAdd}
            >
              {item.cta_label ?? "Take Action"}
            </button>
          ) : null}
        </div>
      )}
    </section>
  );
}

export function StitchMomentsHero({
  title,
  memberCount,
  pendingApprovals,
  openIssues,
  activityCount,
  isActive,
}: {
  title: string;
  memberCount: number;
  pendingApprovals: number;
  openIssues: number;
  activityCount: number;
  isActive?: boolean;
}) {
  const stats = [
    { label: "Members", value: memberCount },
    { label: "Pending", value: pendingApprovals },
    { label: "Open issues", value: openIssues },
  ];
  return (
    <TeamOpsSectionCard gradient>
      <div className="mb-4 flex justify-end">{isActive ? <StitchBadge text="Active" tone={TEAM_OPS.success} /> : null}</div>
      <div className="mb-5 flex items-start gap-4">
        <div
          className="flex h-14 w-14 items-center justify-center rounded-xl text-2xl"
          style={{ background: `${TEAM_OPS.primaryContainer}55`, color: TEAM_OPS.primary }}
        >
          👥
        </div>
        <div>
          <h2 className="text-xl font-bold" style={{ color: TEAM_OPS.onSurface }}>
            {title}
          </h2>
          <p className="text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
            {activityCount} logged activities
          </p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-0 min-w-0">
        {stats.map((stat, index) => (
          <div
            key={stat.label}
            className="min-w-0 text-center px-1"
            style={{
              borderLeft: index === 1 ? `1px solid ${TEAM_OPS.outline}33` : undefined,
              borderRight: index === 1 ? `1px solid ${TEAM_OPS.outline}33` : undefined,
            }}
          >
            <p className="text-3xl font-bold" style={{ color: TEAM_OPS.onSurface }}>
              <AnimatedNumber value={stat.value} />
            </p>
            <p className="text-[10px] uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
              {stat.label}
            </p>
          </div>
        ))}
      </div>
    </TeamOpsSectionCard>
  );
}

export function StitchTimelineSection({
  items,
}: {
  items: TeamOpsEventItem[];
}) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? items : items.slice(0, 5);
  return (
    <section>
      <StitchSectionHeader
        title="Moment Timeline"
        trailing={items.length > 5 ? (expanded ? "Show Less" : "Show More") : undefined}
        onTrailing={items.length > 5 ? () => setExpanded((v) => !v) : undefined}
      />
      {!items.length ? (
        <TeamOpsEmptyLine label="Timeline is empty until activities are recorded." />
      ) : (
        <div className="space-y-2">
          {visible.map((item) => (
            <div
              key={item.event_id}
              className="flex items-center gap-3 rounded-xl p-4"
              style={{ background: TEAM_OPS.surface }}
            >
              <div
                className="flex h-10 w-10 items-center justify-center rounded-lg"
                style={{ background: `${TEAM_OPS.primary}22`, color: TEAM_OPS.primary }}
              >
                •
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium" style={{ color: TEAM_OPS.onSurface }}>
                    {item.title || item.action_type}
                  </p>
                  <span className="text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
                    {formatOccurredAt(item.occurred_at)}
                  </span>
                </div>
                {item.subtitle ? (
                  <p className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
                    {item.subtitle}
                  </p>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export function StitchProgressSnapshot({ items }: { items: TeamOpsProgressMetric[] }) {
  if (!items.length) return <TeamOpsEmptyLine label="Progress snapshot will appear after activity is logged." />;
  return (
    <section>
      <p
        className="mb-3 text-xs font-semibold uppercase tracking-widest"
        style={{ color: TEAM_OPS.onVariant }}
      >
        Progress Snapshot
      </p>
      <div className="grid grid-cols-2 gap-2">
        {items.map((metric) => (
          <div
            key={metric.metric_code}
            className="rounded-xl border px-4 py-3"
            style={{
              background: TEAM_OPS.surfaceLow,
              borderColor: `${TEAM_OPS.outline}33`,
            }}
          >
            <p className="mb-1 text-[10px] uppercase" style={{ color: TEAM_OPS.onVariant }}>
              {metric.metric_name}
            </p>
            <p className="text-2xl font-bold" style={{ color: TEAM_OPS.onSurface }}>
              <AnimatedNumber value={Math.round(metric.score)} />%
            </p>
            {typeof metric.delta === "number" ? (
              <p className="text-[10px]" style={{ color: metric.delta >= 0 ? TEAM_OPS.success : TEAM_OPS.error }}>
                {metric.delta > 0 ? "+" : ""}
                {metric.delta}% vs last 7 days
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}

export function StitchHighlights({ items }: { items: TeamOpsEventItem[] }) {
  return (
    <section>
      <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest" style={{ color: TEAM_OPS.primary }}>
        Recent Wins
      </p>
      <StitchSectionHeader title="Recent Highlights" />
      {!items.length ? (
        <TeamOpsEmptyLine label="Highlights appear as team activities are logged." />
      ) : (
        <div className="space-y-2">
          {items.slice(0, 4).map((item) => (
            <div
              key={item.event_id}
              className="flex items-center gap-3 rounded-xl p-4"
              style={{ background: TEAM_OPS.surface }}
            >
              <div
                className="flex h-10 w-10 items-center justify-center rounded-full"
                style={{ background: `${TEAM_OPS.primary}22`, color: TEAM_OPS.primary }}
              >
                ★
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium" style={{ color: TEAM_OPS.onSurface }}>
                  {item.title || item.action_type}
                </p>
                {item.subtitle ? (
                  <p className="text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
                    {item.subtitle}
                  </p>
                ) : null}
              </div>
              <span className="text-[10px] whitespace-nowrap" style={{ color: TEAM_OPS.onVariant }}>
                {formatOccurredAt(item.occurred_at)}
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export function StitchContinueManaging({ onQuickAdd }: { onQuickAdd?: () => void }) {
  return (
    <section
      className="rounded-2xl border p-6 text-center"
      style={{
        background: TEAM_OPS.surfaceLow,
        borderColor: `${TEAM_OPS.outline}33`,
      }}
    >
      <h3 className="mb-1 text-lg font-bold" style={{ color: TEAM_OPS.onSurface }}>
        Continue Managing
      </h3>
      <p className="mb-5 text-sm" style={{ color: TEAM_OPS.onVariant }}>
        Open your Team Operations workspace
      </p>
      {onQuickAdd ? (
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="flex-1 rounded-xl py-3 text-sm font-bold"
            style={{ background: TEAM_OPS.primaryContainer, color: "#0d0096" }}
            onClick={onQuickAdd}
          >
            Manage Team Operations
          </button>
          <button type="button" className="flex flex-col items-center gap-1" onClick={onQuickAdd}>
            <div
              className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-dashed"
              style={{ borderColor: TEAM_OPS.primary, color: TEAM_OPS.primary }}
            >
              +
            </div>
            <span className="text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
              Quick Add
            </span>
          </button>
        </div>
      ) : null}
    </section>
  );
}

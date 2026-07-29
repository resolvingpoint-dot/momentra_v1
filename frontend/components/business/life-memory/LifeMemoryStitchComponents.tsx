"use client";

import type { CSSProperties, ReactNode } from "react";
import type {
  BusinessLifeDimension,
  BusinessLifeHealth,
  BusinessLifeSignal,
  BusinessMemoryEvent,
  BusinessMemoryJourneyItem,
  BusinessMemoryMemoryItem,
  BusinessMemorySourceFilter,
  BusinessMemorySummary,
  TeamOpsEventItem,
} from "@/lib/api/businessActive";
import {
  formatOccurredAt,
  healthBandColor,
  TEAM_OPS,
} from "@/components/business/active/team-operations/shared/teamOpsTheme";
import { TeamOpsEmptyLine } from "@/components/business/active/team-operations/shared/shared";

const JAKARTA = TEAM_OPS.fontBody;

/** Band ordinal for ring fill — no composite score. */
function bandProgress(band?: string): number {
  switch ((band || "empty").toLowerCase()) {
    case "healthy":
      return 0.85;
    case "needs_attention":
      return 0.55;
    case "at_risk":
      return 0.3;
    case "critical":
      return 0.15;
    default:
      return 0.08;
  }
}

export function LmGlassCard({
  children,
  glow = false,
  className = "",
  style,
}: {
  children: ReactNode;
  glow?: boolean;
  className?: string;
  style?: CSSProperties;
}) {
  return (
    <section
      className={`relative overflow-hidden rounded-3xl p-5 ${className}`}
      style={{
        background: "rgba(27, 27, 35, 0.72)",
        backdropFilter: "blur(12px)",
        border: `1px solid ${glow ? "rgba(99, 102, 241, 0.28)" : "rgba(255,255,255,0.08)"}`,
        boxShadow: glow ? "0 0 24px rgba(99, 102, 241, 0.12)" : undefined,
        fontFamily: JAKARTA,
        ...style,
      }}
    >
      {glow ? (
        <div
          className="pointer-events-none absolute -right-10 -top-10 h-48 w-48 rounded-full"
          style={{ background: "rgba(99, 102, 241, 0.12)", filter: "blur(48px)" }}
          aria-hidden
        />
      ) : null}
      <div className="relative">{children}</div>
    </section>
  );
}

export function LmNumberedHeader({
  index,
  title,
  trailing,
  onTrailing,
}: {
  index: number;
  title: string;
  trailing?: string;
  onTrailing?: () => void;
}) {
  return (
    <div className="mb-4 flex items-center justify-between gap-2">
      <div className="flex items-center gap-3">
        <span
          className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
          style={{ background: TEAM_OPS.primaryContainer }}
        >
          {index}
        </span>
        <h2
          className="text-base font-bold tracking-tight"
          style={{ color: TEAM_OPS.onSurface, fontFamily: JAKARTA }}
        >
          {title}
        </h2>
      </div>
      {trailing && onTrailing ? (
        <button
          type="button"
          className="text-xs font-medium"
          style={{ color: TEAM_OPS.primary }}
          onClick={onTrailing}
        >
          {trailing}
        </button>
      ) : null}
    </div>
  );
}

export function LmBadge({ text, tone }: { text: string; tone: string }) {
  return (
    <span
      className="rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-wider"
      style={{ background: `${tone}33`, color: tone, fontFamily: JAKARTA }}
    >
      {text}
    </span>
  );
}

/** Life health hero — band ring + label only (no 84/100). */
export function LmBandHero({
  health,
  activeMomentCount,
}: {
  health?: BusinessLifeHealth | null;
  activeMomentCount: number;
}) {
  const band = health?.band ?? "empty";
  const tone = healthBandColor(band);
  const progress = bandProgress(band);
  const r = 70;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - progress);

  return (
    <LmGlassCard glow>
      <LmNumberedHeader index={1} title="Business Life Health" />
      <div className="mb-4 flex flex-col items-center">
        <div className="relative mb-4 flex h-40 w-40 items-center justify-center">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 160 160" aria-hidden>
            <circle
              cx="80"
              cy="80"
              r={r}
              fill="transparent"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="8"
            />
            <circle
              cx="80"
              cy="80"
              r={r}
              fill="transparent"
              stroke={tone}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={c}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="absolute flex flex-col items-center px-2 text-center">
            <span
              className="text-2xl font-extrabold leading-tight"
              style={{ color: tone, fontFamily: JAKARTA }}
            >
              {health?.label ?? "Not started"}
            </span>
          </div>
        </div>
        <p
          className="max-w-xs text-center text-sm leading-relaxed"
          style={{ color: TEAM_OPS.onVariant }}
        >
          {health?.description ??
            "Overall business health from operational discipline, execution quality, financial resilience, vendor reliability, and team participation."}
        </p>
        <p
          className="mt-4 text-[10px] uppercase tracking-wider"
          style={{ color: TEAM_OPS.onVariant }}
        >
          {activeMomentCount} active business moment{activeMomentCount === 1 ? "" : "s"}
          {health?.active_dimension_count != null
            ? ` · ${health.active_dimension_count} active dimension${
                health.active_dimension_count === 1 ? "" : "s"
              }`
            : ""}
        </p>
      </div>
    </LmGlassCard>
  );
}

export function LmSignalCards({
  signals,
  sectionIndex = 2,
}: {
  signals: BusinessLifeSignal[];
  sectionIndex?: number;
}) {
  if (!signals.length) return null;
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title="Business signals" />
      <div className="space-y-2">
        {signals.map((s, i) => {
          const tone =
            s.severity === "high"
              ? TEAM_OPS.error
              : s.severity === "medium"
                ? TEAM_OPS.tertiary
                : TEAM_OPS.primary;
          return (
            <div
              key={`${s.signal_type ?? "s"}-${i}`}
              className="flex items-start gap-3 rounded-xl border p-3"
              style={{
                background: "rgba(255,255,255,0.03)",
                borderColor: `${tone}33`,
              }}
            >
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-sm font-bold"
                style={{ background: `${tone}22`, color: tone }}
              >
                !
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold" style={{ color: TEAM_OPS.onSurface }}>
                  {s.label}
                </p>
                {s.count > 0 ? (
                  <p className="mt-0.5 text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
                    Observed {s.count}
                    {s.dimension ? ` · ${s.dimension.replace(/_/g, " ")}` : ""}
                  </p>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </LmGlassCard>
  );
}

export function LmDimensionChips({
  dimensions,
  sectionIndex = 3,
}: {
  dimensions: BusinessLifeDimension[];
  sectionIndex?: number;
}) {
  const active = dimensions.filter((d) => d.count > 0 || (d.band && d.band !== "empty"));
  if (!active.length) return null;
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title="Health dimensions" />
      <div className="grid grid-cols-2 gap-2">
        {active.map((d) => {
          const tone = healthBandColor(d.band);
          return (
            <div
              key={d.key}
              className="overflow-hidden rounded-xl border"
              style={{
                background: "rgba(255,255,255,0.03)",
                borderColor: `${TEAM_OPS.outline}33`,
              }}
            >
              <div className="h-1 w-full" style={{ background: tone }} />
              <div className="p-3">
                <p className="text-[10px] font-medium uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
                  {d.label}
                </p>
                <p className="mt-1 text-sm font-bold capitalize" style={{ color: tone, fontFamily: JAKARTA }}>
                  {(d.band || "empty").replace(/_/g, " ")}
                </p>
                <p className="text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
                  Count {d.count}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </LmGlassCard>
  );
}

function LmEventFeed({
  items,
  emptyLabel,
}: {
  items: TeamOpsEventItem[] | BusinessMemoryEvent[];
  emptyLabel: string;
}) {
  if (!items.length) return <TeamOpsEmptyLine label={emptyLabel} />;
  return (
    <ul className="space-y-2">
      {items.map((e, i) => {
        const id = "event_id" in e ? e.event_id : `row-${i}`;
        const title = e.title || ("action_type" in e ? e.action_type : "");
        const action = "action_type" in e ? e.action_type : "";
        const at = "occurred_at" in e ? e.occurred_at : undefined;
        const source =
          "source_moment_name" in e && e.source_moment_name ? e.source_moment_name : undefined;
        return (
          <li
            key={id || i}
            className="flex gap-3 rounded-xl border px-3 py-3"
            style={{
              background: "rgba(255,255,255,0.03)",
              borderColor: `${TEAM_OPS.outline}22`,
            }}
          >
            <div
              className="mt-0.5 h-2 w-2 shrink-0 rounded-full"
              style={{ background: TEAM_OPS.primaryContainer }}
            />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium" style={{ color: TEAM_OPS.onSurface }}>
                {title}
              </p>
              <p className="mt-0.5 text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
                {[action, at ? formatOccurredAt(at) : null, source].filter(Boolean).join(" · ")}
              </p>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export function LmSliceCard({
  index,
  title,
  band,
  count,
  state,
  items,
}: {
  index: number;
  title: string;
  band?: string | null;
  count: number;
  state?: string;
  items: TeamOpsEventItem[];
}) {
  return (
    <LmGlassCard>
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-3">
          <span
            className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
            style={{ background: TEAM_OPS.primaryContainer }}
          >
            {index}
          </span>
          <h2
            className="truncate text-base font-bold tracking-tight"
            style={{ color: TEAM_OPS.onSurface, fontFamily: JAKARTA }}
          >
            {title}
          </h2>
        </div>
        {band ? <LmBadge text={band.replace(/_/g, " ")} tone={healthBandColor(band)} /> : null}
      </div>
      <p className="mb-3 text-xs" style={{ color: TEAM_OPS.onVariant }}>
        Count: {count}
        {state ? ` · ${state}` : ""}
      </p>
      <LmEventFeed items={items} emptyLabel="No contribution items yet." />
    </LmGlassCard>
  );
}

export function LmTimeline({
  items,
  sectionIndex,
  title = "Business journey",
}: {
  items: Array<BusinessMemoryJourneyItem | { kind?: string; title: string; occurred_at?: string | null }>;
  sectionIndex: number;
  title?: string;
}) {
  if (!items.length) return null;
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title={title} />
      <ol className="relative ml-2 space-y-4 border-l border-white/10 pl-5">
        {items.map((item, i) => (
          <li key={`${item.kind}-${item.occurred_at}-${i}`} className="relative">
            <span
              className="absolute -left-[1.4rem] top-1.5 h-2.5 w-2.5 rounded-full"
              style={{
                background: TEAM_OPS.primaryContainer,
                boxShadow: `0 0 0 4px ${TEAM_OPS.surfaceLow}`,
              }}
            />
            <p className="text-sm font-semibold" style={{ color: TEAM_OPS.onSurface }}>
              {item.title}
            </p>
            {item.occurred_at ? (
              <p className="text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
                {formatOccurredAt(item.occurred_at)}
              </p>
            ) : null}
          </li>
        ))}
      </ol>
    </LmGlassCard>
  );
}

export function LmQuickActions({
  sectionIndex,
  onQuickAdd,
  onCreateMoment,
}: {
  sectionIndex: number;
  onQuickAdd?: () => void;
  onCreateMoment?: () => void;
}) {
  if (!onQuickAdd && !onCreateMoment) return null;
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title="Quick actions" />
      <div className="grid grid-cols-2 gap-3">
        {onCreateMoment ? (
          <button
            type="button"
            onClick={onCreateMoment}
            className="flex flex-col items-center justify-center gap-2 rounded-2xl px-3 py-6 text-center transition-opacity hover:opacity-90"
            style={{
              background: TEAM_OPS.primaryContainer,
              color: "#0d0096",
              fontFamily: JAKARTA,
            }}
          >
            <span className="text-2xl font-bold leading-none">+</span>
            <span className="text-xs font-bold uppercase tracking-wide">Create moment</span>
          </button>
        ) : null}
        {onQuickAdd ? (
          <button
            type="button"
            onClick={onQuickAdd}
            className="flex flex-col items-center justify-center gap-2 rounded-2xl border px-3 py-6 text-center transition-opacity hover:opacity-90"
            style={{
              background: "rgba(255,255,255,0.04)",
              borderColor: `${TEAM_OPS.outline}44`,
              color: TEAM_OPS.onSurface,
              fontFamily: JAKARTA,
              gridColumn: onCreateMoment ? undefined : "span 2",
            }}
          >
            <span className="text-lg" aria-hidden>
              ⌗
            </span>
            <span className="text-xs font-bold uppercase tracking-wide">Add activity</span>
          </button>
        ) : null}
      </div>
    </LmGlassCard>
  );
}

/** Memory hero — factual counts only, decorative ring, no strength score. */
export function LmMemoryHero({
  summary,
  activeMomentCount,
  eventCount,
}: {
  summary?: BusinessMemorySummary | null;
  activeMomentCount: number;
  eventCount: number;
}) {
  const signals = summary?.event_count ?? eventCount;
  const months = summary?.months_active ?? 0;
  const moments = summary?.active_moment_count ?? activeMomentCount;
  const hasActivity = signals > 0 || moments > 0;
  const tone = hasActivity ? TEAM_OPS.secondary : TEAM_OPS.onVariant;
  const progress = hasActivity ? Math.min(0.75, 0.2 + months * 0.05 + Math.min(signals, 40) * 0.01) : 0.08;
  const r = 64;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - progress);

  return (
    <LmGlassCard glow>
      <LmNumberedHeader index={1} title="Business Memory" />
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
        <div className="relative flex h-32 w-32 shrink-0 items-center justify-center">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 140 140" aria-hidden>
            <circle cx="70" cy="70" r={r} fill="transparent" stroke="rgba(255,255,255,0.06)" strokeWidth="7" />
            <circle
              cx="70"
              cy="70"
              r={r}
              fill="transparent"
              stroke={tone}
              strokeWidth="7"
              strokeLinecap="round"
              strokeDasharray={c}
              strokeDashoffset={offset}
              style={{ opacity: 0.85 }}
            />
          </svg>
          <div className="absolute text-center">
            <p className="text-[9px] font-bold uppercase tracking-widest" style={{ color: TEAM_OPS.onVariant }}>
              Memory
            </p>
            <p className="text-sm font-bold" style={{ color: tone, fontFamily: JAKARTA }}>
              {hasActivity ? "Active" : "Empty"}
            </p>
          </div>
        </div>
        <div className="min-w-0 flex-1 text-center sm:text-left">
          <h3 className="text-xl font-bold" style={{ fontFamily: JAKARTA, color: TEAM_OPS.onSurface }}>
            Memory sources
          </h3>
          <p className="mt-2 text-sm leading-relaxed" style={{ color: TEAM_OPS.onVariant }}>
            {summary?.description ??
              "Allowlisted event references only — AI and media not available."}
          </p>
          <div className="mt-4 flex flex-wrap justify-center gap-3 sm:justify-start">
            <MetaChip label="Learning signals" value={String(signals)} />
            <MetaChip label="Months active" value={String(months)} />
            <MetaChip label="Moments" value={String(moments)} />
          </div>
        </div>
      </div>
    </LmGlassCard>
  );
}

function MetaChip({ label, value }: { label: string; value: string }) {
  return (
    <div
      className="rounded-xl border px-3 py-2 text-center"
      style={{ background: "rgba(255,255,255,0.04)", borderColor: `${TEAM_OPS.outline}33` }}
    >
      <p className="text-lg font-bold" style={{ color: TEAM_OPS.onSurface, fontFamily: JAKARTA }}>
        {value}
      </p>
      <p className="text-[9px] uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
        {label}
      </p>
    </div>
  );
}

export function LmFilterChips({
  filters,
  activeKey,
  onChange,
}: {
  filters: BusinessMemorySourceFilter[];
  activeKey: string;
  onChange: (key: string) => void;
}) {
  if (filters.length <= 1) return null;
  return (
    <div className="flex gap-2 overflow-x-auto pb-1" style={{ fontFamily: JAKARTA }}>
      {filters.map((f) => {
        const active = f.key === activeKey;
        return (
          <button
            key={f.key}
            type="button"
            onClick={() => onChange(f.key)}
            className="shrink-0 rounded-full px-4 py-2 text-xs font-bold transition-colors"
            style={{
              background: active ? TEAM_OPS.primaryContainer : TEAM_OPS.surfaceLow,
              color: active ? "#0d0096" : TEAM_OPS.onVariant,
              border: active ? "none" : `1px solid ${TEAM_OPS.outline}44`,
            }}
          >
            {f.label}
          </button>
        );
      })}
    </div>
  );
}

export function LmPatternPills({
  patterns,
  sectionIndex,
}: {
  patterns: Array<{ pattern_type?: string; dimension?: string; label?: string; count?: number } | string>;
  sectionIndex: number;
}) {
  if (!patterns.length) return null;
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title="Pattern network" />
      <div className="flex flex-wrap gap-2">
        {patterns.map((p, i) => {
          const label =
            typeof p === "string"
              ? p
              : typeof p.label === "string"
                ? p.label
                : "Pattern";
          return (
            <span
              key={i}
              className="rounded-full border px-3 py-2 text-xs font-medium"
              style={{
                background: "rgba(128, 131, 255, 0.12)",
                borderColor: "rgba(128, 131, 255, 0.35)",
                color: TEAM_OPS.primary,
              }}
            >
              {label}
            </span>
          );
        })}
      </div>
    </LmGlassCard>
  );
}

export function LmInsightCards({
  success,
  risk,
  sectionIndex,
}: {
  success: BusinessMemoryMemoryItem[];
  risk: BusinessMemoryMemoryItem[];
  sectionIndex: number;
}) {
  if (!success.length && !risk.length) return null;
  return (
    <div className="space-y-4">
      {success.length > 0 ? (
        <LmGlassCard>
          <LmNumberedHeader index={sectionIndex} title="Success memory" />
          <div className="space-y-2">
            {success.map((item, i) => (
              <div
                key={`s-${i}`}
                className="rounded-xl border p-4"
                style={{
                  borderColor: `${TEAM_OPS.secondary}55`,
                  background: `${TEAM_OPS.secondary}12`,
                }}
              >
                <p className="text-sm font-bold" style={{ color: TEAM_OPS.secondary }}>
                  {item.title}
                </p>
                {item.detail ? (
                  <p className="mt-1 text-xs" style={{ color: TEAM_OPS.onVariant }}>
                    {item.detail}
                  </p>
                ) : null}
                {item.observed_count != null ? (
                  <p className="mt-2 text-[10px] uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
                    Observed {item.observed_count}×
                  </p>
                ) : null}
              </div>
            ))}
          </div>
        </LmGlassCard>
      ) : null}
      {risk.length > 0 ? (
        <LmGlassCard>
          <LmNumberedHeader
            index={success.length ? sectionIndex + 1 : sectionIndex}
            title="Risk memory"
          />
          <div className="space-y-2">
            {risk.map((item, i) => (
              <div
                key={`r-${i}`}
                className="rounded-xl border p-4"
                style={{
                  borderColor: `${TEAM_OPS.error}55`,
                  background: `${TEAM_OPS.error}12`,
                }}
              >
                <p className="text-sm font-bold" style={{ color: TEAM_OPS.error }}>
                  {item.title}
                </p>
                <p className="mt-1 text-xs" style={{ color: TEAM_OPS.onVariant }}>
                  {[item.detail, item.impact].filter(Boolean).join(" · ")}
                </p>
                {item.observed_count != null ? (
                  <p className="mt-2 text-[10px] uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
                    Observed {item.observed_count}×
                  </p>
                ) : null}
              </div>
            ))}
          </div>
        </LmGlassCard>
      ) : null}
    </div>
  );
}

export function LmBucketSection({
  index,
  title,
  items,
}: {
  index: number;
  title: string;
  items: BusinessMemoryEvent[];
}) {
  return (
    <LmGlassCard>
      <LmNumberedHeader index={index} title={title} />
      <LmEventFeed items={items} emptyLabel="No events in this bucket." />
    </LmGlassCard>
  );
}

export function LmTimelineFeed({
  items,
  sectionIndex,
}: {
  items: BusinessMemoryEvent[];
  sectionIndex: number;
}) {
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title="Timeline" />
      <LmEventFeed items={items} emptyLabel="No timeline events yet." />
    </LmGlassCard>
  );
}

function trendLabel(band?: string): { text: string; tone: string } {
  switch ((band || "empty").toLowerCase()) {
    case "healthy":
      return { text: "↑ Imp.", tone: TEAM_OPS.secondary };
    case "needs_attention":
      return { text: "→ Watch", tone: TEAM_OPS.tertiary };
    case "at_risk":
    case "critical":
      return { text: "↓ Decl.", tone: TEAM_OPS.error };
    default:
      return { text: "— Empty", tone: TEAM_OPS.onVariant };
  }
}

/** Empty-capable glass section used for stitch-layout slots without inventing data. */
export function LmEmptySection({
  index,
  title,
  emptyLabel,
  borderAccent,
}: {
  index: number;
  title: string;
  emptyLabel: string;
  borderAccent?: string;
}) {
  return (
    <LmGlassCard
      style={
        borderAccent
          ? { borderLeft: `4px solid ${borderAccent}` }
          : undefined
      }
    >
      <LmNumberedHeader index={index} title={title} />
      <TeamOpsEmptyLine label={emptyLabel} />
    </LmGlassCard>
  );
}

export function LmConnectionsSection({ sectionIndex }: { sectionIndex: number }) {
  return (
    <LmEmptySection
      index={sectionIndex}
      title="Connections & Influence"
      emptyLabel="No connection signals yet."
    />
  );
}

/** Drift alerts — bind real life signals; empty when none. */
export function LmDriftAlertSection({
  signals,
  sectionIndex,
}: {
  signals: BusinessLifeSignal[];
  sectionIndex: number;
}) {
  return (
    <LmGlassCard style={{ borderLeft: `4px solid ${TEAM_OPS.tertiary}` }}>
      <LmNumberedHeader index={sectionIndex} title="Business Drift Alert" />
      {signals.length === 0 ? (
        <TeamOpsEmptyLine label="No drift signals yet." />
      ) : (
        <div className="space-y-2">
          {signals.map((s, i) => {
            const tone =
              s.severity === "high"
                ? TEAM_OPS.error
                : s.severity === "medium"
                  ? TEAM_OPS.tertiary
                  : TEAM_OPS.primary;
            return (
              <div
                key={`${s.signal_type ?? "d"}-${i}`}
                className="flex items-start gap-3"
              >
                <div
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-bold"
                  style={{ background: `${tone}22`, color: tone }}
                >
                  !
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm" style={{ color: TEAM_OPS.onSurface }}>
                    {s.label}
                  </p>
                  {s.count > 0 ? (
                    <p className="mt-0.5 text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
                      Observed {s.count}
                      {s.dimension ? ` · ${s.dimension.replace(/_/g, " ")}` : ""}
                    </p>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </LmGlassCard>
  );
}

/** Highest leverage — pick best non-empty dimension by band priority; else empty. */
export function LmLeverageSection({
  dimensions,
  sectionIndex,
}: {
  dimensions: BusinessLifeDimension[];
  sectionIndex: number;
}) {
  const order: Record<string, number> = {
    healthy: 4,
    needs_attention: 3,
    at_risk: 2,
    critical: 1,
    empty: 0,
  };
  const active = dimensions.filter((d) => d.band && d.band !== "empty");
  const best =
    active.length === 0
      ? null
      : [...active].sort(
          (a, b) => (order[b.band] ?? 0) - (order[a.band] ?? 0) || b.count - a.count,
        )[0];

  if (!best) {
    return (
      <LmEmptySection
        index={sectionIndex}
        title="Highest Business Leverage"
        emptyLabel="No leverage signal yet."
      />
    );
  }
  const tone = healthBandColor(best.band);
  return (
    <LmGlassCard
      style={{
        background: "linear-gradient(135deg, rgba(67,56,202,0.28), rgba(19,19,27,0.6))",
        borderColor: "rgba(99, 102, 241, 0.3)",
      }}
    >
      <LmNumberedHeader index={sectionIndex} title="Highest Business Leverage" />
      <div className="mb-3">
        <h3 className="text-lg font-bold" style={{ color: TEAM_OPS.onSurface, fontFamily: JAKARTA }}>
          {best.label}
        </h3>
        <p className="mt-1 text-xs uppercase tracking-wider" style={{ color: TEAM_OPS.onVariant }}>
          Band · <span style={{ color: tone }}>{best.band.replace(/_/g, " ")}</span>
          {best.count > 0 ? ` · Count ${best.count}` : ""}
        </p>
      </div>
      <div
        className="h-2 w-full overflow-hidden rounded-full"
        style={{ background: "rgba(255,255,255,0.1)" }}
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${Math.round(bandProgress(best.band) * 100)}%`,
            background: tone,
          }}
        />
      </div>
    </LmGlassCard>
  );
}

export function LmTrendsSection({
  dimensions,
  sectionIndex,
}: {
  dimensions: BusinessLifeDimension[];
  sectionIndex: number;
}) {
  const rows = dimensions.filter((d) => d.band && d.band !== "empty").slice(0, 6);
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title="Trends" />
      {rows.length === 0 ? (
        <TeamOpsEmptyLine label="No trend signals yet." />
      ) : (
        <div className="space-y-3">
          {rows.map((d) => {
            const t = trendLabel(d.band);
            return (
              <div key={d.key} className="flex items-center justify-between gap-2">
                <span className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
                  {d.label}
                </span>
                <span className="text-xs font-bold" style={{ color: t.tone }}>
                  {t.text}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </LmGlassCard>
  );
}

export function LmDrivesGrowthSection({ sectionIndex }: { sectionIndex: number }) {
  return (
    <LmEmptySection
      index={sectionIndex}
      title="Drives Growth"
      emptyLabel="No growth correlations yet."
    />
  );
}

export function LmMonthlyChangesSection({ sectionIndex }: { sectionIndex: number }) {
  return (
    <LmEmptySection
      index={sectionIndex}
      title="What Changed This Month?"
      emptyLabel="No monthly changes yet."
    />
  );
}

/** Journey that always reserves the stitch slot (empty-capable). Horizontal when items exist. */
export function LmJourneySection({
  items,
  sectionIndex,
  title = "Business Journey",
}: {
  items: Array<BusinessMemoryJourneyItem | { kind?: string; title: string; occurred_at?: string | null }>;
  sectionIndex: number;
  title?: string;
}) {
  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title={title} />
      {items.length === 0 ? (
        <TeamOpsEmptyLine label="No journey milestones yet." />
      ) : (
        <div className="relative overflow-x-auto pb-1">
          <div className="relative flex min-w-full items-start justify-between gap-4 px-2 py-4">
            <div
              className="absolute left-4 right-4 top-[22px] h-px"
              style={{ background: `${TEAM_OPS.outline}44` }}
              aria-hidden
            />
            {items.slice(0, 6).map((item, i) => (
              <div
                key={`${item.kind}-${item.occurred_at}-${i}`}
                className="relative z-10 flex min-w-[88px] flex-1 flex-col items-center gap-2 text-center"
              >
                <span
                  className="h-3 w-3 rounded-full border-4"
                  style={{
                    background: TEAM_OPS.primaryContainer,
                    borderColor: TEAM_OPS.surfaceLow,
                  }}
                />
                {item.occurred_at ? (
                  <p className="text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
                    {formatOccurredAt(item.occurred_at)}
                  </p>
                ) : null}
                <p className="text-xs font-semibold leading-tight" style={{ color: TEAM_OPS.onSurface }}>
                  {item.title}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </LmGlassCard>
  );
}

export function LmContributionDetails({
  children,
  defaultOpen = false,
}: {
  children: ReactNode;
  defaultOpen?: boolean;
}) {
  return (
    <details
      className="rounded-2xl border px-4 py-3"
      open={defaultOpen}
      style={{
        background: "rgba(27, 27, 35, 0.5)",
        borderColor: `${TEAM_OPS.outline}33`,
        fontFamily: JAKARTA,
      }}
    >
      <summary
        className="cursor-pointer list-none text-sm font-bold"
        style={{ color: TEAM_OPS.onSurface }}
      >
        Contribution details
      </summary>
      <div className="mt-4 space-y-4">{children}</div>
    </details>
  );
}

/** Memory Strength hero — factual metrics + radar chrome (no /100 score). */
export function LmMemoryStrengthHero({
  summary,
  activeMomentCount,
  eventCount,
  satellites = [],
}: {
  summary?: BusinessMemorySummary | null;
  activeMomentCount: number;
  eventCount: number;
  /** Short moment-type labels for radar nodes (max 4). */
  satellites?: string[];
}) {
  const signals = summary?.event_count ?? eventCount;
  const months = summary?.months_active ?? 0;
  const moments = summary?.active_moment_count ?? activeMomentCount;
  const hasActivity = signals > 0 || moments > 0;
  const growing = signals > 0;
  const tone = hasActivity ? TEAM_OPS.secondary : TEAM_OPS.onVariant;
  const nodes = satellites.slice(0, 4);

  return (
    <LmGlassCard glow>
      <LmNumberedHeader index={1} title="Business Memory Strength" />
      <div className="grid grid-cols-1 items-center gap-6 sm:grid-cols-2">
        <div className="space-y-4">
          <div className="flex items-baseline gap-2">
            <span
              className="text-5xl font-extrabold leading-none"
              style={{ color: tone, fontFamily: JAKARTA }}
            >
              {hasActivity ? "Active" : "Empty"}
            </span>
          </div>
          {growing ? (
            <div
              className="flex items-center gap-1 text-xs font-bold uppercase tracking-widest"
              style={{ color: TEAM_OPS.secondary }}
            >
              <span aria-hidden>↑</span>
              <span>Memory growing</span>
            </div>
          ) : null}
          <div className="space-y-2 text-sm" style={{ color: TEAM_OPS.onVariant }}>
            <p className="flex items-center gap-2">
              <span aria-hidden style={{ color: TEAM_OPS.primary }}>◈</span>
              {signals.toLocaleString()} Learning Signals
            </p>
            <p className="flex items-center gap-2">
              <span aria-hidden style={{ color: TEAM_OPS.primary }}>▣</span>
              {months} Months Active
            </p>
            <p className="flex items-center gap-2">
              <span aria-hidden style={{ color: TEAM_OPS.primary }}>◉</span>
              {moments} Moments
            </p>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: TEAM_OPS.onVariant }}>
            {summary?.description ??
              "Your business has accumulated operational knowledge through recorded moments and events."}
          </p>
        </div>
        <LmMemoryRadar nodes={nodes} active={hasActivity} />
      </div>
    </LmGlassCard>
  );
}

function LmMemoryRadar({ nodes, active }: { nodes: string[]; active: boolean }) {
  const tone = active ? TEAM_OPS.primary : TEAM_OPS.outline;
  const positions = [
    { x: 200, y: 40 },
    { x: 360, y: 200 },
    { x: 200, y: 360 },
    { x: 40, y: 200 },
  ];
  return (
    <div className="relative mx-auto flex min-h-[220px] w-full max-w-[280px] items-center justify-center">
      <div
        className="pointer-events-none absolute inset-0 rounded-full"
        style={{
          background: `radial-gradient(circle, ${tone}26 0%, transparent 70%)`,
        }}
        aria-hidden
      />
      <svg className="relative z-10 h-auto w-full" viewBox="0 0 400 400" aria-hidden>
        <circle cx="200" cy="200" r="160" fill="none" stroke="currentColor" strokeWidth="1" style={{ color: `${TEAM_OPS.outline}55` }} />
        <circle cx="200" cy="200" r="100" fill="none" stroke="currentColor" strokeWidth="1" style={{ color: `${TEAM_OPS.outline}33` }} />
        {positions.map((p, i) => (
          <line
            key={`l-${i}`}
            x1="200"
            y1="200"
            x2={p.x}
            y2={p.y}
            stroke={tone}
            strokeOpacity="0.35"
            strokeWidth="1"
            strokeDasharray="4 4"
          />
        ))}
        <circle cx="200" cy="200" r="44" fill={TEAM_OPS.surfaceLow} stroke={tone} strokeWidth="2" />
        <text
          x="200"
          y="195"
          textAnchor="middle"
          fill={tone}
          fontSize="10"
          fontWeight="700"
          style={{ textTransform: "uppercase" }}
        >
          Business
        </text>
        <text
          x="200"
          y="210"
          textAnchor="middle"
          fill={tone}
          fontSize="10"
          fontWeight="700"
          style={{ textTransform: "uppercase" }}
        >
          Memory
        </text>
        {positions.map((p, i) => {
          const label = nodes[i];
          return (
            <g key={`n-${i}`} transform={`translate(${p.x}, ${p.y})`}>
              <circle
                r="22"
                fill={TEAM_OPS.surfaceLow}
                stroke={label ? tone : `${TEAM_OPS.outline}66`}
                strokeWidth="1.5"
              />
              {label ? (
                <text
                  y="4"
                  textAnchor="middle"
                  fill={TEAM_OPS.onVariant}
                  fontSize="7"
                  fontWeight="600"
                >
                  {label.length > 10 ? `${label.slice(0, 9)}…` : label}
                </text>
              ) : null}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export function LmBiggestLearningSection({
  item,
  sectionIndex,
}: {
  item?: BusinessMemoryMemoryItem | null;
  sectionIndex: number;
}) {
  if (!item) {
    return (
      <LmEmptySection
        index={sectionIndex}
        title="Biggest Learning"
        emptyLabel="No learning derived yet."
      />
    );
  }
  return (
    <LmGlassCard style={{ borderColor: `${TEAM_OPS.primary}44` }} className="relative">
      <div
        className="pointer-events-none absolute right-4 top-2 text-6xl opacity-10"
        style={{ color: TEAM_OPS.primary }}
        aria-hidden
      >
        ✦
      </div>
      <LmNumberedHeader index={sectionIndex} title="Biggest Learning" />
      <p className="relative z-10 max-w-[85%] text-base font-semibold leading-snug" style={{ color: TEAM_OPS.onSurface }}>
        {item.title}
      </p>
      {item.detail ? (
        <p className="relative z-10 mt-2 text-sm" style={{ color: TEAM_OPS.onVariant }}>
          {item.detail}
        </p>
      ) : null}
      {item.observed_count != null && item.observed_count > 0 ? (
        <div
          className="relative z-10 mt-4 flex gap-6 border-t pt-3"
          style={{ borderColor: `${TEAM_OPS.outline}22` }}
        >
          <div>
            <p className="text-[10px] uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
              Derived from
            </p>
            <p className="font-bold" style={{ color: TEAM_OPS.onSurface }}>
              {item.observed_count} Activities
            </p>
          </div>
        </div>
      ) : null}
    </LmGlassCard>
  );
}

const FLOW_PATTERN_TYPES = new Set([
  "meeting_cadence",
  "vendor_activity",
  "recognition_culture",
  "runway_risk_memory",
]);

/** Pattern network — short event-derived flows only (not dimension_active slogans). */
export function LmPatternNetworkSection({
  patterns,
  sectionIndex,
}: {
  patterns: Array<{ pattern_type?: string; dimension?: string; label?: string; count?: number } | string>;
  sectionIndex: number;
}) {
  const flow = patterns.filter((p) => {
    if (typeof p === "string") return true;
    const t = (p.pattern_type || "").toLowerCase();
    if (t === "dimension_active") return false;
    if (FLOW_PATTERN_TYPES.has(t)) return true;
    // Legacy / unknown: keep if label is short (not a tracked slogan).
    const label = typeof p.label === "string" ? p.label : "";
    return label.length > 0 && label.length <= 48 && !/actively being tracked/i.test(label);
  });

  if (!flow.length) {
    return (
      <LmEmptySection
        index={sectionIndex}
        title="Pattern Network"
        emptyLabel="No patterns detected yet."
      />
    );
  }

  const labels = flow.map((p) =>
    typeof p === "string" ? p : typeof p.label === "string" ? p.label : "Pattern",
  );

  return (
    <LmGlassCard>
      <LmNumberedHeader index={sectionIndex} title="Pattern Network" />
      <div className="flex flex-wrap items-center justify-center gap-2 py-2">
        {labels.map((label, i) => (
          <div key={i} className="flex items-center gap-2">
            <span
              className="rounded-lg border px-3 py-2 text-xs font-medium"
              style={{
                background: "rgba(128, 131, 255, 0.12)",
                borderColor: "rgba(128, 131, 255, 0.35)",
                color: TEAM_OPS.primary,
              }}
            >
              {label}
            </span>
            {i < labels.length - 1 ? (
              <span className="text-xs" style={{ color: TEAM_OPS.primary }} aria-hidden>
                →
              </span>
            ) : null}
          </div>
        ))}
      </div>
    </LmGlassCard>
  );
}

export function LmPlaybookSection({
  playbooks,
  sectionIndex,
}: {
  playbooks?: unknown[];
  sectionIndex: number;
}) {
  const list = Array.isArray(playbooks) ? playbooks : [];
  if (!list.length) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span
            className="flex h-5 w-5 items-center justify-center rounded-sm text-[10px] font-bold"
            style={{ background: `${TEAM_OPS.primary}33`, color: TEAM_OPS.primary }}
          >
            {sectionIndex}
          </span>
          <h3 className="text-sm font-bold" style={{ color: TEAM_OPS.onSurface, fontFamily: JAKARTA }}>
            Business Playbook
          </h3>
        </div>
        <div
          className="rounded-2xl border-l-4 p-4"
          style={{
            background: TEAM_OPS.surfaceLow,
            borderLeftColor: TEAM_OPS.primary,
            borderColor: `${TEAM_OPS.outline}22`,
            borderWidth: 1,
            borderLeftWidth: 4,
            minHeight: 88,
          }}
        >
          <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: TEAM_OPS.primary }}>
            Playbook
          </p>
          <p className="mt-2 text-sm" style={{ color: TEAM_OPS.onVariant }}>
            No playbooks yet.
          </p>
        </div>
      </div>
    );
  }
  return (
    <LmGlassCard style={{ borderLeft: `4px solid ${TEAM_OPS.primary}` }}>
      <LmNumberedHeader index={sectionIndex} title="Business Playbook" />
      <div className="space-y-3">
        {list.map((raw, i) => {
          const p = raw as {
            playbook_title?: string;
            title?: string;
            playbook_summary?: string;
          };
          const title = p.playbook_title || p.title || `Playbook #${i + 1}`;
          return (
            <div
              key={i}
              className="rounded-xl border p-4"
              style={{
                background: "rgba(255,255,255,0.03)",
                borderColor: `${TEAM_OPS.outline}33`,
              }}
            >
              <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: TEAM_OPS.primary }}>
                Playbook #{i + 1}
              </p>
              <p className="mt-1 font-bold" style={{ color: TEAM_OPS.onSurface }}>
                {title}
              </p>
              {p.playbook_summary ? (
                <p className="mt-1 text-xs" style={{ color: TEAM_OPS.onVariant }}>
                  {p.playbook_summary}
                </p>
              ) : null}
            </div>
          );
        })}
      </div>
    </LmGlassCard>
  );
}

export function LmSuccessMemorySection({
  items,
  sectionIndex,
}: {
  items: BusinessMemoryMemoryItem[];
  sectionIndex: number;
}) {
  if (!items.length) {
    return (
      <LmEmptySection
        index={sectionIndex}
        title="Success Memory"
        emptyLabel="No success memory yet."
      />
    );
  }
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span
          className="flex h-5 w-5 items-center justify-center rounded-sm text-[10px] font-bold"
          style={{ background: `${TEAM_OPS.primary}33`, color: TEAM_OPS.primary }}
        >
          {sectionIndex}
        </span>
        <h3 className="text-sm font-bold" style={{ color: TEAM_OPS.onSurface, fontFamily: JAKARTA }}>
          Success Memory
        </h3>
      </div>
      <div className="space-y-2">
        {items.map((item, i) => (
          <div
            key={`s-${i}`}
            className="rounded-2xl border p-4"
            style={{
              borderColor: `${TEAM_OPS.secondary}55`,
              background: `${TEAM_OPS.secondary}12`,
            }}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-bold" style={{ color: TEAM_OPS.secondary }}>
                {item.title}
              </p>
              <span aria-hidden style={{ color: TEAM_OPS.secondary }}>
                ★
              </span>
            </div>
            {item.detail ? (
              <p className="mt-2 text-xs leading-relaxed" style={{ color: TEAM_OPS.onVariant }}>
                {item.detail}
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

export function LmRiskMemorySection({
  items,
  sectionIndex,
}: {
  items: BusinessMemoryMemoryItem[];
  sectionIndex: number;
}) {
  if (!items.length) {
    return (
      <LmEmptySection
        index={sectionIndex}
        title="Risk Memory"
        emptyLabel="No risk memory yet."
      />
    );
  }
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span
          className="flex h-5 w-5 items-center justify-center rounded-sm text-[10px] font-bold"
          style={{ background: `${TEAM_OPS.primary}33`, color: TEAM_OPS.primary }}
        >
          {sectionIndex}
        </span>
        <h3 className="text-sm font-bold" style={{ color: TEAM_OPS.onSurface, fontFamily: JAKARTA }}>
          Risk Memory
        </h3>
      </div>
      <div className="space-y-2">
        {items.map((item, i) => (
          <div
            key={`r-${i}`}
            className="rounded-2xl border p-4"
            style={{
              borderColor: `${TEAM_OPS.error}55`,
              background: `${TEAM_OPS.error}12`,
            }}
          >
            <div className="mb-2 flex items-center gap-2">
              <span aria-hidden style={{ color: TEAM_OPS.error }}>
                ⚠
              </span>
              <p className="text-sm font-bold uppercase" style={{ color: TEAM_OPS.error }}>
                {item.title}
              </p>
            </div>
            {(item.detail || item.impact) && (
              <p className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
                {[item.impact ? `Impact: ${item.impact}` : null, item.detail]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
            )}
            {item.observed_count != null && item.observed_count > 0 ? (
              <p className="mt-2 text-[10px] font-bold uppercase tracking-wide" style={{ color: `${TEAM_OPS.error}cc` }}>
                Observed {item.observed_count} Times
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

export function LmWisdomSection({ sectionIndex }: { sectionIndex: number }) {
  return (
    <LmEmptySection
      index={sectionIndex}
      title="Business Wisdom"
      emptyLabel="No wisdom captured yet."
    />
  );
}

"use client";

import type { ReactNode } from "react";
import type { TeamOpsEventItem } from "@/lib/api/businessActive";
import { TEAM_OPS, formatOccurredAt, healthBandColor } from "./teamOpsTheme";

export function TeamOpsScrollShell({
  bottomPadding = 0,
  children,
}: {
  bottomPadding?: number;
  children: ReactNode;
}) {
  return (
    <div
      className="mx-auto flex min-h-0 w-full max-w-lg flex-1 flex-col gap-6 overflow-y-auto px-1 pt-2"
      style={{
        color: TEAM_OPS.onSurface,
        paddingBottom: bottomPadding || 24,
        fontFamily: TEAM_OPS.fontBody,
      }}
    >
      {children}
    </div>
  );
}

export function TeamOpsSectionCard({
  children,
  gradient = false,
}: {
  children: ReactNode;
  gradient?: boolean;
}) {
  return (
    <section
      className="rounded-2xl p-5"
      style={{
        background: gradient
          ? `linear-gradient(135deg, rgba(128,131,255,0.12) 0%, ${TEAM_OPS.surfaceLow} 100%)`
          : TEAM_OPS.surfaceLow,
        border: `1px solid ${TEAM_OPS.outline}33`,
      }}
    >
      {children}
    </section>
  );
}

export function TeamOpsSectionTitle({ children }: { children: ReactNode }) {
  return (
    <h3
      className="mb-3 text-sm font-semibold"
      style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
    >
      {children}
    </h3>
  );
}

export function TeamOpsEmptyLine({ label }: { label: string }) {
  return (
    <p className="py-1 text-sm" style={{ color: TEAM_OPS.onVariant }}>
      {label}
    </p>
  );
}

export function TeamOpsEventRows({
  items,
  emptyLabel,
  onSelect,
}: {
  items: TeamOpsEventItem[];
  emptyLabel: string;
  onSelect?: (item: TeamOpsEventItem) => void;
}) {
  if (!items.length) return <TeamOpsEmptyLine label={emptyLabel} />;
  return (
    <ul className="space-y-2">
      {items.map((item) => {
        const key = item.event_id || `${item.action_type}-${item.title}`;
        const content = (
          <div className="min-w-0">
            <p className="truncate text-sm font-medium" style={{ color: TEAM_OPS.onSurface }}>
              {item.title || item.action_type}
            </p>
            <p className="mt-0.5 text-xs uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
              {item.action_type}
              {item.occurred_at ? ` · ${formatOccurredAt(item.occurred_at)}` : ""}
            </p>
          </div>
        );
        return (
          <li key={key}>
            {onSelect ? (
              <button
                type="button"
                className="w-full rounded-xl px-3 py-3 text-left"
                style={{ background: TEAM_OPS.surface, border: `1px solid ${TEAM_OPS.outline}22` }}
                onClick={() => onSelect(item)}
              >
                {content}
              </button>
            ) : (
              <div
                className="rounded-xl px-3 py-3"
                style={{ background: TEAM_OPS.surface, border: `1px solid ${TEAM_OPS.outline}22` }}
              >
                {content}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function isPermissionDenied(error: string | null): boolean {
  if (!error) return false;
  return /403|401|permission|forbidden|not allowed|access denied|unauthorized|not a member|invalid_member|membership/i.test(
    error,
  );
}

export function TeamOpsSkeleton() {
  return (
    <div className="flex flex-col gap-4 py-2" aria-hidden>
      <div
        className="h-36 animate-pulse rounded-2xl"
        style={{ background: TEAM_OPS.surfaceLow }}
      />
      <div className="flex gap-2 overflow-hidden">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-16 min-w-[112px] flex-shrink-0 animate-pulse rounded-xl"
            style={{ background: TEAM_OPS.surfaceLow }}
          />
        ))}
      </div>
      <div
        className="h-24 animate-pulse rounded-xl"
        style={{ background: TEAM_OPS.surfaceLow }}
      />
      <div
        className="h-24 animate-pulse rounded-xl"
        style={{ background: TEAM_OPS.surfaceLow }}
      />
    </div>
  );
}

export function TeamOpsStatusBanner({
  loading,
  refreshing,
  error,
  onRetry,
  hasData,
}: {
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  onRetry: () => void;
  /** When true, never show full skeleton — usable data is on screen. */
  hasData?: boolean;
}) {
  if (loading && !hasData) {
    return <TeamOpsSkeleton />;
  }
  if (error) {
    const denied = isPermissionDenied(error);
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <p className="text-sm" style={{ color: denied ? TEAM_OPS.onVariant : TEAM_OPS.error }}>
          {denied ? "Permission denied" : error}
        </p>
        {!denied ? (
          <button
            type="button"
            className="rounded-lg px-4 py-2 text-sm font-semibold"
            style={{ background: TEAM_OPS.surfaceHigh, color: TEAM_OPS.primary }}
            onClick={onRetry}
          >
            Retry
          </button>
        ) : null}
      </div>
    );
  }
  if (refreshing) {
    return (
      <p className="text-center text-[11px]" style={{ color: TEAM_OPS.onVariant }}>
        Updating…
      </p>
    );
  }
  return null;
}

export function TeamOpsKpiChip({ label, value }: { label: string; value: string | number }) {
  return (
    <div
      className="min-w-[112px] flex-shrink-0 rounded-xl p-3"
      style={{ background: TEAM_OPS.surfaceLow, border: `1px solid ${TEAM_OPS.outline}1a` }}
    >
      <div className="mb-1 truncate text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
        {label}
      </div>
      <div className="text-lg font-bold" style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}>
        {value}
      </div>
    </div>
  );
}

export function HealthBandBadge({ band, label }: { band?: string; label?: string }) {
  const color = healthBandColor(band);
  return (
    <span
      className="rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider"
      style={{ background: `${color}33`, color }}
    >
      {label || "Not started"}
    </span>
  );
}

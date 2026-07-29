"use client";

import type { BusinessMemoryEvent, BusinessMemoryResponse } from "@/lib/api/businessActive";
import { MEMORY_BUCKET_LABELS, MEMORY_BUCKET_ORDER } from "@/lib/business/teamOpsApiMappers";
import { formatOccurredAt, TEAM_OPS } from "./teamOpsTheme";
import {
  TeamOpsEmptyLine,
  TeamOpsScrollShell,
  TeamOpsSectionCard,
  TeamOpsSectionTitle,
  TeamOpsStatusBanner,
} from "./shared";

type Props = {
  data: BusinessMemoryResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
};

function MemoryRows({ items }: { items: BusinessMemoryEvent[] }) {
  if (!items.length) return <TeamOpsEmptyLine label="No events in this bucket." />;
  return (
    <ul className="space-y-2">
      {items.map((e) => (
        <li
          key={e.event_id}
          className="rounded-xl px-3 py-3"
          style={{ background: TEAM_OPS.surfaceLow, border: `1px solid ${TEAM_OPS.outline}22` }}
        >
          <p className="text-sm font-medium" style={{ color: TEAM_OPS.onSurface }}>
            {e.title || e.action_type}
          </p>
          <p className="mt-0.5 text-xs" style={{ color: TEAM_OPS.onVariant }}>
            {e.action_type}
            {e.occurred_at ? ` · ${formatOccurredAt(e.occurred_at)}` : ""}
            {e.source_moment_name ? ` · ${e.source_moment_name}` : ""}
          </p>
        </li>
      ))}
    </ul>
  );
}

function patternLabel(raw: unknown): string {
  if (typeof raw === "string") return raw;
  if (raw && typeof raw === "object") {
    const o = raw as Record<string, unknown>;
    if (typeof o.label === "string") return o.label;
    if (typeof o.title === "string") return o.title;
    if (typeof o.pattern === "string") return o.pattern;
  }
  return "Pattern";
}

/** Presentational Memory — timeline / patterns / allowlisted buckets only. */
export function BusinessMemoryContribution({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  onRetry,
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

  const patterns = Array.isArray(data.patterns) ? data.patterns : [];

  return (
    <TeamOpsScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <TeamOpsStatusBanner loading={false} refreshing error={null} onRetry={onRetry} />
      ) : null}

      <TeamOpsSectionCard gradient>
        <h2
          className="text-2xl font-bold"
          style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
        >
          Memory sources
        </h2>
        <p className="mt-2 text-sm" style={{ color: TEAM_OPS.onVariant }}>
          Allowlisted event references only — no AI narrative.
        </p>
      </TeamOpsSectionCard>

      <section>
        <TeamOpsSectionTitle>Timeline</TeamOpsSectionTitle>
        <MemoryRows items={data.events ?? []} />
      </section>

      <section>
        <TeamOpsSectionTitle>Patterns</TeamOpsSectionTitle>
        {patterns.length === 0 ? (
          <TeamOpsEmptyLine label="No patterns yet." />
        ) : (
          <ul className="space-y-2">
            {patterns.map((p, i) => (
              <li
                key={i}
                className="rounded-xl px-3 py-3 text-sm"
                style={{ background: TEAM_OPS.surfaceLow, color: TEAM_OPS.onSurface }}
              >
                {patternLabel(p)}
              </li>
            ))}
          </ul>
        )}
      </section>

      {MEMORY_BUCKET_ORDER.map((key) => {
        const items = data.buckets?.[key]?.items ?? [];
        return (
          <section key={key}>
            <TeamOpsSectionTitle>{MEMORY_BUCKET_LABELS[key]}</TeamOpsSectionTitle>
            <MemoryRows items={items} />
          </section>
        );
      })}
    </TeamOpsScrollShell>
  );
}

/** @deprecated */
export const TeamOpsMemory = BusinessMemoryContribution;

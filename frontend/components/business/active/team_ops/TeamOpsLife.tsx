"use client";

import { TEAM_OPS_LIFE_SLICE_KEYS, type BusinessLifeResponse } from "@/lib/api/businessActive";
import { healthBandColor, TEAM_OPS } from "./teamOpsTheme";
import {
  TeamOpsEmptyLine,
  TeamOpsEventRows,
  TeamOpsScrollShell,
  TeamOpsSectionCard,
  TeamOpsSectionTitle,
  TeamOpsStatusBanner,
} from "./shared";

type Props = {
  data: BusinessLifeResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  onRetry: () => void;
};

/** Presentational Life contribution — items already moment-filtered by ViewModel. */
export function BusinessLifeContribution({
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
          Life contributions
        </h2>
        <p className="mt-2 text-sm" style={{ color: TEAM_OPS.onVariant }}>
          Team Ops slices only — not a full Life command center.
        </p>
        <p className="mt-1 text-xs" style={{ color: TEAM_OPS.onVariant }}>
          {data.active_moment_count} active business moment
          {data.active_moment_count === 1 ? "" : "s"}
        </p>
      </TeamOpsSectionCard>

      {TEAM_OPS_LIFE_SLICE_KEYS.map((key) => {
        const slice = data.slices[key];
        if (!slice) return null;
        return (
          <section key={key}>
            <div className="mb-2 flex items-center justify-between gap-2">
              <TeamOpsSectionTitle>{slice.label || key}</TeamOpsSectionTitle>
              {slice.band ? (
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase"
                  style={{
                    color: healthBandColor(slice.band),
                    background: `${healthBandColor(slice.band)}22`,
                  }}
                >
                  {slice.band.replace(/_/g, " ")}
                </span>
              ) : null}
            </div>
            <p className="mb-2 text-xs" style={{ color: TEAM_OPS.onVariant }}>
              Count: {slice.count} · {slice.state}
            </p>
            <TeamOpsEventRows items={slice.items ?? []} emptyLabel="No contribution items yet." />
          </section>
        );
      })}
    </TeamOpsScrollShell>
  );
}

/** @deprecated */
export const TeamOpsLife = BusinessLifeContribution;

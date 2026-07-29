"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import {
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import type { TemplateLifeResponse } from "@/lib/api/personal";

type LifeOperationsLifeProps = {
  data: TemplateLifeResponse;
  bottomPadding?: number;
};

const DIMENSION_LABELS: Record<string, string> = {
  financial_health: "Financial health",
  recovery: "Recovery",
  attention: "Attention",
  rhythm: "Rhythm",
  workload: "Workload",
  momentum: "Momentum",
};

export function LifeOperationsLife({ data, bottomPadding = 0 }: LifeOperationsLifeProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <div style={personalPulseContainerStyle(tokens)}>
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            Personal · Life
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            How is my life operating?
          </h1>
        </header>

        <section
          className="mt-4 rounded-2xl border p-5"
          style={{ borderColor: colors.border, background: colors.surfaceContainer }}
        >
          <p className="text-xs uppercase tracking-wide opacity-60">Today</p>
          <h2 className="mt-1 text-xl font-bold">{data.headline}</h2>
          <p className="mt-2 text-sm opacity-80">{data.subtitle}</p>
          <div className="mt-4 flex items-center gap-4">
            <div>
              <p className="text-3xl font-bold">{data.operating_summary.ops_index}</p>
              <p className="text-xs opacity-60">Ops Index</p>
            </div>
            <div>
              <p className="text-sm font-semibold">{data.operating_summary.momentum.label}</p>
              <p className="text-xs opacity-60 capitalize">
                Momentum {data.operating_summary.momentum.direction}
              </p>
            </div>
          </div>
        </section>

        <section className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {Object.entries(data.dimensions).map(([key, dim]) => (
            <div
              key={key}
              className="rounded-xl p-4"
              style={{ background: colors.surfaceContainerLow }}
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold">{DIMENSION_LABELS[key] ?? key}</p>
                <span className="text-lg font-bold">{dim.score}</span>
              </div>
              <p className="mt-1 text-xs font-medium opacity-80">{dim.label}</p>
              <p className="mt-1 text-xs opacity-60">{dim.detail}</p>
            </div>
          ))}
        </section>

        {(data.pressure_sources.length > 0 || data.recovery_supports.length > 0) && (
          <section className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {data.pressure_sources.length > 0 ? (
              <div className="rounded-xl p-4" style={{ background: `color-mix(in srgb, ${colors.error} 18%, ${colors.surfaceContainer})`, opacity: 0.9 }}>
                <p className="text-sm font-semibold">Pressure sources</p>
                <p className="mt-1 text-xs">{data.pressure_sources.join(", ")}</p>
              </div>
            ) : null}
            {data.recovery_supports.length > 0 ? (
              <div className="rounded-xl p-4" style={{ background: colors.primaryContainer }}>
                <p className="text-sm font-semibold">Recovery supports</p>
                <p className="mt-1 text-xs">{data.recovery_supports.join(", ")}</p>
              </div>
            ) : null}
          </section>
        )}

        <section className="mt-6 grid grid-cols-2 gap-3">
          <div className="rounded-xl p-4" style={{ background: colors.surfaceContainerLow }}>
            <p className="text-xs opacity-60">Today</p>
            <p className="text-sm font-semibold">{String(data.today.event_count ?? 0)} signals</p>
          </div>
          <div className="rounded-xl p-4" style={{ background: colors.surfaceContainerLow }}>
            <p className="text-xs opacity-60">This week</p>
            <p className="text-sm font-semibold">{String(data.week.event_count ?? 0)} signals</p>
          </div>
        </section>

        {data.recent_activity.length > 0 ? (
          <section className="mt-6">
            <h3 className="text-sm font-semibold opacity-80">Recent life signals</h3>
            <ul className="mt-2 space-y-2">
              {data.recent_activity.slice(0, 6).map((item) => (
                <li
                  key={String(item.id)}
                  className="rounded-lg px-3 py-2 text-sm"
                  style={{ background: colors.surfaceContainerLow }}
                >
                  {String(item.title ?? "")}
                </li>
              ))}
            </ul>
          </section>
        ) : null}
      </div>
    </div>
  );
}

export function LifeOperationsLifeSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div className="min-h-0 flex-1 p-6" style={{ paddingBottom: bottomPadding }}>
      <div className="mx-auto max-w-[1080px] space-y-4">
        <div className="h-8 w-64 animate-pulse rounded bg-[#2a2a2a]" />
        <div className="h-36 animate-pulse rounded-2xl bg-[#2a2a2a]" />
        <div className="grid grid-cols-2 gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-[#2a2a2a]" />
          ))}
        </div>
      </div>
    </div>
  );
}

export function LifeOperationsLifeEmpty({ bottomPadding = 0 }: { bottomPadding?: number }) {
  return (
    <div
      className="flex min-h-0 flex-1 items-center justify-center px-6 text-center"
      style={{ paddingBottom: bottomPadding }}
    >
      <p className="text-sm opacity-70">Activate Life Operations to see your operating view.</p>
    </div>
  );
}

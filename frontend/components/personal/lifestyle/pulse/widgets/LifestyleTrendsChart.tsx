"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";
import type { PersonalLifestylePulseMetrics } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";

const MOMENT_TYPE = "LIFESTYLE";

type Props = { trends: PersonalLifestylePulseMetrics["trends_30d"] };

function trendValues(series: Array<{ date: string; value: number } | number>): number[] {
  return series.map((point) => {
    if (typeof point === "number") return Number.isFinite(point) ? point : 0;
    const value = point?.value;
    return typeof value === "number" && Number.isFinite(value) ? value : 0;
  });
}

function seriesToPath(values: number[], width: number, height: number): string {
  if (values.length < 2) return "";
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;
  const step = width / (values.length - 1);
  return values
    .map((v, i) => {
      const x = i * step;
      const y = height - ((v - min) / range) * (height - 8) - 4;
      if (!Number.isFinite(x) || !Number.isFinite(y)) return "";
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .filter(Boolean)
    .join(" ");
}

function seriesToBarHeights(values: number[], count: number): number[] | null {
  if (values.length === 0) return null;
  const max = Math.max(...values, 1);
  const sampled =
    values.length >= count
      ? values.slice(-count)
      : Array.from({ length: count }, (_, i) => values[Math.min(i, values.length - 1)] ?? 0);
  return sampled.map((v) => Math.max(8, Math.round((v / max) * 100)));
}

export function LifestyleTrendsChart({ trends }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const joyVals = trendValues(trends.joy);
  const vitVals = trendValues(trends.vitality);
  const hasSeries = joyVals.length > 1 || vitVals.length > 1;
  const barSource = joyVals.length ? joyVals : vitVals;
  const barHeights = hasSeries ? seriesToBarHeights(barSource, 12) : null;
  const peakIndex =
    barHeights && barHeights.length
      ? barHeights.reduce((best, h, i, arr) => (h >= arr[best]! ? i : best), 0)
      : -1;

  if (!hasSeries) return null;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
      <div className="mb-4 flex items-center justify-between">
        <PersonalWidgetSectionHeader title={lifestylePulseCopy.trendsTitle} explainerId="PULSE-007" momentTypeCode={MOMENT_TYPE} />
        <div className="flex gap-2">
          <div className="flex items-center gap-1">
            <div className="size-1.5 rounded-full" style={{ background: colors.brandPrimary }} />
            <span className="text-[9px] font-bold uppercase opacity-60">{lifestylePulseCopy.trendsJoyLegend}</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="size-1.5 rounded-full" style={{ background: colors.tertiary }} />
            <span className="text-[9px] font-bold uppercase opacity-60">{lifestylePulseCopy.trendsVitalityLegend}</span>
          </div>
        </div>
      </div>
      <div className="relative flex h-40 items-end justify-between px-2">
        <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-40" viewBox="0 0 100 100" preserveAspectRatio="none">
          {joyVals.length > 1 ? <path d={seriesToPath(joyVals, 100, 100)} fill="none" stroke={colors.brandPrimary} strokeWidth="2" /> : null}
          {vitVals.length > 1 ? <path d={seriesToPath(vitVals, 100, 100)} fill="none" stroke={colors.tertiary} strokeWidth="2" /> : null}
        </svg>
        {barHeights?.map((h, i) => (
          <div
            key={i}
            className="relative w-2 rounded-t-sm"
            style={{
              height: `${h}%`,
              background: i === peakIndex ? colors.brandPrimary : `${colors.brandPrimary}1a`,
              boxShadow: i === peakIndex ? "0 0 15px rgba(108,78,242,0.4)" : undefined,
            }}
          >
            {i === peakIndex ? (
              <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-bold" style={{ color: colors.brandPrimary }}>
                Peak
              </div>
            ) : null}
          </div>
        ))}
      </div>
      <div className="mt-2 flex justify-between px-2 text-[9px] font-bold uppercase tracking-widest opacity-40">
        <span>{lifestylePulseCopy.trendsAxis30dAgo}</span>
        <span>{lifestylePulseCopy.trendsAxis15dAgo}</span>
        <span>{lifestylePulseCopy.trendsAxisNow}</span>
      </div>
    </section>
  );
}

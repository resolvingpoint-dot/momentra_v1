"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GuidedSetupTip } from "@/components/setup/GuidedSetupTip";
import { useGuidedSetupTheme } from "@/components/setup/GuidedSetupTheme";
import type { GuidedSetupSummaryRow } from "@/components/setup/guidedSetupTypes";

type Props = {
  rows: GuidedSetupSummaryRow[];
  contextHelp?: string | null;
  tip?: string | null;
  estimatedDuration?: number;
  currentStepTitle?: string;
  className?: string;
};

/** Local-only summary panel. Never calls preview. */
export function GuidedSetupLiveSummary({
  rows,
  contextHelp,
  tip,
  estimatedDuration,
  currentStepTitle,
  className,
}: Props) {
  const { colors } = useThemeTokens();
  const setupTheme = useGuidedSetupTheme();

  return (
    <aside
      className={className ?? "space-y-4 rounded-2xl border p-4"}
      style={{
        borderColor: `color-mix(in srgb, ${setupTheme.summaryAccent} 28%, ${colors.border})`,
        background: setupTheme.surface,
      }}
      aria-label="Live summary"
      data-guided-live-summary
    >
      <p
        className="text-[10px] font-bold uppercase tracking-widest opacity-60"
        style={{ color: setupTheme.summaryAccent }}
      >
        Summary
      </p>
      {currentStepTitle ? (
        <p className="text-xs opacity-70">
          Current step: <span className="font-semibold opacity-100">{currentStepTitle}</span>
        </p>
      ) : null}
      {rows.length === 0 ? (
        <p className="text-sm opacity-60">Answers appear here as you go.</p>
      ) : null}
      {rows.length > 0 ? (
        <dl className="space-y-2">
          {rows.map((row) => (
            <div key={row.label} className="flex justify-between gap-3 text-sm">
              <dt className="opacity-60">{row.label}</dt>
              <dd className="max-w-[60%] truncate text-right font-medium">{row.value || "—"}</dd>
            </div>
          ))}
        </dl>
      ) : null}
      {tip ? <GuidedSetupTip tip={tip} /> : null}
      {contextHelp && !tip ? (
        <p className="text-xs leading-relaxed opacity-75" style={{ color: colors.textSecondary }}>
          {contextHelp}
        </p>
      ) : null}
      {estimatedDuration ? (
        <p className="text-[10px] opacity-50">
          Estimated completion · About {estimatedDuration} minutes
        </p>
      ) : null}
    </aside>
  );
}

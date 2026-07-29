"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = {
  title: string;
  primary: string;
  detail?: string;
  estimateLabel?: string;
};

/**
 * @deprecated Do not use for the setup shell summary panel.
 * Prefer GuidedSetupLiveSummary via GuidedSetupShell.
 * Still acceptable for inline local estimates (e.g. runway months) inside step content.
 */
export function SetupLiveSummary({ title, primary, detail, estimateLabel = "Estimate" }: Props) {
  const { colors } = useThemeTokens();
  return (
    <aside
      className="rounded-2xl border p-4"
      style={{
        borderColor: `color-mix(in srgb, ${colors.primary} 35%, transparent)`,
        background: `color-mix(in srgb, ${colors.primary} 10%, transparent)`,
      }}
      aria-live="polite"
    >
      <p className="text-[10px] font-bold uppercase tracking-widest opacity-60">{estimateLabel}</p>
      <p className="mt-1 text-sm font-semibold">{title}</p>
      <p className="mt-1 text-2xl font-bold" style={{ color: colors.primary }}>
        {primary}
      </p>
      {detail ? (
        <p className="mt-2 text-xs leading-relaxed opacity-75" style={{ color: colors.textSecondary }}>
          {detail}
        </p>
      ) : null}
    </aside>
  );
}

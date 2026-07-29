"use client";

import type { ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

export type ReviewBlock = {
  title: string;
  rows: Array<{ label: string; value: string }>;
};

type Props = {
  blocks: ReviewBlock[];
  warnings?: string[];
  children?: ReactNode;
};

export function SetupReviewSummary({ blocks, warnings = [], children }: Props) {
  const { colors } = useThemeTokens();
  return (
    <div className="space-y-6">
      {blocks.map((block) => (
        <section
          key={block.title}
          className="space-y-3 rounded-2xl border p-4"
          style={{
            borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
            background: colors.surfaceContainer,
          }}
        >
          <h3 className="text-sm font-semibold">{block.title}</h3>
          <dl className="space-y-2">
            {block.rows.map((row) => (
              <div key={`${block.title}-${row.label}`} className="flex justify-between gap-3 text-sm">
                <dt className="opacity-60">{row.label}</dt>
                <dd className="text-right font-medium">{row.value || "—"}</dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
      {warnings.length > 0 ? (
        <section
          className="space-y-2 rounded-2xl border p-4"
          style={{
            borderColor: `color-mix(in srgb, ${colors.primary} 30%, transparent)`,
            background: `color-mix(in srgb, ${colors.primary} 8%, transparent)`,
          }}
        >
          <h3 className="text-sm font-semibold">Recommended</h3>
          <ul className="space-y-1 text-sm opacity-80">
            {warnings.map((w) => (
              <li key={w}>• {w}</li>
            ))}
          </ul>
        </section>
      ) : null}
      {children}
    </div>
  );
}

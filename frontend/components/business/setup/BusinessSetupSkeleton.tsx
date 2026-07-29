"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";

/** In-shell skeleton for Business setup first paint — not a full-screen blocker. */
export function BusinessSetupSkeleton({ rows = 4 }: { rows?: number }) {
  const { colors } = useThemeTokens();
  return (
    <div className="space-y-4" aria-busy="true" aria-label="Loading setup">
      <p className="text-sm font-medium opacity-80" role="status" aria-live="polite">
        Loading setup…
      </p>
      <div
        className="h-5 w-40 animate-pulse rounded"
        style={{ background: colors.surfaceContainer }}
      />
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="space-y-2">
          <div
            className="h-3 w-24 animate-pulse rounded"
            style={{ background: colors.surfaceContainer }}
          />
          <div
            className="h-11 w-full animate-pulse rounded-xl"
            style={{ background: colors.surfaceContainer }}
          />
        </div>
      ))}
    </div>
  );
}

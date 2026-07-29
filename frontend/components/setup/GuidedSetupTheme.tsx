"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { GuidedSetupContextType } from "@/components/setup/guidedSetupTypes";
import type { ContextColors } from "@/lib/contextTokens";

export type GuidedSetupThemeTokens = {
  accentColor: string;
  surface: string;
  selectedCard: string;
  selectedChip: string;
  summaryAccent: string;
  illustrationTint: string;
};

function resolveGuidedSetupTheme(
  contextType: GuidedSetupContextType,
  colors: ContextColors,
): GuidedSetupThemeTokens {
  const accent =
    colors.primary ?? colors.brandPrimary ?? colors.brandSecondary;
  const surface = colors.surfaceContainer ?? colors.surface;
  const tintBase =
    contextType === "personal"
      ? (colors.brandTertiary ?? accent)
      : contextType === "group"
        ? (colors.brandSecondary ?? accent)
        : accent;

  return {
    accentColor: accent,
    surface,
    selectedCard: `color-mix(in srgb, ${accent} 14%, transparent)`,
    selectedChip: `color-mix(in srgb, ${accent} 16%, transparent)`,
    summaryAccent: tintBase,
    illustrationTint: `color-mix(in srgb, ${tintBase} 22%, transparent)`,
  };
}

const GuidedSetupThemeContext = createContext<GuidedSetupThemeTokens | null>(
  null,
);

export function GuidedSetupThemeProvider({
  contextType = "business",
  children,
}: {
  contextType?: GuidedSetupContextType;
  children: ReactNode;
}) {
  const { colors } = useThemeTokens();
  const value = useMemo(
    () => resolveGuidedSetupTheme(contextType, colors),
    [contextType, colors],
  );
  return (
    <GuidedSetupThemeContext.Provider value={value}>
      {children}
    </GuidedSetupThemeContext.Provider>
  );
}

export function useGuidedSetupTheme(): GuidedSetupThemeTokens {
  const ctx = useContext(GuidedSetupThemeContext);
  const { colors } = useThemeTokens();
  return useMemo(
    () => ctx ?? resolveGuidedSetupTheme("business", colors),
    [ctx, colors],
  );
}

export { resolveGuidedSetupTheme };

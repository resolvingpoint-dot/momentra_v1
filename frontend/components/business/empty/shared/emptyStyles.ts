import type { CSSProperties } from "react";
import type { ContextThemeTokens } from "@/lib/contextTokens";

export function businessCardStyle(tokens: ContextThemeTokens): CSSProperties {
  return {
    background: tokens.colors.surfaceContainer,
    border: `1px solid color-mix(in srgb, ${tokens.colors.border} 15%, transparent)`,
  };
}

export function businessScrollShellStyle(
  tokens: ContextThemeTokens,
  bottomPadding: number,
): CSSProperties {
  return {
    background: tokens.colors.background,
    color: tokens.colors.textPrimary,
    paddingBottom: bottomPadding || tokens.spacing.md,
  };
}

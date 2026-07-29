import type { CSSProperties } from "react";
import type { ContextThemeTokens } from "@/lib/contextTokens";

export function groupGlassCardStyle(tokens: ContextThemeTokens): CSSProperties {
  return {
    background: `color-mix(in srgb, ${tokens.colors.surfaceContainer} 70%, transparent)`,
    border: "1px solid rgba(255, 255, 255, 0.08)",
    backdropFilter: "blur(16px)",
  };
}

export function groupMemoryGlassCardStyle(accentGlow: string): CSSProperties {
  return {
    background: "rgba(32, 31, 31, 0.72)",
    border: "1px solid rgba(255, 255, 255, 0.08)",
    backdropFilter: "blur(20px)",
    boxShadow: `0 10px 40px ${accentGlow}`,
    borderRadius: 24,
    padding: 20,
  };
}

export function groupScrollShellStyle(
  tokens: ContextThemeTokens,
  bottomPadding: number,
): CSSProperties {
  return {
    background: tokens.colors.background,
    color: tokens.colors.textPrimary,
    paddingBottom: bottomPadding || tokens.spacing.md,
  };
}

/** Vertical gap between major sections (`spacing.sectionGap` = 48). */
export function groupSectionGap(tokens: ContextThemeTokens): number {
  return tokens.spacing.sectionGap;
}

/** Standard inner card padding from group tokens (20–24px). */
export function groupCardPadding(tokens: ContextThemeTokens): number {
  return tokens.spacing.lg;
}

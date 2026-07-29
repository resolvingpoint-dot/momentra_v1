import type { CSSProperties } from "react";
import type { ContextThemeTokens } from "@/lib/contextTokens";

const FONT_FAMILY = "Plus Jakarta Sans, Helvetica Neue, Helvetica, Arial, sans-serif";

/** Typography scale from `design-tokens/group.tokens.json` (Plus Jakarta Sans). */
export const groupTypography = {
  display: {
    fontFamily: FONT_FAMILY,
    fontSize: 36,
    fontWeight: 700,
    lineHeight: 1.2,
  },
  headline: {
    fontFamily: FONT_FAMILY,
    fontSize: 32,
    fontWeight: 600,
    lineHeight: 1.25,
  },
  headlineMd: {
    fontFamily: FONT_FAMILY,
    fontSize: 24,
    fontWeight: 500,
    lineHeight: 1.3,
  },
  body: {
    fontFamily: FONT_FAMILY,
    fontSize: 18,
    fontWeight: 400,
    lineHeight: 1.5,
  },
  bodyMd: {
    fontFamily: FONT_FAMILY,
    fontSize: 16,
    fontWeight: 400,
    lineHeight: 1.5,
  },
  label: {
    fontFamily: FONT_FAMILY,
    fontSize: 12,
    fontWeight: 700,
    lineHeight: 1.4,
    letterSpacing: "0.05em",
  },
  labelSm: {
    fontFamily: FONT_FAMILY,
    fontSize: 12,
    fontWeight: 500,
    lineHeight: 1.4,
    letterSpacing: "0.04em",
  },
  brandTitle: {
    fontFamily: FONT_FAMILY,
    fontSize: 32,
    fontWeight: 700,
    lineHeight: 1.2,
  },
} as const satisfies Record<string, CSSProperties>;

export function groupSectionLabel(tokens: ContextThemeTokens): CSSProperties {
  return {
    ...groupTypography.label,
    color: tokens.colors.textSecondary,
    textTransform: "uppercase",
  };
}

export function groupCardTitle(tokens: ContextThemeTokens): CSSProperties {
  return {
    ...groupTypography.headlineMd,
    fontWeight: 600,
    color: tokens.colors.textPrimary,
  };
}

export function groupStatValue(tokens: ContextThemeTokens): CSSProperties {
  return {
    ...groupTypography.headlineMd,
    fontWeight: 600,
    color: tokens.colors.textPrimary,
  };
}

export function groupCaption(tokens: ContextThemeTokens): CSSProperties {
  return {
    ...groupTypography.labelSm,
    color: tokens.colors.textSecondary,
  };
}

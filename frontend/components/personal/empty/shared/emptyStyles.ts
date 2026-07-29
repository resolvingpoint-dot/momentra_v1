import type { CSSProperties } from "react";
import type { ContextThemeTokens } from "@/lib/contextTokens";

/** Personal glass card surface — matches design-tokens glass.cardBackground */
const GLASS_CARD_BG = "#1a1728";

export const PERSONAL_OUTWARD_GLOW = "0 0 40px -10px rgba(108, 78, 242, 0.3)";
export const PERSONAL_PREMIUM_OUTWARD_GLOW = "0 0 25px -5px rgba(201, 191, 255, 0.25)";
export const PERSONAL_GLASS_DEPTH_SHADOW = "0 4px 24px -1px rgba(0, 0, 0, 0.2)";

export function personalGlowWrapperStyle(
  _tokens: ContextThemeTokens,
  cornerRadius = 24,
): CSSProperties {
  return {
    borderRadius: cornerRadius,
    boxShadow: PERSONAL_OUTWARD_GLOW,
    padding: 2,
    margin: "6px 3px",
  };
}

export function premiumGlowWrapperStyle(cornerRadius = 16): CSSProperties {
  return {
    borderRadius: cornerRadius,
    boxShadow: PERSONAL_PREMIUM_OUTWARD_GLOW,
    padding: 2,
    margin: "6px 3px",
  };
}

export function premiumGlowCardStyle(tokens: ContextThemeTokens): CSSProperties {
  return {
    ...personalGlassCardStyle(tokens),
    boxShadow: PERSONAL_GLASS_DEPTH_SHADOW,
    border: "1px solid rgba(201, 191, 255, 0.2)",
  };
}

export function personalGlassCardStyle(
  tokens: ContextThemeTokens,
  options?: { glow?: boolean },
): CSSProperties {
  const style: CSSProperties = {
    background: GLASS_CARD_BG,
    border: "1px solid rgba(255, 255, 255, 0.08)",
    backdropFilter: "blur(12px)",
    WebkitBackdropFilter: "blur(12px)",
    boxShadow: PERSONAL_GLASS_DEPTH_SHADOW,
  };
  if (options?.glow) {
    style.boxShadow = `${PERSONAL_OUTWARD_GLOW}, ${PERSONAL_GLASS_DEPTH_SHADOW}`;
  }
  return style;
}

export function personalGlassInnerStyle(
  tokens: ContextThemeTokens,
  cornerRadius = 16,
  extra?: CSSProperties,
): CSSProperties {
  return {
    ...personalGlassCardStyle(tokens),
    borderRadius: Math.max(0, cornerRadius - 2),
    ...extra,
  };
}

/** @deprecated Use personalGlassCardStyle */
export function glassCardStyle(tokens: ContextThemeTokens): CSSProperties {
  return personalGlassCardStyle(tokens);
}

export function neuralLineBackground(): CSSProperties {
  return {
    backgroundImage:
      "radial-gradient(circle at 2px 2px, rgba(108, 78, 242, 0.05) 1px, transparent 0)",
    backgroundSize: "24px 24px",
  };
}

export const personalTypography = {
  heroTitle: {
    fontSize: 28,
    fontWeight: 700,
    lineHeight: "36px",
    letterSpacing: "-0.02em",
  } satisfies CSSProperties,
  screenTitle: {
    fontSize: 22,
    fontWeight: 700,
    lineHeight: "28px",
    letterSpacing: "-0.01em",
  } satisfies CSSProperties,
  sectionHeader: {
    fontSize: 17,
    fontWeight: 600,
    lineHeight: "22px",
  } satisfies CSSProperties,
  bodyMd: {
    fontSize: 14,
    fontWeight: 400,
    lineHeight: "20px",
  } satisfies CSSProperties,
  labelSm: {
    fontSize: 12,
    fontWeight: 500,
    lineHeight: "16px",
    letterSpacing: "0.01em",
  } satisfies CSSProperties,
  breadcrumb: {
    fontSize: 10,
    fontWeight: 500,
    lineHeight: "16px",
    letterSpacing: "0.1em",
    textTransform: "uppercase" as const,
  } satisfies CSSProperties,
  microLabel: {
    fontSize: 10,
    fontWeight: 700,
    lineHeight: "12px",
    letterSpacing: "0.1em",
    textTransform: "uppercase" as const,
  } satisfies CSSProperties,
};

/** Section index labels (e.g. "1 IDENTITY SNAPSHOT") — brand primary @ 70%. */
export function memoryMicroLabelStyle(
  tokens: ContextThemeTokens,
  accentColor?: string,
): CSSProperties {
  const accent = accentColor ?? tokens.colors.brandPrimary;
  return {
    ...personalTypography.microLabel,
    color: accent,
    opacity: 0.7,
  };
}

export function scrollShellStyle(
  tokens: ContextThemeTokens,
  bottomPadding: number,
): CSSProperties {
  return {
    background: tokens.colors.background,
    color: tokens.colors.textPrimary,
    paddingBottom: bottomPadding || tokens.spacing.md,
  };
}

export function personalPulseContainerStyle(tokens: ContextThemeTokens): CSSProperties {
  return {
    maxWidth: 1080,
    width: "100%",
    marginLeft: "auto",
    marginRight: "auto",
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacing.md,
    paddingLeft: tokens.spacing.screenHorizontal,
    paddingRight: tokens.spacing.screenHorizontal,
    paddingTop: tokens.spacing.lg,
    paddingBottom: tokens.spacing.lg,
  };
}

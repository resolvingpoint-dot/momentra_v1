import type { AppContext } from "./appContext";

export type BusinessOperationalDimensionKey =
  | "team"
  | "project"
  | "event"
  | "runway"
  | "department"
  | "vendor"
  | "custom";

export type BusinessOperationalDimension = {
  label: string;
  main: string;
  softTint: string;
  glow: string;
  icon: string;
};

export type ContextColors = {
  brandPrimary: string;
  brandOnPrimary: string;
  brandSecondary: string;
  brandOnSecondary: string;
  brandTertiary: string;
  brandOnTertiary: string;
  brandMuted: string;
  background: string;
  surface: string;
  surfaceElevated: string;
  surfaceHigh: string;
  surfaceContainer: string;
  /** Lower elevation surface between background and container. */
  surfaceContainerLow: string;
  /** Alias for surfaceContainer on the lowest elevation. */
  surfaceContainerLowest: string;
  /** Alias for surfaceElevated / high-elevation surface. */
  surfaceContainerHigh: string;
  /** Muted surface variant for subtle backgrounds. */
  surfaceVariant: string;
  primaryContainer: string;
  /** Alias for primaryContainer used by some components. */
  brandPrimaryContainer: string;
  onPrimaryContainer: string;
  /** Alias for brandOnPrimary used by some components. */
  onPrimary: string;
  /** Alias for brandPrimary — setup/legacy call sites. */
  primary?: string;
  /** Alias for brandSecondary — group life call sites. */
  secondary?: string;
  /** Optional secondary container gradient stop. */
  secondaryContainer?: string;
  textPrimary: string;
  textSecondary: string;
  textSubtle: string;
  /** Alias for brandTertiary used by some components. */
  tertiary: string;
  border: string;
  error: string;
  success: string;
  warning: string;
  info: string;
  glassBackground: string;
  accentEscape: string;
  accentVow: string;
  accentPulse: string;
  accentSummit: string;
};

export type ContextSpacing = {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
  screenHorizontal: number;
  inputPaddingX: number;
  inputPaddingY: number;
  scrollBottom: number;
  buttonHeight: number;
  appleButtonHeight: number;
  sectionGap: number;
  gutter: number;
  bottomNavHeight: number;
};

export type ContextRadius = {
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
  xxxl: number;
  input: number;
  button: number;
  card: number;
  pill: number;
};

export type ContextShadow = {
  cardRadius: number;
  cardOffsetY: number;
  cardColor: string;
  fabRadius: number;
  fabOffsetY: number;
  fabColor: string;
  glowRadius: number;
  glowColor: string;
};

export type ContextGradient = {
  heroStart: string;
  heroEnd: string;
  brandFadeStart: string;
  brandFadeEnd: string;
  purpleFadeStart: string;
  purpleFadeEnd: string;
};

export type ContextAppShell = {
  topBarHeight: number;
  contextSwitcherHeight: number;
};

export type ContextThemeTokens = {
  context: AppContext;
  colors: ContextColors;
  spacing: ContextSpacing;
  radius: ContextRadius;
  shadows: ContextShadow;
  gradients: ContextGradient;
  appShell: ContextAppShell;
};

export const businessOperationalDimensions: Record<
  BusinessOperationalDimensionKey,
  BusinessOperationalDimension
> = {
  team: {
    label: "Team Operations",
    main: "#5b5ceb",
    softTint: "#252654",
    glow: "rgba(91, 92, 235, 0.25)",
    icon: "groups",
  },
  project: {
    label: "Project Operations",
    main: "#00ced1",
    softTint: "#0a3234",
    glow: "rgba(0, 206, 209, 0.25)",
    icon: "project_ops",
  },
  event: {
    label: "Event Operations",
    main: "#f59e0b",
    softTint: "#3a2d14",
    glow: "rgba(245, 158, 11, 0.25)",
    icon: "event_ops",
  },
  runway: {
    label: "Business Runway",
    main: "#10b981",
    softTint: "#0f3329",
    glow: "rgba(16, 185, 129, 0.25)",
    icon: "business_runway",
  },
  department: {
    label: "Business Operations",
    main: "#f97316",
    softTint: "#3a2214",
    glow: "rgba(249, 115, 22, 0.25)",
    icon: "department_ops",
  },
  vendor: {
    label: "Vendor Operations",
    main: "#8b5cf6",
    softTint: "#2a2045",
    glow: "rgba(139, 92, 246, 0.25)",
    icon: "vendor_ops",
  },
  custom: {
    label: "Custom Operations",
    main: "#5b5ceb",
    softTint: "#252654",
    glow: "rgba(91, 92, 235, 0.25)",
    icon: "custom",
  },
};

const defaultAppShell: ContextAppShell = {
  topBarHeight: 56,
  contextSwitcherHeight: 44,
};

const personalTokens: ContextThemeTokens = {
  context: "personal",
  colors: {
    brandPrimary: "#c9bfff",
    brandOnPrimary: "#2f009c",
    brandSecondary: "#cabeff",
    brandOnSecondary: "#311c7e",
    brandTertiary: "#4cd6ff",
    brandOnTertiary: "#003543",
    brandMuted: "#c9c4d8",
    background: "#14121b",
    surface: "#14121b",
    surfaceElevated: "#3a3842",
    surfaceHigh: "#35333e",
    surfaceContainer: "#201e28",
    surfaceContainerLow: "#1c1a24",
    surfaceContainerLowest: "#14121b",
    surfaceContainerHigh: "#3a3842",
    surfaceVariant: "#35333e",
    primaryContainer: "#6c4ef2",
    brandPrimaryContainer: "#6c4ef2",
    onPrimaryContainer: "#f2ecff",
    onPrimary: "#2f009c",
    textPrimary: "#e5e0ee",
    textSecondary: "#c9c4d8",
    textSubtle: "#938ea1",
    tertiary: "#4cd6ff",
    border: "#938ea1",
    error: "#ffb4ab",
    success: "#c9bfff",
    warning: "#4cd6ff",
    info: "#cabeff",
    glassBackground: "rgba(255, 255, 255, 0.05)",
    accentEscape: "#c9bfff",
    accentVow: "#cabeff",
    accentPulse: "#4cd6ff",
    accentSummit: "#6c4ef2",
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    screenHorizontal: 20,
    inputPaddingX: 14,
    inputPaddingY: 12,
    scrollBottom: 40,
    buttonHeight: 56,
    appleButtonHeight: 50,
    sectionGap: 32,
    gutter: 16,
    bottomNavHeight: 80,
  },
  radius: {
    sm: 4,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 24,
    xxxl: 24,
    input: 12,
    button: 12,
    card: 16,
    pill: 9999,
  },
  shadows: {
    cardRadius: 0,
    cardOffsetY: 0,
    cardColor: "transparent",
    fabRadius: 12,
    fabOffsetY: 4,
    fabColor: "rgba(108, 78, 242, 0.35)",
    glowRadius: 40,
    glowColor: "rgba(108, 78, 242, 0.2)",
  },
  gradients: {
    heroStart: "#6c4ef2",
    heroEnd: "#c9bfff",
    brandFadeStart: "rgba(108, 78, 242, 0.12)",
    brandFadeEnd: "rgba(76, 214, 255, 0.08)",
    purpleFadeStart: "#201e28",
    purpleFadeEnd: "#14121b",
  },
  appShell: defaultAppShell,
};

const groupTokens: ContextThemeTokens = {
  context: "group",
  colors: {
    brandPrimary: "#FFB598",
    brandOnPrimary: "#591D00",
    brandSecondary: "#FFB690",
    brandOnSecondary: "#542100",
    brandTertiary: "#FFB951",
    brandOnTertiary: "#452B00",
    brandMuted: "#DFC0B4",
    background: "#131313",
    surface: "#131313",
    surfaceElevated: "#201F1F",
    surfaceHigh: "#2A2A2A",
    surfaceContainer: "#201F1F",
    surfaceContainerLow: "#1C1B1B",
    surfaceContainerLowest: "#131313",
    surfaceContainerHigh: "#2A2A2A",
    surfaceVariant: "#201F1F",
    primaryContainer: "#FF7A3D",
    brandPrimaryContainer: "#FF7A3D",
    onPrimaryContainer: "#ffffff",
    onPrimary: "#591D00",
    textPrimary: "#E5E2E1",
    textSecondary: "#DFC0B4",
    textSubtle: "#DFC0B4",
    tertiary: "#FFB951",
    border: "rgba(255, 255, 255, 0.1)",
    error: "#FFB4AB",
    success: "#4ADE80",
    warning: "#FFB951",
    info: "#FFB598",
    glassBackground: "rgba(255, 255, 255, 0.05)",
    accentEscape: "#FFB598",
    accentVow: "#FFB690",
    accentPulse: "#FF7A3D",
    accentSummit: "#FFB951",
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    screenHorizontal: 20,
    inputPaddingX: 14,
    inputPaddingY: 12,
    scrollBottom: 100,
    buttonHeight: 56,
    appleButtonHeight: 50,
    sectionGap: 48,
    gutter: 24,
    bottomNavHeight: 80,
  },
  radius: {
    sm: 8,
    md: 16,
    lg: 24,
    xl: 24,
    xxl: 24,
    xxxl: 32,
    input: 8,
    button: 16,
    card: 24,
    pill: 9999,
  },
  shadows: {
    cardRadius: 25,
    cardOffsetY: 20,
    cardColor: "rgba(0, 0, 0, 0.5)",
    fabRadius: 12,
    fabOffsetY: 4,
    fabColor: "rgba(255, 122, 61, 0.35)",
    glowRadius: 40,
    glowColor: "rgba(255, 122, 61, 0.2)",
  },
  gradients: {
    heroStart: "#FF7A3D",
    heroEnd: "#FFB598",
    brandFadeStart: "rgba(255, 122, 61, 0.12)",
    brandFadeEnd: "rgba(255, 185, 152, 0.08)",
    purpleFadeStart: "#201F1F",
    purpleFadeEnd: "#131313",
  },
  appShell: defaultAppShell,
};

const businessTokens: ContextThemeTokens = {
  context: "business",
  colors: {
    brandPrimary: "#5b5ceb",
    brandOnPrimary: "#ffffff",
    brandSecondary: "#a1a7c1",
    brandOnSecondary: "#0b1020",
    brandTertiary: "#10b981",
    brandOnTertiary: "#0b1020",
    brandMuted: "#a1a7c1",
    background: "#0b1020",
    surface: "#0b1020",
    surfaceElevated: "#1e243d",
    surfaceHigh: "#1a2036",
    surfaceContainer: "#161b2e",
    surfaceContainerLow: "#12172a",
    surfaceContainerLowest: "#0b1020",
    surfaceContainerHigh: "#1e243d",
    surfaceVariant: "#1a2036",
    primaryContainer: "#252654",
    brandPrimaryContainer: "#252654",
    onPrimaryContainer: "#c7c8ff",
    onPrimary: "#ffffff",
    textPrimary: "#ffffff",
    textSecondary: "#a1a7c1",
    textSubtle: "#a1a7c1",
    tertiary: "#10b981",
    border: "#2d3554",
    error: "#f87171",
    success: "#10b981",
    warning: "#f59e0b",
    info: "#a1a7c1",
    glassBackground: "rgba(22, 27, 46, 0.92)",
    accentEscape: "#5b5ceb",
    accentVow: "#00ced1",
    accentPulse: "#00ced1",
    accentSummit: "#0a3234",
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    screenHorizontal: 16,
    inputPaddingX: 16,
    inputPaddingY: 12,
    scrollBottom: 40,
    buttonHeight: 40,
    appleButtonHeight: 50,
    sectionGap: 24,
    gutter: 16,
    bottomNavHeight: 80,
  },
  radius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 12,
    xxl: 12,
    xxxl: 12,
    input: 8,
    button: 8,
    card: 12,
    pill: 9999,
  },
  shadows: {
    cardRadius: 12,
    cardOffsetY: 0,
    cardColor: "rgba(91, 92, 235, 0.12)",
    fabRadius: 8,
    fabOffsetY: 2,
    fabColor: "rgba(91, 92, 235, 0.2)",
    glowRadius: 16,
    glowColor: "rgba(91, 92, 235, 0.2)",
  },
  gradients: {
    heroStart: "#5b5ceb",
    heroEnd: "#252654",
    brandFadeStart: "rgba(91, 92, 235, 0.12)",
    brandFadeEnd: "rgba(16, 185, 129, 0.08)",
    purpleFadeStart: "#161b2e",
    purpleFadeEnd: "#0b1020",
  },
  appShell: defaultAppShell,
};

/** Circle Magenta — from docs/design-tokens/tokens.md (not Stitch rose mocks). */
const circleTokens: ContextThemeTokens = {
  context: "circle",
  colors: {
    brandPrimary: "#D946EF",
    brandOnPrimary: "#1A0828",
    brandSecondary: "#E879F9",
    brandOnSecondary: "#1A0828",
    brandTertiary: "#F5D0FE",
    brandOnTertiary: "#4A1060",
    brandMuted: "#7A3A90",
    background: "#100520",
    surface: "#100520",
    surfaceElevated: "#1E0E30",
    surfaceHigh: "#1E0E30",
    surfaceContainer: "#1A0828",
    surfaceContainerLow: "#140620",
    surfaceContainerLowest: "#100520",
    surfaceContainerHigh: "#1E0E30",
    surfaceVariant: "#4A1060",
    primaryContainer: "#4A1060",
    brandPrimaryContainer: "#4A1060",
    onPrimaryContainer: "#F5D0FE",
    onPrimary: "#1A0828",
    textPrimary: "#F5D0FE",
    textSecondary: "#E879F9",
    textSubtle: "#7A3A90",
    tertiary: "#F5D0FE",
    border: "rgba(217, 70, 239, 0.25)",
    error: "#FFB4AB",
    success: "#4ADE80",
    warning: "#E879F9",
    info: "#D946EF",
    glassBackground: "rgba(255, 255, 255, 0.05)",
    accentEscape: "#D946EF",
    accentVow: "#E879F9",
    accentPulse: "#D946EF",
    accentSummit: "#F5D0FE",
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    screenHorizontal: 20,
    inputPaddingX: 14,
    inputPaddingY: 12,
    scrollBottom: 100,
    buttonHeight: 56,
    appleButtonHeight: 50,
    sectionGap: 32,
    gutter: 16,
    bottomNavHeight: 80,
  },
  radius: {
    sm: 8,
    md: 16,
    lg: 24,
    xl: 24,
    xxl: 24,
    xxxl: 32,
    input: 8,
    button: 16,
    card: 24,
    pill: 9999,
  },
  shadows: {
    cardRadius: 25,
    cardOffsetY: 20,
    cardColor: "rgba(0, 0, 0, 0.5)",
    fabRadius: 12,
    fabOffsetY: 4,
    fabColor: "rgba(217, 70, 239, 0.35)",
    glowRadius: 40,
    glowColor: "rgba(217, 70, 239, 0.25)",
  },
  gradients: {
    heroStart: "#D946EF",
    heroEnd: "#E879F9",
    brandFadeStart: "rgba(217, 70, 239, 0.12)",
    brandFadeEnd: "rgba(232, 121, 249, 0.08)",
    purpleFadeStart: "#1A0828",
    purpleFadeEnd: "#100520",
  },
  appShell: defaultAppShell,
};

const tokensByContext: Record<AppContext, ContextThemeTokens> = {
  personal: personalTokens,
  group: groupTokens,
  business: businessTokens,
  circle: circleTokens,
};

export function tokensFor(context: AppContext): ContextThemeTokens {
  return tokensByContext[context];
}

export type GroupMomentTypeCode =
  | "SHARED_EXPERIENCE"
  | "SHARED_PURCHASE"
  | "SHARED_LIVING";

export type GroupMomentAccent = {
  accent: string;
  accentSecondary: string;
  onAccent: string;
  glow: string;
};

const groupMomentAccents: Record<GroupMomentTypeCode, GroupMomentAccent> = {
  SHARED_EXPERIENCE: {
    accent: "#14B8A6",
    accentSecondary: "#2DD4BF",
    onAccent: "#003734",
    glow: "rgba(20,184,166,0.15)",
  },
  SHARED_PURCHASE: {
    accent: "#FF7A3D",
    accentSecondary: "#FFB690",
    onAccent: "#652200",
    glow: "rgba(249,115,22,0.15)",
  },
  SHARED_LIVING: {
    accent: "#F59E0B",
    accentSecondary: "#F59E0B",
    onAccent: "#422006",
    glow: "rgba(245,158,11,0.15)",
  },
};

export function groupMomentAccent(momentTypeCode: string): GroupMomentAccent {
  const normalized = momentTypeCode.trim().toUpperCase();
  if (normalized in groupMomentAccents) {
    return groupMomentAccents[normalized as GroupMomentTypeCode];
  }
  return {
    accent: groupTokens.colors.accentPulse,
    accentSecondary: groupTokens.colors.brandSecondary,
    onAccent: groupTokens.colors.brandOnPrimary,
    glow: "rgba(255,122,61,0.15)",
  };
}

export function accentForTag(
  tag: string,
  tokens: ContextThemeTokens,
): string {
  const normalized = tag.trim().toUpperCase();
  switch (normalized) {
    case "THE VOW":
      return tokens.colors.accentVow;
    case "THE PULSE":
      return tokens.colors.accentPulse;
    case "THE SUMMIT":
      return tokens.colors.accentSummit;
    default:
      return tokens.colors.accentEscape;
  }
}

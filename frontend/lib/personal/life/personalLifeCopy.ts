import type { CSSProperties } from "react";
import type { ContextColors } from "@/lib/contextTokens";

export const personalLifeCopy = {
  screenTitle: "Life",
  screenSubtitle: "Money follows moments. We help you understand life.",
  scoreSuffix: "/100",
  lifeHealthLabel: "Life Health",
  deltaMonthLabel: (n: number) => `${n} this month`,
  emotionalTrendSparseTitle: "Not enough reflection data yet",
  emotionalTrendSparseBody:
    "Log reflections across your moments to see how Connection, Joy, Stress, and Fulfillment shift over time.",
  dominantEmotionSparseBody: "Your emotional mix will appear after you log a few reflections.",
  sparseCta: "Log Reflection",
  sections: {
    personalLifeHealth: "Personal Life Health",
    emotionalTrend: "Emotional Trend",
    dominantEmotion: "Dominant Emotional State",
    lifeBalance: "Life Balance Model",
    lifeConnections: "Life Connections",
    lifeConnectionsSubtitle: "How one area of life impacts another",
    driftAlert: "Life Drift Alert",
    leverage: "Highest Life Leverage",
    happiness: "What Actually Makes You Happy?",
    topDrivers: "Top Drivers",
    highestReturn: "Highest Emotional Return",
    lowestReturn: "Lowest Return Activities",
    intelligence: "Life Intelligence",
    monthlyChanges: "What Changed This Month",
    journey: "Life Journey",
  },
  series: {
    connection: "Connection",
    joy: "Joy",
    stress: "Stress",
    fulfillment: "Fulfillment",
  },
  loading: "Loading your life dashboard…",
};

export function satelliteColor(colorToken: string, colors: ContextColors): string {
  switch (colorToken) {
    case "node_blue":
      return colors.brandTertiary;
    case "node_green":
      return colors.success;
    case "node_orange":
      return colors.warning;
    case "node_pink":
      return colors.error;
    case "info":
      return colors.info;
    case "primary":
    default:
      return colors.brandPrimary;
  }
}

export function emotionColor(colorToken: string, colors: ContextColors): string {
  return satelliteColor(colorToken, colors);
}

export function sentimentColor(sentiment: string, colors: ContextColors): string {
  if (sentiment.includes("POSITIVE")) return colors.success;
  if (sentiment === "MODERATE") return colors.warning;
  return colors.textSecondary;
}

export function quickActionColor(colorToken: string, colors: ContextColors): string {
  switch (colorToken) {
    case "tertiary":
      return colors.brandTertiary;
    case "node_blue":
      return colors.brandTertiary;
    case "accent_yellow":
      return colors.warning;
    case "primary":
    default:
      return colors.brandPrimary;
  }
}

export function badgeStyle(
  badgeColorToken: string,
  colors: ContextColors,
): CSSProperties {
  const accent = satelliteColor(badgeColorToken, colors);
  return {
    border: `1px solid color-mix(in srgb, ${accent} 40%, transparent)`,
    color: accent,
    background: `color-mix(in srgb, ${accent} 12%, transparent)`,
  };
}

export function emotionalSeriesColors(colors: ContextColors) {
  return {
    connection: colors.brandPrimary,
    joy: colors.warning,
    stress: colors.error,
    fulfillment: colors.brandTertiary,
  } as const;
}

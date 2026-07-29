"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { usePersonalMomentSession } from "@/hooks/usePersonalMomentSession";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import type { ContextThemeTokens } from "@/lib/contextTokens";

export type DomainPalette = {
  background: string;
  surface: string;
  surfaceHigh: string;
  surfaceContainer: string;
  primaryAccent: string;
  secondaryAccent: string;
  textPrimary: string;
  textSecondary: string;
  glow: string;
};

const DOMAIN_OVERRIDES: Record<
  Exclude<PersonalMomentTypeCode, "LIFE_OPERATIONS">,
  Partial<ContextThemeTokens["colors"]>
> = {
  LIFESTYLE: {
    background: "#0a0a1a",
    surface: "#0a0a1a",
    surfaceContainer: "#14142b",
    surfaceHigh: "#1c1a3a",
    surfaceContainerHigh: "#1e1c3f",
    brandPrimary: "#8b5cf6",
    brandSecondary: "#ec4899",
    brandTertiary: "#10b981",
    primaryContainer: "#8b5cf6",
    textPrimary: "#ffffff",
    textSecondary: "#94a3b8",
  },
  FUTURE_BUILDING: {
    background: "#05071a",
    surface: "#05071a",
    surfaceContainer: "#0d112d",
    surfaceHigh: "#131a45",
    surfaceContainerHigh: "#161d4a",
    brandPrimary: "#3b82f6",
    brandSecondary: "#8b5cf6",
    brandTertiary: "#f59e0b",
    primaryContainer: "#3b82f6",
    textPrimary: "#e2e8f0",
    textSecondary: "#94a3b8",
  },
  RELATIONSHIPS: {
    background: "#0a0b1e",
    surface: "#0a0b1e",
    surfaceContainer: "#141630",
    surfaceHigh: "#1c1e42",
    surfaceContainerHigh: "#202245",
    brandPrimary: "#d63384",
    brandSecondary: "#6f42c1",
    brandTertiary: "#3b82f6",
    primaryContainer: "#d63384",
    textPrimary: "#ffffff",
    textSecondary: "#9ca3af",
  },
};

export function usePersonalDomainTokens(): ContextThemeTokens {
  const base = useThemeTokens();
  const typeCode = usePersonalMomentSession();
  if (typeCode === "LIFE_OPERATIONS") return base;

  const overrides = DOMAIN_OVERRIDES[typeCode];
  return {
    ...base,
    colors: {
      ...base.colors,
      ...overrides,
    },
  };
}

export function getDomainGradient(typeCode: PersonalMomentTypeCode): [string, string] {
  switch (typeCode) {
    case "LIFESTYLE":
      return ["#8b5cf6", "#ec4899"];
    case "FUTURE_BUILDING":
      return ["#3b82f6", "#8b5cf6"];
    case "RELATIONSHIPS":
      return ["#d63384", "#6f42c1"];
    default:
      return ["#6c4ef2", "#c9bfff"];
  }
}

export function useDomainGradient(): [string, string] {
  const typeCode = usePersonalMomentSession();
  return getDomainGradient(typeCode);
}

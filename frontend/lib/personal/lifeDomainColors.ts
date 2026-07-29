/** Global Momentra domain color tokens for Life OS surfaces. */

export const LIFE_DOMAIN_COLORS = {
  Money: "#6C4EF2",
  Lifestyle: "#F59E0B",
  Relationships: "#F43F5E",
  Future: "#10B981",
  Business: "#3B82F6",
  Circle: "#06B6D4",
  Memory: "#6366F1",
  default: "#8B7CFF",
} as const;

export type LifeDomainKey = keyof typeof LIFE_DOMAIN_COLORS;

export function lifeDomainColor(domain: string | null | undefined): string {
  const key = (domain ?? "").trim();
  if (key in LIFE_DOMAIN_COLORS) {
    return LIFE_DOMAIN_COLORS[key as LifeDomainKey];
  }
  const lower = key.toLowerCase();
  if (lower.includes("money")) return LIFE_DOMAIN_COLORS.Money;
  if (lower.includes("lifestyle")) return LIFE_DOMAIN_COLORS.Lifestyle;
  if (lower.includes("relationship")) return LIFE_DOMAIN_COLORS.Relationships;
  if (lower.includes("future") || lower.includes("momentum")) return LIFE_DOMAIN_COLORS.Future;
  if (lower.includes("business")) return LIFE_DOMAIN_COLORS.Business;
  if (lower.includes("circle")) return LIFE_DOMAIN_COLORS.Circle;
  if (lower.includes("memory")) return LIFE_DOMAIN_COLORS.Memory;
  return LIFE_DOMAIN_COLORS.default;
}

export function moodDotColor(label: string | null | undefined): string {
  const code = (label ?? "").toLowerCase();
  if (/(good|happy|proud|excit|energ)/.test(code)) return "#34D399";
  if (/(calm|okay|ok|peace)/.test(code)) return "#60A5FA";
  if (/(focus|productiv|flow)/.test(code)) return "#A78BFA";
  if (/(tired|stress|sad|low|anx)/.test(code)) return "#94A3B8";
  return "#94A3B8";
}
